

# Airflow Iris Dataset Download DAG

This project contains an **Airflow DAG** designed to periodically download the **Iris dataset** from the UCI Machine Learning Repository and save it as a CSV file.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [How to Use](#how-to-use)
5. [DAG Overview](#dag-overview)
6. [Project Structure](#project-structure)
7. [Docker Compose Overview](#docker-compose-overview)
8. [Additional Notes](#additional-notes)

## Overview

This repository demonstrates:
- How to create a periodic task using **Apache Airflow** to download a dataset from the internet.
- Using **Docker Compose** to easily run an Airflow instance.
- Basic logging and error handling practices for downloading data with Python in a production environment.

## Prerequisites

Before you start, ensure you have the following installed on your local machine:

- **Docker** (https://docs.docker.com/get-docker/)
- **Docker Compose** (https://docs.docker.com/compose/install/)

> Note: If you are using **Docker Desktop**, Docker Compose is included.

## Setup Instructions

Follow these steps to set up and run the project:

1. **Clone this repository** to your local machine:

   ```bash
   git clone https://github.com/your-repo/airflow-iris-dataset-dag.git
   cd airflow-iris-dataset-dag
   ```

2. **Start Airflow** using Docker Compose:

   ```bash
   docker-compose up
   ```

   This command will start the following services:
   - Airflow webserver (available at [http://localhost:8080](http://localhost:8080)).
   - Airflow scheduler to manage the DAGs.
   - Airflow worker to execute tasks.
   - PostgreSQL database for Airflow metadata.

   > Note: The first time you run this, it may take a few minutes for Docker to pull all required images.

3. **Access the Airflow web UI**:

   Open a web browser and go to [http://localhost:8080](http://localhost:8080). Use the following default credentials to log in:

   - **Username**: `airflow`
   - **Password**: `airflow`

4. **Trigger the DAG**:

   In the Airflow UI, navigate to the DAGs tab, locate the DAG named `download_iris_dataset`, and click the trigger button (a "play" button).

5. **Check the Output**:

   Once the DAG runs successfully, the Iris dataset will be saved to the `output/iris_dataset.csv` file inside your project directory.

## How to Use

- **Trigger DAG**: You can manually trigger the DAG in the Airflow UI as described in step 4. Alternatively, the DAG will automatically run every 5 minutes based on the defined schedule (`*/5 * * * *`).
- **View Logs**: You can monitor task execution logs from the Airflow UI by clicking on the task inside the DAG and navigating to the `Logs` tab.

## DAG Overview

### `download_iris_dataset` DAG

This DAG performs the following tasks:
1. **Downloads the Iris dataset** from [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data).
2. **Saves the dataset** as a CSV file in the `output/` directory.

### DAG Parameters

- **Retries**: If the download fails (e.g., due to network issues), it will retry once after a delay of 1 minute.
- **Catchup**: Disabled (`catchup=False`) to prevent backfilling unnecessary past DAG runs.
- **Execution Timeout**: Each task is limited to 1 minute of execution time.

## Project Structure

```bash
.
├── dags/
│   └── download_iris_dataset_dag.py     # Airflow DAG definition
├── logs/                                # Airflow task logs (auto-generated)
├── output/                              # Directory where the Iris dataset CSV will be saved
├── docker-compose.yaml                  # Docker Compose setup to run Airflow
└── README.md                            # Project documentation
```

- `dags/`: Contains the Airflow DAG definition (`download_iris_dataset_dag.py`).
- `logs/`: This directory stores logs from task executions, allowing for debugging and auditing.
- `output/`: Directory where the Iris dataset CSV will be saved after successful DAG runs.
- `docker-compose.yaml`: The Docker Compose file defines the Airflow environment with services for Airflow webserver, scheduler, worker, and PostgreSQL.

## Docker Compose Overview

The `docker-compose.yaml` file sets up the following services for the Airflow instance:

- **Postgres**: PostgreSQL database for storing Airflow's metadata.
- **Webserver**: The Airflow web UI, available at [http://localhost:8080](http://localhost:8080).
- **Scheduler**: Service responsible for scheduling and managing DAG runs.
- **Worker**: Executes the tasks defined in your DAG.

### Docker Compose Configuration:

```yaml
version: '3'
x-airflow-common:
  &airflow-common
  image: apache/airflow:latest
  environment:
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__WEBSERVER__SECRET_KEY: your_secret_key
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./output:/opt/airflow/output
  depends_on:
    - postgres

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data

  webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"

  scheduler:
    <<: *airflow-common
    command: scheduler

  worker:
    <<: *airflow-common
    command: celery worker

volumes:
  postgres-db-volume:
```

## Additional Notes

- Ensure that Docker and Docker Compose are properly installed before running the project.
- You can modify the default configuration (e.g., the URL for the dataset or the schedule) using **Airflow Variables** in the Airflow UI or by updating the `download_iris_dataset_dag.py` file.
- If needed, update the directory paths in the `docker-compose.yaml` file to match your local environment.


