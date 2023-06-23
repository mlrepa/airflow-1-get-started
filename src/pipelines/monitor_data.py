import argparse
import logging
import os
from pathlib import Path
from typing import Dict, List, Text

import pandas as pd
import pendulum
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import DatasetSummaryMetric
from evidently.report import Report

from src.monitoring.data_quality import commit_data_metrics_to_db
from src.monitoring.utils import detect_data_drift
from src.utils.utils import extract_batch_data, get_batch_interval
from config import FEATURES_DIR, MONITORING_DB_URI, REFERENCE_DIR, COLUMN_MAPPING, DATA_DRIFT_REPORTS_DIR 


def prepare_current_data(start_time: Text, end_time: Text) -> pd.DataFrame:
    """Merge the current data with the corresponding predictions.

    Args:
        start_time (Text): Start time.
        end_time (Text): End time.

    Returns:
        pd.DataFrame:
            A DataFrame containing the current data merged with predictions.
    """

    # Get current data (features)
    data_path = f'{FEATURES_DIR}/green_tripdata_2021-02.parquet'
    data = pd.read_parquet(data_path)
    current_data = extract_batch_data(
        data,
        start_time=start_time,
        end_time=end_time
    )

    # Fill missing values
    current_data = current_data.fillna(current_data.median(numeric_only=True)).fillna(-1)

    return current_data


# def generate_reports(
#     current_data: pd.DataFrame,
#     reference_data: pd.DataFrame,
#     column_mapping: ColumnMapping,
#     timestamp: float
# ) -> None:
#     """
#     Generate data quality and data drift reports and
#     commit metrics to the database.

#     Args:
#         current_data (pd.DataFrame):
#             The current DataFrame with features and predictions.
#         reference_data (pd.DataFrame):
#             The reference DataFrame with features and predictions.
#         column_mapping: ColumnMapping
#             ColumnMapping object to map your column names and feature types
#         timestamp (float):
#             Metric pipeline execution timestamp.
#     """




def monitor_data(
    ts: pendulum.DateTime,
    interval: int = 60, 
) -> None:
    """Build and save data validation reports.

    Args:
        ts (pendulum.DateTime): Timestamp.
        interval (int, optional): Interval. Defaults to 60.
    """

    # Define columns
    columns: List[Text] = COLUMN_MAPPING.numerical_features \
                        + COLUMN_MAPPING.categorical_features

    # Prepare current data
    start_time, end_time = get_batch_interval(ts, interval)
    current_data: pd.DataFrame = prepare_current_data(start_time, end_time)
    current_data = current_data.loc[:, columns]

    # Prepare reference data
    ref_path = f'{REFERENCE_DIR}/reference_data_2021-01.parquet'
    ref_data = pd.read_parquet(ref_path)
    reference_data = ref_data.loc[:, columns]

    if current_data.shape[0] == 0:
        
        # Skip monitoring if current data is empty
        # Usually it may happen for few first batches
        print("Current data is empty!")
        print("Skip model monitoring")

    else:
        
        # Generate and save reports
        logging.info("Data quality report")
        data_quality_report = Report(metrics=[DatasetSummaryMetric()])
        data_quality_report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=COLUMN_MAPPING
        )

        logging.info('Data drift report')
        data_drift_report = Report(metrics=[DataDriftPreset()])
        data_drift_report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=COLUMN_MAPPING
        )

        logging.info('Commit metrics into database')
        data_quality_report_content: Dict = data_quality_report.as_dict()
        data_drift_report_content: Dict = data_drift_report.as_dict()
        commit_data_metrics_to_db(
            data_quality_report=data_quality_report_content,
            data_drift_report=data_drift_report_content,
            timestamp=ts.timestamp(),
            db_uri=MONITORING_DB_URI
        )
        
        logging.info('Save HTML report if Data Drift detected')
        dataset_drift = detect_data_drift(data_drift_report)
        path = os.path.join(DATA_DRIFT_REPORTS_DIR, 'data_drift' f"{ts.to_datetime_string()}.html")
        if dataset_drift: 
            data_drift_report.save_html(path)
            



if __name__ == "__main__":

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--ts",
        dest="ts",
        required=True
    )
    args_parser.add_argument(
        "--interval",
        dest="interval",
        required=False,
        type=int,
        default=60
    )
    args = args_parser.parse_args()

    ts = pendulum.parse(args.ts)
    monitor_data(ts=ts, interval=args.interval)
