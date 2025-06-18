# 🌬️ Basics of Airflow for Modern AI and MLOps

<img src="assets/images/airflow-banner-1.png" alt="Airflow Basics for Modern AI and MLOps" width="800">

This repository contains the example code and setup instructions for the "Airflow Basics for Modern AI and MLOps" tutorial. It will guide you through setting up Apache Airflow using Docker and running a basic example DAG.

## 👩‍💻 Installation & Setup

Follow these steps to get your Airflow environment up and running.

### 1️⃣ Fork / Clone this Repository

First, get the tutorial example code onto your local machine:

```bash
git clone https://github.com/mlrepa/airflow-for-modern-ai-and-mlops.git
cd airflow-for-modern-ai-and-mlops
```

## 🚀 Launch Airflow

Running options:

- Standalone (python environment)
- Docker Compose (docker container)

### 1. Run Airflow Standalone (Local Installation)

For development or learning purposes, you can run Airflow in standalone mode directly on your machine. This method is simpler but less production-ready than the Docker Compose approach.

**Step 1: Install Airflow Locally**

If you haven't installed Airflow locally, you can do so using the development environment setup:

```bash
# Create virtual environment and install dependencies
uv venv .venv --python 3.12
source .venv/bin/activate
uv sync
```

**Step 2: Run Airflow Standalone**  

The Standalone command will initialise the database, make a user, and start all components for you.

```bash
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
airflow standalone
```

> 📝 **Note:** The admin username and password will be displayed in the command output. Look for lines like:
>
> ```
> standalone | Airflow is ready
> standalone | Login with username: admin  password: [generated_password]
> ```

**Step 3: Configure DAGs Folder (Optional)**

To make DAGs from this repository's `dags/` folder visible in your local Airflow instance:

1. **Stop Airflow** by pressing `Ctrl+C` in the terminal where `airflow standalone` is running

2. **Update the configuration** in `~/airflow/airflow.cfg`:

   ```bash
   # Find the [core] section and update the dags_folder setting
   dags_folder = [PATH_TO_YOUR_REPO]/dags
   ```

3. **Restart Airflow**:

   ```bash
   airflow standalone
   ```

**Access the Web Interface**

- **URL:** [http://localhost:8080](http://localhost:8080)
- **Credentials:** Use the admin `username` and `password` shown in the startup output

### 2. Run Aiflow in Docker ⚙️

**Step 1: Set Up Environment Variables**

For Linux users, it's crucial to set the host user ID to ensure correct file permissions for files created by Airflow within the Docker containers.

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

> 👉 **Tip:** This step helps avoid permission issues where files written by Airflow containers (running as `root` by default) become inaccessible to your host user.

**Step 2: Initialize the Database**

This step sets up the Airflow metadata database and creates the initial admin user.

```bash
docker compose up airflow-init
```

> ⚠️ **Default Credentials:**
> The account created by `airflow-init` has the login: `airflow` and password: `airflow`.
> Remember to change these for any non-local or production environment!

**Step 3: Run with Docker Compose**

With the environment initialized, you can now start all the Airflow services:

```bash
docker compose up -d
```

The `-d` flag runs the containers in detached mode (in the background).

<details>
<summary>🔍 Understanding the Docker Compose Services</summary>

The `docker-compose.yaml` file defines several services that work together:

- `airflow-webserver`: The Airflow User Interface (UI). Accessible at [http://localhost:8080](http://localhost:8080).
- `airflow-scheduler`: The core Airflow component that monitors DAGs and triggers task runs. It doesn't have exposed ports.
- `airflow-worker` (if defined): Executes the tasks scheduled by the scheduler (common in CeleryExecutor setups).
- `airflow-triggerer` (if defined): Manages deferrable tasks.
- `postgres` (or similar): The PostgreSQL database used by Airflow to store its metadata. Accessible (e.g., for DB tools) typically on `localhost:5432`.
- `redis` (if defined): Often used as a message broker for CeleryExecutor.

For more details on the official Docker Compose setup, refer to the [Airflow Docker Documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#fetching-docker-compose-yaml).

</details>

To check the status of your running containers and ensure they are healthy:

```bash
docker ps
```

## 📺 Accessing Your Airflow Environment

Once Airflow is running, you can interact with it in several ways:

### 1️⃣ Via the Web Interface (UI)

This is the most common way to monitor and manage your DAGs.

- **URL:** [http://localhost:8080](http://localhost:8080)
- **Login:** `airflow`
- **Password:** `airflow`

### 2️⃣ Using the Command Line Interface (CLI)

You can execute Airflow CLI commands directly within the running Airflow containers.

**Option A: Using `docker compose run` (for one-off commands)**

This starts a new, temporary container to run the command. Replace `airflow-1-get-started-airflow-scheduler-1` with the actual name of your scheduler or webserver service if it differs (check `docker-compose.yaml` or `docker ps`). *Often, the scheduler service is a good target for CLI commands.*

```bash
# Example: Get Airflow version and configuration info
docker compose run airflow-scheduler airflow info
# Example: List DAGs
docker compose run airflow-scheduler airflow dags list
```

> 👉 **Note:** The service name like `airflow-1-get-started-airflow-apiserver-1` in your original example might be from a custom compose file. For the official one, it's usually `airflow-scheduler` or `airflow-webserver`.

**Option B: Executing commands in an existing container**

This opens an interactive shell inside a running container (e.g., the webserver or scheduler).

```bash
# Get a bash shell inside the webserver container
docker exec -ti airflow-1-get-started-airflow-webserver-1 /bin/bash
# Or, more commonly for official compose file:
# docker exec -ti <your_project_name>-airflow-webserver-1 /bin/bash

# Once inside, you can run Airflow commands directly:
# airflow dags list
# airflow tasks test your_dag_id your_task_id YYYY-MM-DD
# exit
```

> (Replace `<your_project_name>-airflow-webserver-1` with the actual name from `docker ps`)

## 🧹 Cleaning Up Your Environment

When you're done, you can stop and remove the Airflow containers and associated resources.

**Stop the Cluster:**

```bash
docker compose down
```

**Full Cleanup (Stop, Remove Containers, Volumes, and Orphans):**

This command is useful if you want to reset your environment completely, including the database data.

```bash
docker compose down -v --remove-orphans
```

> ⚠️ **Data Loss:** Using the `-v` flag will remove the Docker volumes, including your Airflow metadata database. This means all DAG run history, connections, etc., will be lost.

**Full Cleanup including Images (Use with Caution):**

This will also remove the Docker images that were downloaded or built for this setup.

```bash
docker compose down --volumes --rmi all
```
