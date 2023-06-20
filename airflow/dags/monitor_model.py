from airflow.decorators import dag, task
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from dateutil.relativedelta import relativedelta
from pathlib import Path
import pendulum

from config import START_DATE_TIME, END_DATE_TIME, BATCH_INTERVAL
from src.pipelines.monitor_model import monitor_model


@dag(
    dag_id='monitor_model',
    start_date=pendulum.parse(START_DATE_TIME).add(minutes=BATCH_INTERVAL),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval='@hourly',
    max_active_runs=1
)
def monitor_model_taskflow():

    wait_predictions = ExternalTaskSensor(
        task_id='wait_predictions',
        external_dag_id='predict',
        external_task_id='predict_task',
        allowed_states=['success'],
        failed_states=['failed', 'skipped'],
        execution_date_fn=lambda exec_date: exec_date - relativedelta(minutes=BATCH_INTERVAL),
        poke_interval=30
    )

    # TODO: add a model sensor
    # model_path = ...
    check_model_exist = FileSensor(
        task_id='check_predictions_file',
        filepath=f'{Path(".").absolute() / model_path}',
        timeout=10
    )

    @task()
    def monitor_model_task(logical_date=None):
        monitor_model(ts=logical_date, interval=BATCH_INTERVAL)

    monitor_model_task = monitor_model_task()
    
    wait_predictions >> check_model_exist >> monitor_model_task


monitor_model_taskflow()
