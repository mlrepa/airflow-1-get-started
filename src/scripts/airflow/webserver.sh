#!/usr/bin/env bash

export AIRFLOW_HOME=./airflow

airflow db init

airflow users create \
    --username admin \
    --password admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@admin.org

airflow webserver --port 8080
