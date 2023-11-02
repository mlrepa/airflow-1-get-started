import json
import os
from pathlib import Path
from typing import Dict, Text

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
import git
import gitlab
from gitlab.v4.objects.projects import Project as GitlabProject
import mlflow
import pendulum

from config import START_DATE_TIME, MLFLOW_TRACKING_URI, MLFLOW_DEFAULT_MODEL_NAME
from dags.utils.tasks import create_tmp_dir, clone, clean
from dags.config import CLONED_PROJECT_PATH, AIRFLOW_DAGS_PARAMS


dag = DAG(
    dag_id="train",
    start_date=pendulum.parse(START_DATE_TIME),
    max_active_runs=1,
    schedule_interval="@weekly",
    catchup=False
)


with dag:

    PROJECT_DIR = os.environ["PROJECT_DIR"]
    # TS = "{{ ts }}"  # The DAG run’s logical date
    # EXP_NAME = "{{ ds }}"

    train = BashOperator(
        task_id="train",
        bash_command=f"""

            cd {CLONED_PROJECT_PATH} && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \
            dvc exp run
        """
    )

    @task
    def commit_and_push(local_repo_path: Text, **kwargs) -> Text:

        import subprocess as sp

        ts: pendulum.DateTime = pendulum.parse(kwargs["ts"])

        print("Build branch name and commit message")
        exp_date, exp_time = ts.to_date_string(), ts.to_time_string()
        branch_name: Text = f"exp-{exp_date}-{exp_time}".replace(":", "-")
        commit_msg: Text = f"Run {branch_name}"

        print("Commit and push new experiment")
        repo: git.Repo = git.Repo(local_repo_path)
        repo.git.checkout("-b", branch_name)
        repo.git.add(".")
        repo.git.commit("-m", commit_msg)
        repo.git.push("origin", branch_name)

        print("Push DVC pipeline artifacts to a remote")
        dvc_push_proc = sp.Popen(
            f"cd {local_repo_path} && dvc push",
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        )
        out, err = dvc_push_proc.communicate()
        print(f"DVC push command output: {out}")
        print(f"DVC push command errors: {err}")

        return branch_name

    @task
    def add_metadata_to_mlflow_run(local_repo_path: Text):

        print("Collect metadata")
        repo_url: Text = AIRFLOW_DAGS_PARAMS.get("repo_url")
        repo: git.Repo = git.Repo(local_repo_path)
        commit_sha: Text = repo.head.commit.hexsha
        commit_url: Text = f"{repo_url.replace('.git', '')}/-/commit/{commit_sha}"
        print(f"commit_sha = {commit_sha}")
        print(f"commit_url = {commit_sha}")

        print("Read MLflow report")
        mlflow_report_path: Path = Path(local_repo_path) / "reports/mlflow_report.json"

        with open(mlflow_report_path) as mlflow_report_f:
            mlflow_report: Dict = json.load(mlflow_report_f)

        mlflow_run_id: Text = mlflow_report["run_id"]
        print(f"MLflow run ID = {mlflow_run_id}")

        print("Add metadata to run - set MLflow run tags")
        mlflow_client = mlflow.MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
        # Custom tag
        mlflow_client.set_tag(mlflow_run_id, "commit_sha", commit_sha)
        # Built-in tag - Description of the run. Source: https://mlflow.org/docs/latest/tracking.html#system-tags
        mlflow_client.set_tag(mlflow_run_id, "mlflow.note.content", commit_url)

    @task
    def create_merge_request(source_branch_name: Text, local_repo_path: Text, **kwargs):

        print("Get GitLab project")
        project_url: Text = AIRFLOW_DAGS_PARAMS["repo_url"]
        gitlab_pat: Text = AIRFLOW_DAGS_PARAMS["repo_password"]

        gl: gitlab.Gitlab = gitlab.Gitlab(private_token=gitlab_pat)
        full_project_name: Text = project_url.replace("https://gitlab.com/", "").replace(".git", "")
        project: GitlabProject = gl.projects.get(full_project_name)
        
        print("Read MLflow report")
        mlflow_report_path: Path = Path(local_repo_path) / "reports/mlflow_report.json"

        with open(mlflow_report_path) as mlflow_report_f:
            mlflow_report: Dict = json.load(mlflow_report_f)
        
        mlflow_exp_id: Text = mlflow_report["experiment_id"]
        mlflow_run_id: Text = mlflow_report["run_id"]
        print(f"MLflow experiment ID = {mlflow_exp_id}")
        print(f"MLflow run ID = {mlflow_run_id}")

        mlflow_run_url: Text = f"http://localhost:5000/#/experiments/{mlflow_exp_id}/runs/{mlflow_run_id}"
        print(f"MLflow run URL = {mlflow_run_url}")

        mlflow_client = mlflow.MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
        found_models = mlflow_client.search_model_versions(
            filter_string=f"name='{MLFLOW_DEFAULT_MODEL_NAME}' run_id='{mlflow_run_id}'"
        )

        mlflow_run_model_url: Text = ""

        if found_models:
            model = found_models[0]
            mlflow_run_model_url = f"http://localhost:5000/#/models/{MLFLOW_DEFAULT_MODEL_NAME}/versions/{model.version}"

        print(f"MLflow run model URL = {mlflow_run_model_url}")
        
        mr_description: Text = (    
            f"MLflow run URL: {mlflow_run_url}\n\n"
            f"MLflow run model URL: {mlflow_run_model_url}"
        )

        print("Create merge request")
        mr = project.mergerequests.create({
            "source_branch": source_branch_name,
            "target_branch": "main",
            "title": f"Run experiment on {kwargs['ts']}",
            "description": mr_description
        })
        changes = mr.changes()

        print(f"MR changes:\n {changes}")

    create_tmp_dir = create_tmp_dir(CLONED_PROJECT_PATH)
    clone = clone(CLONED_PROJECT_PATH, "main")
    clean = clean(CLONED_PROJECT_PATH)
    source_branch_name = commit_and_push(CLONED_PROJECT_PATH)
    create_merge_request = create_merge_request(source_branch_name, CLONED_PROJECT_PATH)
    add_metadata_to_mlflow_run = add_metadata_to_mlflow_run(CLONED_PROJECT_PATH)

    create_tmp_dir >> clone >> train >> source_branch_name >> create_merge_request >> add_metadata_to_mlflow_run >> clean
