from pathlib import Path
import shutil
from typing import Text

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
    AIRFLOW_DAGS_PARAMS,
    CLONED_PROJECT_PATH,
    MLFLOW_TRACKING_URI,
    MLFLOW_DEFAULT_MODEL_NAME
)
from utils.tasks import clone_repo_task
from utils.utils import create_dag_run_dir


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

    @dag.task()
    def create_tmp_dir(dag_run_dir: Text):
        """Creates temporary folder (of local repository) in $AIRFLOW_RUN_DIR, from which
        scoring script will be run.
        Args:
            dag_run_dir: local repository path; dag_run_dir = $AIRFLOW_RUN_DIR/<timestamp>/<repo_name>
        """
        create_dag_run_dir(dag_run_dir)

    @dag.task()
    def clone(dag_run_dir: Text):
        """Clones repository in dag_run_dir, switches on specified branch.
        Args:
            dag_run_dir: local repository path; dag_run_dir = $AIRFLOW_RUN_DIR/<timestamp>/<repo_name>
        """
        clone_repo_task(
            repo_url=AIRFLOW_DAGS_PARAMS.get("repo_url"),
            branch=AIRFLOW_DAGS_PARAMS.get("branch"),
            repo_local_path=dag_run_dir,
            repo_username=AIRFLOW_DAGS_PARAMS.get("repo_username"),
            repo_password=AIRFLOW_DAGS_PARAMS.get("repo_password")
        )

    run_scoring = BashOperator(
        task_id="scoring_task",
        bash_command=f"""
            
            cp $PROJECT_DIR/models/model.joblib {CLONED_PROJECT_PATH}/models && \
            cp -r $PROJECT_DIR/data/features/* {CLONED_PROJECT_PATH}/data/features && \
            
            cd {CLONED_PROJECT_PATH} && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \    
            python src/pipelines/predict_mlflow.py \
                --model-uri "{{{{ ti.xcom_pull(task_ids='get_model_in_production') }}}}" \
                --ts {{{{ ts }}}} \
                --interval { BATCH_INTERVAL } && \
            
            export SRC_PRED_DIR={CLONED_PROJECT_PATH}/data/predictions/{{{{ ds }}}} && \
            export DST_PRED_DIR=$PROJECT_DIR/data/predictions/{{{{ ds }}}} && \
            export TS_TIME={{{{macros.datetime.strftime(macros.datetime.fromisoformat(ts), "%H:%M:%S")}}}} && \
            mkdir -p $DST_PRED_DIR && \
            cp $SRC_PRED_DIR/$TS_TIME.parquet $DST_PRED_DIR
        """
    )

    @dag.task(trigger_rule='all_success')
    def clean(dag_run_dir):
        """
        Removes the repository temporary folder.
        Args:
            dag_run_dir: local repository path; dag_run_dir = $AIRFLOW_RUN_DIR/<timestamp>/<repo_name>
        """

        shutil.rmtree(Path(dag_run_dir).parent)

    # [Create task instances]
    # os.makedirs(CLONED_PROJECT_PATH, exist_ok=True)

    model_in_prod_uri = get_model_in_production()

    create_tmp_dir = create_tmp_dir(CLONED_PROJECT_PATH)
    clone = clone(CLONED_PROJECT_PATH)
    clean = clean(CLONED_PROJECT_PATH)

    # [Set task dependencies]
    model_in_prod_uri >> create_tmp_dir >> clone >> run_scoring >> clean
