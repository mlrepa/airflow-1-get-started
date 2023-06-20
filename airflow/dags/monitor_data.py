from airflow.decorators import dag, task
from airflow.sensors.filesystem import FileSensor
import logging
from pathlib import Path
import pendulum

from config import START_DATE_TIME, END_DATE_TIME, BATCH_INTERVAL, FEATURES_DIR, REFERENCE_DIR 
from src.pipelines.monitor_data import monitor_data

@dag(
    dag_id='monitor_data',
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval='@hourly',
    max_active_runs=1
)
def monitor_data_taskflow():
    
    
    # PROJECT_DIR = Path(".").absolute()
    
    # data_path = f'{FEATURES_DIR}/green_tripdata_2021-02.parquet'
    # check_data_file = FileSensor(
    #     task_id='check_data_file',
    #     # filepath=Path(FEATURES_DIR) / 'green_tripdata_2021-02.parquet',
    #     filepath=data_path,
    #     poke_interval=30,
    #     timeout=10,
    # )
    
    # print(f"\n\n\nCHECK DATA FILE: {data_path}")
    # print(check_data_file.poke(context={}))
    # print("\n\n\n")
    
    # # Check Reference data file exists
    # file_path = f'{PROJECT_DIR}/{REFERENCE_DIR}/reference_data_2021-01.parquet'
    # check_reference_data_file = FileSensor(
    #     task_id='check_reference_data_file',
    #     filepath=file_path,
    #     # filepath=PROJECT_DIR / REFERENCE_DIR / 'reference_data_2021-01.parquet',
    #     timeout=10
    # )
    # print(f"\nCHECK REFERENCE DATA: {PROJECT_DIR / FEATURES_DIR / 'reference_data_2021-01.parquet'}")
    # print(check_reference_data_file .execute(context={}))
    # print("\n")

    @task()
    def monitor_data_task(logical_date=None):
        monitor_data(ts=logical_date, interval=BATCH_INTERVAL)

    monitor_data_task = monitor_data_task()
    
    # check_data_file >> check_reference_data_file >> 
    # monitor_data_task

monitor_data_taskflow()
