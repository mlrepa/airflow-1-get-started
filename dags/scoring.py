from airflow import DAG
from airflow.operators.bash import BashOperator
import pendulum

from dags.config import CLONED_PROJECT_PATH

from config import (
    BATCH_INTERVAL,
    END_DATE_TIME,
    START_DATE_TIME
)
from utils.tasks import (
    create_tmp_dir,
    clone,
    load_model,
    load_data,
    download_predictions,
    clean
)


dag = DAG(
    dag_id="scoring",
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval="@hourly",
    max_active_runs=1,
)

with dag:

    run_scoring = BashOperator(
        task_id="scoring_task",
        bash_command=f"""
            cd {CLONED_PROJECT_PATH} && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \    
            python src/pipelines/predict.py \
                --ts {{{{ ts }}}} \
                --interval { BATCH_INTERVAL }
        """
    )

    # [Create task instances]

    create_tmp_dir = create_tmp_dir(CLONED_PROJECT_PATH)
    clone = clone(CLONED_PROJECT_PATH)
    clean = clean(CLONED_PROJECT_PATH)

    # [Set task dependencies]
    create_tmp_dir >> clone >> load_model >> load_data >> run_scoring >> download_predictions >> clean
