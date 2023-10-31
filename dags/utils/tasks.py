from airflow.decorators import task
from airflow.operators.bash import BashOperator
import git
import os
from pathlib import Path
import shutil
from typing import Text

from dags.config import AIRFLOW_DAGS_PARAMS, CLONED_PROJECT_PATH
from utils.utils import repo_url_with_credentials, create_dag_run_dir


def clone_repo_task(repo_url: Text,
                    branch: Text,
                    repo_local_path: Text,
                    repo_username: Text,
                    repo_password: Text,
                    ) -> None:
    """Clone Git repo

    Args:
        repo_url: Remote Git repo URL
        branch: Target branch  to source code
        repo_local_path: Local directory for DAG running
        repo_username: Username
        repo_password: Password (personal access token

    Returns: None

    """
    print(f'Cloning {repo_url}')
    print(f'Repo clone to {repo_local_path}')
    repo_url_with_creds = repo_url_with_credentials(repo_url, repo_username, repo_password)
    repo_local_path = Path(repo_local_path)

    if repo_local_path.exists():
        try:
            shutil.rmtree(repo_local_path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    git.Repo.clone_from(repo_url_with_creds, repo_local_path)
    repo = git.Repo(repo_local_path)
    repo.git.checkout(branch)
    repo.git.pull('origin', branch)

    print(f'Repository cloned to: {repo_local_path}')


@task
def create_tmp_dir(dag_run_dir: Text):
    """Creates temporary folder (of local repository) in $AIRFLOW_RUN_DIR, from which
    scoring script will be run.
    Args:
        dag_run_dir: local repository path; dag_run_dir = $AIRFLOW_RUN_DIR/<timestamp>/<repo_name>
    """
    create_dag_run_dir(dag_run_dir)


@task
def clone(dag_run_dir: Text, branch: Text | None = None):
    """Clones repository in dag_run_dir, switches on specified branch.
    Args:
        dag_run_dir: Local repository path; dag_run_dir = $AIRFLOW_RUN_DIR/<timestamp>/<repo_name>.
        branch (Text | None): Branch name. Defaults to None.
    """

    branch_name: Text = branch if branch is not None else AIRFLOW_DAGS_PARAMS.get("branch")

    clone_repo_task(
        repo_url=AIRFLOW_DAGS_PARAMS.get("repo_url"),
        branch=branch_name,
        repo_local_path=dag_run_dir,
        repo_username=AIRFLOW_DAGS_PARAMS.get("repo_username"),
        repo_password=AIRFLOW_DAGS_PARAMS.get("repo_password")
    )

    
load_model = BashOperator(
    task_id="load_model",
    bash_command=f"cp $PROJECT_DIR/models/model.joblib {CLONED_PROJECT_PATH}/models"
)


load_data = BashOperator(
    task_id="load_data",
    bash_command=f"cp -r $PROJECT_DIR/data/features/* {CLONED_PROJECT_PATH}/data/features"
)


download_predictions = BashOperator(
    task_id="download_predictions",
    bash_command=f"""
        export SRC_PRED_DIR={CLONED_PROJECT_PATH}/data/predictions/{{{{ ds }}}} && \
        export DST_PRED_DIR=$PROJECT_DIR/data/predictions/{{{{ ds }}}} && \
        export TS_TIME={{{{macros.datetime.strftime(macros.datetime.fromisoformat(ts), "%H:%M:%S")}}}} && \
        mkdir -p $DST_PRED_DIR && \
        cp $SRC_PRED_DIR/$TS_TIME.parquet $DST_PRED_DIR
    """
)


@task(trigger_rule='all_success')
def clean(dag_run_dir):
    """
    Removes the repository temporary folder.
    Args:
        dag_run_dir: local repository path; dag_run_dir = $AIRFLOW_RUN_DIR/<timestamp>/<repo_name>
    """

    shutil.rmtree(Path(dag_run_dir).parent)
