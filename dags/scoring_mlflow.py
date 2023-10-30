from airflow import DAG
from airflow.decorators import task
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.sensors.base import PokeReturnValue

import os
import pendulum
from typing import Any, Dict, List, Optional, Tuple

from dags.config import CLONED_PROJECT_PATH
from config import (
    PREDICTIONS_DIR, 
    BATCH_INTERVAL,
    END_DATE_TIME,
    START_DATE_TIME,
    MLFLOW_TRACKING_URI,
    MLFLOW_DEFAULT_MODEL_NAME
)
from utils.tasks import (
    create_tmp_dir,
    clone,
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

    #######################################################
    # [Implement task definitions]
    #######################################################
    
    # [1] Detect if there is a production model in MLflow
    # ===================================================
    @task.sensor(poke_interval=20, timeout=10)
    def model_sensor():

        import mlflow
        
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
    
    # [2] Download the model from MLflow
    # ===================================================
    @task
    def download_model_from_mlflow(model_uri: str, dst_path: str) -> Tuple[str, str]:
        """
        Downloads a model from the specified model URI and saves it to the specified destination path.

        Args:
            model_uri (str): The URI of the model to download.
            dst_path (str): The path to save the downloaded model to.

        Returns:
            A str containing the destination path.
        """
        import mlflow
        from mlflow.pyfunc import load_model
        
        print("------")
        print("MODEL_URI", model_uri)
        print("DST_PATH", dst_path)
        print("------")
        
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        load_model(model_uri=model_uri, dst_path=dst_path)
        return dst_path 

    # [3] Load Data (features)
    # ===================================================
    download_data = BashOperator(
        task_id="download_data",
        bash_command=f"cp -r $PROJECT_DIR/data/features/* {CLONED_PROJECT_PATH}/data/features"
    )
    
    # [4] Run Scoring / Get Predictions
    # ===================================================
    run_scoring = BashOperator(
        task_id="scoring_task",
        bash_command=f"""
            cd {CLONED_PROJECT_PATH} && echo $PWD && \
            export PYTHONPATH=. && echo $PYTHONPATH && \    
            python src/pipelines/scoring_mlflow.py \
                --model-path {CLONED_PROJECT_PATH}/models/{MLFLOW_DEFAULT_MODEL_NAME}/model.pkl \
                --ts {{{{ ts }}}} \
                --interval { BATCH_INTERVAL }
        """
    )
    
    # [5] Upload Predictions to storage
    # ===================================================    
    @task
    def upload_predictions():
        """Upload predictions from a source directory to a destination directory.

        This task is responsible for copying predictions from a source directory to a destination directory. It uses the Airflow context to get the execution date (ds and ts) and the timestamp (ts) to construct the source file path. It also uses the PROJECT_DIR environment variable to construct the destination directory path.
        """
        
        from airflow.operators.python import get_current_context
        from datetime import datetime
        from pathlib import Path
        import shutil
        
        context: Dict[str, Any] = get_current_context()
        ds: str = context["ds"]
        ts: str = context["ts"]
        
        ts_time: str = datetime.fromisoformat(ts).strftime("%H:%M:%S")
        src_pred_dir: str = f"{CLONED_PROJECT_PATH}/{PREDICTIONS_DIR}/{ds}"        
        src_predictions_path: str = Path(src_pred_dir) / f"{ts_time}.parquet"
        dst_pred_dir: str = f"{os.getenv('PROJECT_DIR')}/{PREDICTIONS_DIR}/{ds}"
        
        print("------")
        print("SRC_PRED_DIR", src_pred_dir)
        print("DST_PRED_DIR", dst_pred_dir)
        print("TS_TIME", ts_time)
        print("------")
        
        os.makedirs(dst_pred_dir, exist_ok=True)
        shutil.copy(src_predictions_path, dst_pred_dir)
    
    # [DEV] This task simulates the original `clone` by copying the local repository 
    # ===================================================
    clone = BashOperator(
        task_id="clone_repo",
        bash_command=f"cp -r $PROJECT_DIR/* {CLONED_PROJECT_PATH}"
    )

    #######################################################
    # [Create task instances]
    #######################################################
    model_in_prod_uri = model_sensor()
    create_tmp_dir = create_tmp_dir(CLONED_PROJECT_PATH)
    # clone = clone(CLONED_PROJECT_PATH)
    model_path = download_model_from_mlflow(model_in_prod_uri, f"{CLONED_PROJECT_PATH}/models")
    upload_predictions = upload_predictions()
    clean = clean(CLONED_PROJECT_PATH)

    
    #######################################################
    # [Set Tasks dependencies]
    #######################################################
    chain(
        model_in_prod_uri,
        create_tmp_dir,
        clone,
        [model_path, download_data],
        run_scoring,
        upload_predictions,
        clean
    )
