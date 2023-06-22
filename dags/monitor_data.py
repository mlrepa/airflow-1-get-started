from airflow import DAG
from airflow.operators.bash import BashOperator
import os
import pendulum

from config import START_DATE_TIME, END_DATE_TIME, BATCH_INTERVAL
from src.pipelines.monitor_data import monitor_data

dag = DAG(
    dag_id='monitor_data',
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval='@hourly',
    max_active_runs=1
)

with dag:

    PROJECT_DIR = os.environ["PROJECT_DIR"]
    TS = "{{ ts }}" # The DAG run’s logical date 
    
    monitor_data = BashOperator(
        task_id='monitor_data',
        bash_command=f'''
        
            cd $PROJECT_DIR && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \
            echo { TS } && \
            echo { BATCH_INTERVAL } && \
                
            python src/pipelines/monitor_data.py \
                --ts { TS } \
                --interval { BATCH_INTERVAL }
        '''
    )

    monitor_data