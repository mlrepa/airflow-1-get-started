import os

from airflow.models import Variable

from dags.utils.utils import extract_repo_name

# Airflow parameters

AIRFLOW_DAGS_PARAMS = {
    "ts": "{{ ts_nodash }}",  # execution date in "20180101T000000" format
    "airflow_run_dir": os.getenv("AIRFLOW_RUN_DIR"),
    "repo_name": extract_repo_name(Variable.get("REPO_URL")),
    "repo_url": Variable.get("REPO_URL"),
    "repo_username": Variable.get("REPO_USERNAME"),
    "repo_password": Variable.get("REPO_PASSWORD"),
    "branch": Variable.get("REPO_BRANCH")
}

CLONED_PROJECT_PATH = f"{AIRFLOW_DAGS_PARAMS.get('airflow_run_dir')}/mlops-3-nyt-taxi"
