import pendulum
from airflow.sdk import dag, task

from assignment_6_airflow.load_data import load_data
from assignment_6_airflow.split_dataset import split_dataset

@dag(
    dag_id="assignment_6_airflow",
    schedule="* * * * *",  # every minute
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["assignment6", "mlops", "iris"],
)
def assignment_6_airflow_dag():
    
    @task
    def load_data_task(**context) -> None:
        """Load the iris dataset and save features to CSV."""
        load_data(folder_path="/opt/airflow/data/")

    @task
    def split_dataset_task(test_size: float, **context) -> None:
        """Split the dataset into train and test sets."""
        split_dataset(test_size, folder_path="/opt/airflow/data/")
        
    load_data_op = load_data_task()
    split_dataset_op = split_dataset_task(test_size=0.2)

    load_data_op >> split_dataset_op
        
assignment_6_airflow_dag()
