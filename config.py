import os
from pathlib import Path
from typing import Text

from airflow.models import Variable
from evidently import ColumnMapping


from utils.utils import extract_repo_name

# Database
_monitoring_db_host: Text = os.getenv("MONITORING_DB_HOST", "monitoring-db")
_port = 5432
if _monitoring_db_host == "localhost":
    _port = 5433
MONITORING_DB_URI = (
    f"postgresql+psycopg2://admin:admin@{_monitoring_db_host}:{_port}/monitoring_db"
)

airflow_db_host: Text = os.getenv("AIRFLOW_DB_host", "localhost")
AIRFLOW_DB_URI = f"postgresql+psycopg2://admin:admin@{airflow_db_host}:5432/airflow"

# Dataset
DATA_SOURCE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DATA_FILES = ["green_tripdata_2021-01.parquet", "green_tripdata_2021-02.parquet"]

# Directories
PROJECT_DIR = Path(".").absolute()
DATA_RAW_DIR = "data/raw"
FEATURES_DIR = "data/features"
REFERENCE_DIR = "data/reference"
PREDICTIONS_DIR = "data/predictions"
TARGET_DRIFT_REPORTS_DIR = "reports/target_drift"
DATA_DRIFT_REPORTS_DIR = "reports/data_drift"
PREDICTION_DRIFT_REPORTS_DIR = "reports/prediction_drift"

# Models
MODELS_DIR = "models"

# Pipelines
START_DATE_TIME = "2021-02-01 01:00:00"
END_DATE_TIME = "2021-02-28 23:00:00"
BATCH_INTERVAL = 60

# Map your column names and feature types
COLUMN_MAPPING = ColumnMapping()
COLUMN_MAPPING.target = "duration_min"
COLUMN_MAPPING.prediction = "predictions"
COLUMN_MAPPING.numerical_features = [
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "total_amount",
]
COLUMN_MAPPING.categorical_features = ["PULocationID", "DOLocationID"]


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

# MLflow parameters

# MLFLOW_TRACKING_URI = "http://localhost:5000"
MLFLOW_TRACKING_URI = "http://mlflow-server:5000"
MLFLOW_EXPERIMENT_NAME = "mlops-3-nyt-taxi"
MLFLOW_DEFAULT_MODEL_NAME = "Model"