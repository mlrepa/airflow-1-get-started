import argparse
import logging
from pathlib import Path
from typing import Dict, List, Text

import pandas as pd
import pendulum
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, RegressionQualityMetric
from evidently.report import Report

from src.monitoring.model_performance import commit_model_metrics_to_db
from src.pipelines.monitor_data import prepare_current_data
from src.utils.utils import get_batch_interval
from config import PREDICTIONS_DIR, REFERENCE_DIR, COLUMN_MAPPING


def generate_reports(
    current_data: pd.DataFrame,
    reference_data: pd.DataFrame,
    column_mapping: ColumnMapping,
    timestamp: float
) -> None:
    """
    Generate data quality and data drift reports
    and commit metrics to the database.

    Args:
        current_data (pd.DataFrame):
            The current DataFrame with features and predictions.
        reference_data (pd.DataFrame):
            The reference DataFrame with features and predictions.
        column_mapping: ColumnMapping
            ColumnMapping object to map your column names and feature types
        timestamp (float):
            Metric pipeline execution timestamp.
    """

    logging.info("Create a model performance report")
    model_performance_report = Report(metrics=[RegressionQualityMetric()])
    model_performance_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )

    logging.info("Target drift report")
    target_drift_report = Report(metrics=[ColumnDriftMetric(column_mapping.target)])
    target_drift_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )

    logging.info('Save metrics to database')
    model_performance_report_content: Dict = model_performance_report.as_dict()
    target_drift_report_content: Dict = target_drift_report.as_dict()
    commit_model_metrics_to_db(
        model_performance_report=model_performance_report_content,
        target_drift_report=target_drift_report_content,
        timestamp=timestamp
    )


def monitor_model(
    ts: pendulum.DateTime,
    interval: int = 60
) -> None:
    """Build and save monitoring reports.

    Args:
        ts (pendulum.DateTime, optional): Timestamp.
        interval (int, optional): Interval. Defaults to 60.
    """

    # Prepare current data
    start_time, end_time = get_batch_interval(ts, interval)
    current_data = prepare_current_data(start_time, end_time)
    
    # Get predictions for the current data
    filename = pendulum.parse(end_time).to_date_string()
    path = Path(f'{PREDICTIONS_DIR}/{filename}.parquet')
    predictions = pd.read_parquet(path)

    # Merge current data with predictions
    current_data = current_data.merge(predictions, on='uuid', how='left')
    current_data = current_data.fillna(current_data.median(numeric_only=True)).fillna(-1)
    
    if current_data.shape[0] == 0:
        # Skip monitoring if current data is empty
        # Usually it may happen for few first batches
        print("Current data is empty!")
        print("Skip model monitoring")

    else:

        # Prepare reference data
        ref_path = f'{REFERENCE_DIR}/reference_data_2021-01.parquet'
        ref_data = pd.read_parquet(ref_path)
        columns: List[Text] = COLUMN_MAPPING.numerical_features \
                            + COLUMN_MAPPING.categorical_features \
                            + [ COLUMN_MAPPING.target, COLUMN_MAPPING.prediction ]
        reference_data = ref_data.loc[:, columns]

        # Generate reports
        generate_reports(
            current_data=current_data,
            reference_data=reference_data,
            column_mapping=COLUMN_MAPPING,
            timestamp=ts.timestamp()
        )


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
    monitor_model(ts=ts, interval=args.interval)
