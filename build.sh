#!/usr/bin/env bash
export $(grep -v '#.*' .env | xargs)

export AIRFLOW_UID=$(id -u)

docker-compose build
