import json

import joblib
import mlflow
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

from config import (
    FEATURES_DIR,
    MLFLOW_TRACKING_URI, 
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_DEFAULT_MODEL_NAME
)


def train() -> None:
    """Train a linear regression model on the given dataset."""

    # Define the target variable, numerical features, and categorical features
    target = "duration_min"
    num_features = [
        "passenger_count", "trip_distance", "fare_amount", "total_amount"
    ]
    cat_features = ["PULocationID", "DOLocationID"]

    print("Load train data")
    data = pd.read_parquet(f"{FEATURES_DIR}/green_tripdata_2021-01.parquet")

    # Filter out outliers
    data = data[(data.duration_min >= 1) & (data.duration_min <= 60)]
    data = data[(data.passenger_count > 0) & (data.passenger_count <= 6)]

    # Split data into training and validation sets
    train_data = data.loc[:30000, :]
    val_data = data.loc[30000:, :]

    print("Train model")
    model = LinearRegression()
    model.fit(
        X=train_data[num_features + cat_features],
        y=train_data[target],
    )

    print("Get predictions for validation")
    train_preds = model.predict(train_data[num_features + cat_features])
    val_preds = model.predict(val_data[num_features + cat_features])

    print("Calculate validation metrics: MAE")
    # Scoring
    print(mean_absolute_error(train_data[target], train_preds))
    print(mean_absolute_error(val_data[target], val_preds))

    print("Calculate validation metrics: MAPE")
    print(mean_absolute_percentage_error(train_data[target], train_preds))
    print(mean_absolute_percentage_error(val_data[target], val_preds))

    print("Save the model")
    joblib.dump(model, "models/model.joblib") 

    print("Log model to MLflow")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow_experiment = mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    model_info = mlflow.sklearn.log_model(model, MLFLOW_DEFAULT_MODEL_NAME)

    mlflow.register_model(model_uri=model_info.model_uri, name=MLFLOW_DEFAULT_MODEL_NAME)

    with open("reports/mlflow_report.json", "w") as mlflow_report_f:
        json.dump(
            obj={
                "experiment_id": mlflow_experiment.experiment_id,
                "run_id": model_info.run_id
            },
            fp=mlflow_report_f,
            indent=4
        )


if __name__ == "__main__":

    train()
