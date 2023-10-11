import os

import pendulum
from airflow.operators.bash import BashOperator

from airflow import DAG
from config import BATCH_INTERVAL, END_DATE_TIME, START_DATE_TIME

dag = DAG(
    dag_id="train",
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval="@weekly",
    max_active_runs=1,
)

with dag:

    PROJECT_DIR = os.environ["PROJECT_DIR"]
    # TS = "{{ ts }}"  # The DAG run’s logical date
    # EXP_NAME = "{{ ds }}"

    train = BashOperator(
        task_id="train",
        bash_command=f"""

            cd $PROJECT_DIR && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \
            dvc exp run
        """
    )

    train
