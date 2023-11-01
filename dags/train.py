import os
from typing import Text

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
import git
import gitlab
from gitlab.v4.objects.projects import Project as GitlabProject
import pendulum

from config import START_DATE_TIME
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

    # TODO: add task: add commit sha/link to MLflow

    @task
    def create_merge_request(source_branch_name, **kwargs):

        project_url: Text = AIRFLOW_DAGS_PARAMS["repo_url"]
        gitlab_pat: Text = AIRFLOW_DAGS_PARAMS["repo_password"]

        gl: gitlab.Gitlab = gitlab.Gitlab(private_token=gitlab_pat)
        full_project_name: Text = project_url.replace("https://gitlab.com/", "").replace(".git", "")
        project: GitlabProject = gl.projects.get(full_project_name)
        
        # TODO: add links (run and model) as description of MR
        mr = project.mergerequests.create({
            "source_branch": source_branch_name,
            "target_branch": "main",
            "title": f"Run experiment on {kwargs['ts']}"
        })
        changes = mr.changes()

        print(f"MR changes:\n {changes}")

    create_tmp_dir = create_tmp_dir(CLONED_PROJECT_PATH)
    clone = clone(CLONED_PROJECT_PATH, "main")
    clean = clean(CLONED_PROJECT_PATH)
    source_branch_name = commit_and_push(CLONED_PROJECT_PATH)
    create_merge_request = create_merge_request(source_branch_name)

    create_tmp_dir >> clone >> train >> source_branch_name >> create_merge_request >> clean
