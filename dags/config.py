from pathlib import Path
from typing import Text
from evidently import ColumnMapping

# Database 
DATABASE_URI = "postgresql://admin:admin@localhost:5432/monitoring" # rename to MONITORING_DB_URI
AIRFLOW_DB_URI = "postgresql+psycopg2://admin:admin@airflow-db:5432/airflow"

# Dataset 
DATA_SOURCE_URL = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
DATA_FILES = [
        "green_tripdata_2021-01.parquet",
        "green_tripdata_2021-02.parquet"
    ]

# Directories 
PROJECT_DIR = Path(".").absolute()
DATA_RAW_DIR = 'data/raw'
FEATURES_DIR = 'data/features'
REFERENCE_DIR = 'data/reference'
PREDICTIONS_DIR = 'data/predictions'
TARGET_DRIFT_REPORTS_DIR = 'reports/target_drift'
DATA_DRIFT_REPORTS_DIR = 'reports/data_drift'

# Pipelines
START_DATE_TIME = '2021-02-01 01:00:00'
END_DATE_TIME = '2021-02-28 23:00:00'
BATCH_INTERVAL = 60

# Map your column names and feature types
COLUMN_MAPPING = ColumnMapping()
COLUMN_MAPPING.target = 'duration_min'
COLUMN_MAPPING.prediction = 'predictions'
COLUMN_MAPPING.numerical_features = [
    'passenger_count', 'trip_distance','fare_amount', 'total_amount']
COLUMN_MAPPING.categorical_features = [
    'PULocationID', 'DOLocationID']