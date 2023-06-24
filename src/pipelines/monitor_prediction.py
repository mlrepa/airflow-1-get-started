import argparse
import logging
import os
from pathlib import Path
from typing import Dict

import pandas as pd
import pendulum
from evidently.metrics import ColumnDriftMetric
from evidently.report import Report
from evidently import ColumnMapping

from src.monitoring.prediction_drift import commit_prediction_drift_metrics_to_db, parse_prediction_drift_report
from src.utils.utils import get_batch_interval
from config import MONITORING_DB_URI, REFERENCE_DIR, PREDICTION_DRIFT_REPORTS_DIR, PREDICTIONS_DIR


def monitor_prediction(
    ts: pendulum.DateTime,
    interval: int = 60, 
) -> None:
    """Build and save data validation reports.

    Args:
        ts (pendulum.DateTime): Timestamp.
        interval (int, optional): Interval. Defaults to 60.
    """
    
    # Prepare current data
    start_time, end_time = get_batch_interval(ts, interval)
    print(start_time, end_time)

    # Get current data (predictions)
    filename = pendulum.parse(end_time).to_date_string()
    path = Path(f'{PREDICTIONS_DIR}/{filename}.parquet')
    current_data = pd.read_parquet(path)

    # Prepare reference data
    ref_path = f'{REFERENCE_DIR}/reference_data_2021-01.parquet'
    ref_data = pd.read_parquet(ref_path)
    reference_data = ref_data.loc[:, current_data.columns]

    # Define Column Mapping object for Prediction Drift 
    COLUMN_MAPPING = ColumnMapping()
    COLUMN_MAPPING.prediction = 'predictions'


    if current_data.shape[0] == 0:
        
        # Skip monitoring if current data is empty
        # Usually it may happen for few first batches
        print("Current data is empty!")
        print("Skip model monitoring")

    else:
        
        # Generate and save reports
        logging.info("Prediction drift report")
        prediction_drift_report = Report(metrics=[ColumnDriftMetric(COLUMN_MAPPING.prediction)])
        prediction_drift_report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=COLUMN_MAPPING
        )
        
        drift_report_metrics: Dict = parse_prediction_drift_report(prediction_drift_report)
        print(drift_report_metrics)
           
        logging.info('Save metrics to database')
        commit_prediction_drift_metrics_to_db(
            drift_report_metrics=drift_report_metrics,
            timestamp=ts.timestamp(),
            db_uri=MONITORING_DB_URI
        )
        
        logging.info('Save HTML report if Prediction Drift detected')
        path = os.path.join(PREDICTION_DRIFT_REPORTS_DIR, f"{ts.to_datetime_string()}.html")
        if drift_report_metrics['drift_detected'] is True: 
            prediction_drift_report.save_html(path)
            



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
    monitor_prediction(ts=ts, interval=args.interval)
