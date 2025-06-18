import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from datetime import datetime
from airflow import DAG
from airflow.decorators import task


def get_features(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Get the features from the dataset.
    """
    features = dataset.copy()
    # Rename columns: replace (cm) and spaces
    features.rename(
        columns=lambda s: s.replace("(cm)", "").strip().replace(" ", "_"), inplace=True
    )

    # Uncomment to add features
    # features['sepal_length_to_sepal_width'] = (
    #     features['sepal_length'] / features['sepal_width']
    # )
    # features['petal_length_to_petal_width'] = (
    #     features['petal_length'] / features['petal_width']
    # )

    return features


with DAG(
        dag_id="assignment-6-airflow",
        start_date=datetime(2022, 1, 1),
        schedule="* * * * *",
        tags=["assignment-6-airflow"]
    ) as dag:
    """
    DAG to load the iris dataset and split it into train and test sets.
    """

    @task()
    def load_data():
        # Load the iris dataset
        iris_data = load_iris(as_frame=True)
        print(list(iris_data.target_names))

        # Get the feature DataFrame from the iris dataset
        dataset = iris_data.frame
        features = get_features(dataset)
        features.to_csv("data/features_iris.csv", index=False)

    @task()
    def split_dataset():
        """
        Split the dataset into train and test sets.
        """
        dataset = pd.read_csv("data/features_iris.csv")

        # Split in train/test
        df_train, df_test = train_test_split(
            dataset, test_size=0.2, random_state=42
        )

        df_train.to_csv("data/train.csv", index=False)
        df_test.to_csv("data/test.csv", index=False)

    load_data() >> split_dataset()
