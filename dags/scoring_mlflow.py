from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.sensors.base import PokeReturnValue
import mlflow
import pendulum

from config import (
    BATCH_INTERVAL,
    END_DATE_TIME,
    START_DATE_TIME,
    CLONED_PROJECT_PATH,
    MLFLOW_TRACKING_URI,
    MLFLOW_DEFAULT_MODEL_NAME
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
    dag_id="scoring_mlflow",
    start_date=pendulum.parse(START_DATE_TIME),
    end_date=pendulum.parse(END_DATE_TIME),
    schedule_interval="@hourly",
    max_active_runs=1,
)

with dag:

    # [Implement task definitions]
    @task.sensor(poke_interval=20, timeout=10)
    def get_model_in_production():

        client = mlflow.MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
        model_versions = client.search_model_versions(f"name='{MLFLOW_DEFAULT_MODEL_NAME}'")
        prod_versions = [mv.source for mv in model_versions if mv.current_stage == "Production"]

        if prod_versions:
            model_in_prod_uri = prod_versions[0]
            print(f"Production model URI = {model_in_prod_uri}")
            return PokeReturnValue(is_done=True, xcom_value=model_in_prod_uri)
        else:
            print("Production model not found!")
            return PokeReturnValue(is_done=False, xcom_value=None)

    run_scoring = BashOperator(
        task_id="scoring_task",
        bash_command=f"""
            cd {CLONED_PROJECT_PATH} && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \    
            python src/pipelines/predict_mlflow.py \
                --model-uri "{{{{ ti.xcom_pull(task_ids='get_model_in_production') }}}}" \
                --ts {{{{ ts }}}} \
                --interval { BATCH_INTERVAL }
        """
    )

    # [Create task instances]

    model_in_prod_uri = get_model_in_production()
    create_tmp_dir = create_tmp_dir(CLONED_PROJECT_PATH)
    clone = clone(CLONED_PROJECT_PATH)
    clean = clean(CLONED_PROJECT_PATH)

    # [Set task dependencies]
    model_in_prod_uri >> create_tmp_dir >> clone >> load_model >> load_data >> run_scoring >> download_predictions >> clean

