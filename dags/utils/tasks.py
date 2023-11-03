from airflow.decorators import task
from airflow.operators.bash import BashOperator
import os
from pathlib import Path
import shutil
from typing import Text

from dags.config import  AIRFLOW_DAGS_PARAMS, CLONED_PROJECT_PATH
from utils.utils import create_dag_run_dir, clone_git_repo


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

    clone_git_repo(
        repo_url=AIRFLOW_DAGS_PARAMS.get("repo_url"),
        branch=branch_name,
        repo_local_path=dag_run_dir,
        repo_username=AIRFLOW_DAGS_PARAMS.get("repo_username"),
        repo_password=AIRFLOW_DAGS_PARAMS.get("repo_password")
    )


@task(trigger_rule='all_success')
def clean(dag_run_dir):
    """
    Removes the repository temporary folder.
    Args:
        dag_run_dir: local repository path; dag_run_dir = $AIRFLOW_RUN_DIR/<timestamp>/<repo_name>
    """
    shutil.rmtree(Path(dag_run_dir).parent)
