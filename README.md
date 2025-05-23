# 🌬️ Basics of Airflow for Modern AI and MLOps

![Airflow Basics for Modern AI and MLOps](assets/images/airflow-banner-1.png){width=800}

This repository contains the example code and setup instructions for the "Airflow Basics for Modern AI and MLOps" tutorial. It will guide you through setting up Apache Airflow using Docker and running a basic example DAG.

## 👩‍💻 Installation & Setup

Follow these steps to get your Airflow environment up and running.

### 1️⃣ Fork / Clone this Repository

First, get the tutorial example code onto your local machine:

```bash
git clone https://github.com/mlrepa/airflow-1-get-started.git
cd airflow-1-get-started
```

### 2️⃣ Initialize Your Airflow Environment

Before starting Airflow for the first time, you need to prepare your environment. This involves creating necessary directories and initializing the Airflow database.

**📂 Create Airflow Folder Structure**

These directories will be mounted into your Docker containers, allowing your local files to be accessed by Airflow:

```bash
mkdir -p ./airflow/{dags,logs,plugins,config}
```

> **Understanding Mounted Directories:**
>
> - `./airflow/dags`: Place your DAG (workflow definition) files here.
> - `./airflow/logs`: Contains logs from task executions and the Airflow scheduler.
> - `./airflow/plugins`: You can add your custom Airflow plugins here.
> - `./airflow/config`: (Optional) For custom Airflow configuration files like `airflow.cfg` if you choose to override defaults. *The provided `docker-compose.yaml` might already handle basic configurations.*

**⚙️ Set Up Environment Variables**

For Linux users, it's crucial to set the host user ID to ensure correct file permissions for files created by Airflow within the Docker containers.

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

> 👉 **Tip:** This step helps avoid permission issues where files written by Airflow containers (running as `root` by default) become inaccessible to your host user.

**🗂️ Initialize the Database**

This step sets up the Airflow metadata database and creates the initial admin user.

```bash
docker compose up airflow-init
```

> ⚠️ **Default Credentials:**
> The account created by `airflow-init` has the login: `airflow` and password: `airflow`.
> Remember to change these for any non-local or production environment!

## 🚀 Launch Airflow

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

### 3️⃣ Interacting with the REST API

Airflow provides a robust REST API for programmatic interaction.

**Authentication (Get an Access Token):**

The Airflow API uses JWT (JSON Web Tokens) for authentication.

```bash
# Request an access token
TOKEN=$(curl -X POST "http://localhost:8080/api/v1/auth" \
  -H "Content-Type: application/json" \
  -u "airflow:airflow" \
  --silent | jq -r '.access_token')

# Optional: Check the token
echo $TOKEN
```

> ⚠️ **API Authentication Update:** The method `POST /auth/token` with username/password in the body is for older Airflow versions or specific auth backends. The current stable API often uses Basic Auth for the `/api/v1/auth` endpoint to get a token as shown above, or expects a pre-configured auth backend. Please refer to the [Airflow API Security Docs](https://airflow.apache.org/docs/apache-airflow/stable/security/api.html) for the most up-to-date authentication methods relevant to your Airflow version and configuration.

**Example API Request (List DAGs):**

```bash
# Get list of DAGs (top 3)
curl -X GET "http://localhost:8080/api/v1/dags?limit=3" \
  -H "Authorization: Bearer $TOKEN"
```

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

## 🛠️ DEV Environment for Pipeline Development (Optional)

If you prefer to develop or debug your Airflow DAGs and custom Python code in a local Python virtual environment (outside of Docker, perhaps for better IDE integration):

- **Install `uv`:** `uv` is a fast Python package installer and resolver.

    ```bash
    # Install uv if you haven't already
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Or consult official uv documentation for other installation methods
    ```

- **Create Virtual Environment & Install Dependencies:**
    Ensure you have a `pyproject.toml` file in your project root that defines your project dependencies.

    ```bash
    # Create and activate virtual environment (e.g., using Python 3.12)
    uv venv .venv --python 3.12
    source .venv/bin/activate

    # Install core dependencies (e.g., apache-airflow and any providers you need)
    # This assumes your dependencies are listed in pyproject.toml or a requirements.txt
    # If using pyproject.toml and your project is installable:
    uv pip install -e .

    # Or from requirements.txt:
    # uv pip install -r requirements.txt

    # Install development dependencies (linters, formatters)
    # Assuming these are defined in your pyproject.toml under [project.optional-dependencies]
    uv pip install -e ".[dev]" 
    # Or add them individually:
    # uv pip install black mypy ruff
    ```

> 👉 **Note for DAG Development:** Even when developing locally, your DAGs will ultimately run inside the Airflow Docker environment. Ensure that any Python packages your DAGs depend on are also available in the Docker image Airflow uses (you might need to build a custom Docker image if you have many specific dependencies).
