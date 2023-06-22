from airflow import DAG
from airflow.operators.bash import BashOperator
import os
import pendulum

from config import START_DATE_TIME, END_DATE_TIME, BATCH_INTERVAL
from src.pipelines.monitor_model import monitor_model


dag = DAG(
    dag_id='monitor_model',
    start_date=pendulum.parse(START_DATE_TIME).add(minutes=BATCH_INTERVAL),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval='@hourly',
    max_active_runs=1
)

with dag:

    PROJECT_DIR = os.environ["PROJECT_DIR"]
    TS = "{{ ts }}" # The DAG run’s logical date 
    
    # wait_predictions = ExternalTaskSensor(
    #     task_id='wait_predictions',
    #     external_dag_id='predict',
    #     external_task_id='predict_task',
    #     allowed_states=['success'],
    #     failed_states=['failed', 'skipped'],
    #     execution_date_fn=lambda exec_date: exec_date - relativedelta(minutes=BATCH_INTERVAL),
    #     poke_interval=30
    # )

    # # TODO: add a model sensor
    # # model_path = ...
    # check_model_exist = FileSensor(
    #     task_id='check_predictions_file',
    #     filepath=f'{Path(".").absolute() / model_path}',
    #     timeout=10
    # )
    
    monitor_model = BashOperator(
        task_id='monitor_model',
        bash_command=f'''
        
            cd $PROJECT_DIR && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \
            echo { TS } && \
            echo { BATCH_INTERVAL } && \
                
            python src/pipelines/monitor_model.py \
                --ts { TS } \
                --interval { BATCH_INTERVAL }
        '''
    )

    monitor_model
