import argparse
import logging
from pathlib import Path
import pickle 
from typing import Text

import mlflow
import pandas as pd
import pendulum

from config import FEATURES_DIR, PREDICTIONS_DIR, MLFLOW_DEFAULT_MODEL_NAME
from src.utils.utils import (
    load_data,
    get_batch_interval,
    get_predictions,
    save_predictions
)

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("PREDICT")


def predict(model_path: Text, ts: pendulum.DateTime, interval: int = 60) -> None:
    """Calculate predictions for the new batch (interval) data.

    Args:
        model_path (Text): MLflow model URI.
        ts (pendulum.DateTime, optional): Timestamp. Defaults to None.
        interval (int, optional): Interval. Defaults to 60.
    """

    LOGGER.info("Start the pipeline")

    # Compute the batch start and end time
    start_time, end_time = get_batch_interval(ts, interval)
    LOGGER.debug(start_time, end_time)

    # Prepare data
    path = Path(f"{FEATURES_DIR}/green_tripdata_2021-02.parquet")
    batch_data = load_data(path, start_time, end_time)

    if batch_data.shape[0] > 0:

        # Predictions generation
        # mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        # model = mlflow.sklearn.load_model(model_path)
        print("---")
        print("MODEL_PATH:", model_path)
        print("---")
        
        # model = joblib.load(Path(model_path))
        model = pickle.load(open(Path(model_path), 'rb'))
        predictions: pd.DataFrame = get_predictions(batch_data, model)
        LOGGER.debug(f"predictions shape = {predictions.shape}")
        LOGGER.debug(f"predictions shape = {predictions.head}")

        # Save predictions
        pred_date, pred_time = ts.to_date_string(), ts.to_time_string()
        pred_dir: Path = Path(PREDICTIONS_DIR) / pred_date
        pred_dir.mkdir(exist_ok=True)
        path = pred_dir / f"{pred_time}.parquet"
        save_predictions(predictions, path)

    else:
        LOGGER.info("No data to predict")

    LOGGER.info("Complete the pipeline")


if __name__ == "__main__":

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--model-path", dest="model_path", required=True)
    args_parser.add_argument("--ts", dest="ts", required=True)
    args_parser.add_argument(
        "--interval", dest="interval", required=False, type=int, default=60
    )
    args = args_parser.parse_args()

    ts = pendulum.parse(args.ts)
    predict(model_path=args.model_path, ts=ts, interval=args.interval)
