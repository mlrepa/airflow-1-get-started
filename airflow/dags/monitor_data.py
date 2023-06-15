from airflow.decorators import dag, task
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from pathlib import Path
import pendulum

from config.dags_config import START_DATE_TIME, END_DATE_TIME, BATCH_INTERVAL
from src.pipelines.monitor_data import monitor_data


@dag(
    dag_id='monitor_data',
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval='@hourly',
    max_active_runs=1
)
def monitor_data_taskflow():

    wait_predictions = ExternalTaskSensor(
        task_id='wait_predictions',
        external_dag_id='predict',
        external_task_id='predict_task',
        allowed_states=['success'],
        failed_states=['failed', 'skipped'],
        poke_interval=30
    )

    check_predictions_file = FileSensor(
        task_id='check_predictions_file',
        filepath=f'{Path(".").absolute() /  "data/predictions/{{ ds }}.parquet"}',
        timeout=10
    )

    @task()
    def monitor_data_task(logical_date=None):
        monitor_data(ts=logical_date, interval=BATCH_INTERVAL)

    monitor_data_task = monitor_data_task()
    wait_predictions >> check_predictions_file >> monitor_data_task


monitor_data_taskflow()
