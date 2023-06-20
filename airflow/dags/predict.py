from airflow.decorators import dag, task
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.filesystem import FileSensor
from pathlib import Path
import pendulum

from config import START_DATE_TIME, END_DATE_TIME, BATCH_INTERVAL, FEATURES_DIR
from src.pipelines.predict import predict


@dag(
    dag_id='predict',
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval='@hourly',
    max_active_runs=1
)
def predict_taskflow():
    
    # wait_data_monitoring = ExternalTaskSensor(
    #     task_id='wait_data_monitoring',
    #     external_dag_id='monitor_data',
    #     external_task_id='monitor_data_task',
    #     allowed_states=['success'],
    #     failed_states=['failed', 'skipped'],
    #     poke_interval=30
    # )

    # data_path = f'{FEATURES_DIR}/green_tripdata_2021-02.parquet'
    # check_data_file = FileSensor(
    #     task_id='check_data_file',
    #     filepath=f'{Path(".").absolute().parent / data_path}',
    #     timeout=10
    # )

    @task()
    def predict_task(logical_date=None):
        predict(ts=logical_date, interval=BATCH_INTERVAL)

    predict_task = predict_task()
    
    # wait_data_monitoring >> check_data_file  >> 
    predict_task


predict_taskflow()
