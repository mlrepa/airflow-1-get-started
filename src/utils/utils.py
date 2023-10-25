from typing import Text, Tuple
from pathlib import Path

import pandas as pd
import pendulum


def get_batch_interval(
    ts: pendulum.DateTime, interval: int
) -> Tuple[Text, Text]:
    """Get data batch for an interval.

    Args:
        ts (pendulum.DateTime): Timestamp.
        interval (int): Interval in minutes.

    Returns:
        Tuple[Text, Text]:
            Tuple of start and end time.
    """

    batch_start_time = ts.subtract(minutes=interval)

    # Convert to 'datetime' format
    ts = ts.to_datetime_string()
    batch_start_time = batch_start_time.to_datetime_string()

    start_time = batch_start_time
    end_time = ts

    return start_time, end_time


def extract_batch_data(
    data: pd.DataFrame, start_time: Text, end_time: Text
) -> pd.DataFrame:
    """Extract the batch data for specified time interval.

    Args:
        data (pd.DataFrame): Pandas dataframe.
        start_time (Text): Start time.
        end_time (Text): End time.

    Returns:
        pd.DataFrame: Data batch - Pandas dataframe.
    """

    data = data.set_index("lpep_pickup_datetime")
    data = data.sort_index().loc[start_time:end_time]

    return data


def prepare_scoring_data(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare scoring data.

    Args:
        data (pd.DataFrame): Input data - Pandas dataframe.

    Returns:
        pd.DataFrame: Pandas dataframe with specific features (columns).
    """

    # Define the target variable, numerical features, and categorical features
    num_features = [
        "passenger_count", "trip_distance", "fare_amount", "total_amount"
    ]
    cat_features = ["PULocationID", "DOLocationID"]
    data = data.loc[:, num_features + cat_features]

    return data


def load_data(path: Path, start_time: Text, end_time: Text) -> pd.DataFrame:
    """Load data and process data

    Args:
        path (Path): Path to data.
        start_time (Text): Start time.
        end_time (Text): End time.

    Returns:
        pd.DataFrame: Loaded Pandas dataframe.
    """

    print(f"Data source: {path}")
    data = pd.read_parquet(path)

    print("Extract batch data")
    data = extract_batch_data(data, start_time=start_time, end_time=end_time)
    data = data.fillna(data.median(numeric_only=True)).fillna(0)

    return data


def get_predictions(data: pd.DataFrame, model) -> pd.DataFrame:
    """Predictions generation.

    Args:
        data (pd.DataFrame): Pandas dataframe.
        model (_type_): Model object.

    Returns:
        pd.DataFrame: Pandas dataframe with predictions column.
    """

    scoring_data = prepare_scoring_data(data)
    predictions = data[["uuid"]].copy()
    predictions["predictions"] = model.predict(scoring_data)

    return predictions


def save_predictions(predictions: pd.DataFrame, path: Path) -> None:
    """Save predictions to parquet file.

    Args:
        predictions (pd.DataFrame): Pandas dataframe with predictions column.
        path (Path): Path to save predictions.
    """

    # Save predictions data to parquet format
    predictions.to_parquet(path, engine="fastparquet")
    print(f"Predictions saved to: {path}")