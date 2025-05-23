# Basics of Airflow for Modern AI and MLOps

![Airflow Basics for Modern AI and MLOps](assets/images/airflow-banner-1.png){width=800}

## :woman_technologist: Installation

### 1 - Fork / Clone this repository

Get the tutorial example code:

```bash
git clone https://github.com/mlrepa/airflow-1-get-started.git
cd airflow-1-get-started
```

### 2 - Initializing Environment

Before starting Airflow for the first time, you need to prepare your environment, i.e. create the necessary files, directories and initialize the database.

**Create Airflow folder structure**

```bash
mkdir -p ./airflow/{dags,logs,plugins,config}
```

Some directories in the container are mounted, which means that their contents are synchronized between your computer and the container.

- `./airflow/dags` - you can put your DAG files here.
- `./airflow/logs` - contains logs from task execution and scheduler.
- `./airflow/plugins` - you can put your custom plugins here.
- `./airflow/airflow.cfg` - Airflow settings file.


**Set up environment**
On Linux, the quick-start needs to know your host user id and needs to have group id set to 0. Otherwise the files created in dags, logs and plugins will be created with root user ownership. You have to make sure to configure them for the docker-compose:

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

**Initialize the database**
On all operating systems, you need to run database migrations and create the first user account. To do this, run.

```bash
docker compose up airflow-init
```

Note: The account created has the login `airflow`and the password `airflow`


## :rocket: Launch Airflow

Now you can start all services:

```bash
docker compose up -d
```

<details>
<summary> Details on the cluster components </summary>

- `airflow-webserver` - Airflow UI, available on [http://localhost:8080](http://localhost:8080)
- `airflow-scheduler` - Airflow Scheduler (doesn't hae exposed endpoints)
- `postgres` - Airflow PostgreSQL DataBase, available on [http://localhost:5432](http://localhost:5432)

See [docs](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#fetching-docker-compose-yaml) for `docker-compose.yaml` details and instructions.


</details>

In a second terminal you can check the condition of the containers and make sure that no containers are in an unhealthy condition:

```bash
docker ps
```


## :tv: Accessing the environment

After starting Airflow, you can interact with it in 3 ways:

- by running CLI commands.
- via a browser using the web interface.
- using the REST API.


### 1 - Running the CLI commands

You can also run CLI commands, but you have to do it in one of the defined `airflow-*` services. For example, to run `airflow info`, run the following command:

```bash
docker compose run airflow-1-get-started-airflow-apiserver-1 airflow info
```

You can also run CLI commands in the `airflow-webserver` service. To do this, run the following command:

```bash
docker exec -ti airflow-webserver /bin/bash
```

### Accessing the web interface

Once the cluster has started up, you can log in to the web interface and begin experimenting with DAGs.

The webserver is available at: `http://localhost:8080`. The default account has the login `airflow` and the password `airflow`.

### Sending requests to the REST API

The webserver is available at: `http://localhost:8080`. The default account has the login `airflow` and the password `airflow`.

The Airflow public API uses JWT (JSON Web Token) for authenticating API requests [docs](https://airflow.apache.org/docs/apache-airflow/stable/security/api.html).

```bash
curl -X POST "http://localhost:8080/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "airflow", "password": "airflow"}'
```

Get list of DAGs (top 3):

```bash
curl -X GET "http://localhost:8080/api/v2/dags?limit=3" \
  -H "Authorization: Bearer <token>"


```

## 🧹 Cleaning up

Stop cluster

```bash
docker compose down
```

The docker-compose environment we have prepared is a "quick-start" one. It was not designed to be used in production. The best way to recover from any problem is to clean it up and restart from scratch. Run the command:
  
```bash
docker compose down -v --remove-orphans
```

To stop and delete containers, delete volumes with database data and download images, run:

```bash
docker compose down --volumes --rmi all
```


## ⚒️ DEV environment for pipelines development

- In case you want to develop, run or debug Pipelines in Python Virtual Environment
- Create virtual environment using `uv` and install python libraries
  
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment from pyproject.toml
uv venv .venv --python=3.12
source .venv/bin/activate

# Install dependencies using uv
uv pip install --upgrade pip setuptools wheel
uv pip install -e .

# Install development dependencies
uv add --dev black mypy ruff
```
