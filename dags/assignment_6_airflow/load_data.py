import pandas as pd
from sklearn.datasets import load_iris


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

def load_data(folder_path: str = "data/") -> None:
    # Load the iris dataset
    iris_data = load_iris(as_frame=True)
    print(list(iris_data.target_names))

    # Get the feature DataFrame from the iris dataset
    dataset = iris_data.frame
    features = get_features(dataset)
    features.to_csv(f"{folder_path}/features_iris.csv", index=False)

if __name__ == "__main__":
    # Load the iris dataset
    iris_data = load_iris(as_frame=True)
    print(list(iris_data.target_names))

    # Get the feature DataFrame from the iris dataset
    dataset = iris_data.frame
    features = get_features(dataset)
    features.to_csv("data/features_iris.csv", index=False)