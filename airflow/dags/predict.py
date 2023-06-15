from airflow.decorators import dag, task
import pendulum

from config import START_DATE_TIME, END_DATE_TIME, BATCH_INTERVAL
from src.pipelines.predict import predict


@dag(
    dag_id='predict',
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval='@hourly',
    max_active_runs=1
)
def predict_taskflow():

    @task()
    def predict_task(logical_date=None):
        predict(ts=logical_date, interval=BATCH_INTERVAL)

    predict_task()


predict_taskflow()
