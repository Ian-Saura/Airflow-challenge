"""
DAG to periodically download the Iris dataset using Airflow. The task fetches the dataset from a configured URL,
saves it as a CSV file, and ensures proper error handling and directory management.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta
import requests
import logging
from airflow.models import Variable
import pendulum
import pandas as pd
import os

# Airflow Variables for URL and file path
url = Variable.get("iris_dataset_url", default_var="https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data")
file_path = Variable.get("iris_dataset_file_path", default_var="./output/iris_dataset.csv")

# Default arguments for the DAG
default_args = {
    'owner': 'Ian',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Define the DAG
dag = DAG(
    'download_iris_dataset',
    default_args=default_args,
    description='A DAG to download the Iris dataset periodically',
    schedule_interval="*/5 * * * *",
    start_date=pendulum.today('UTC').add(days=-2),
    catchup=False
)

# Task logic to download and save the Iris dataset
def download_iris_dataset():
    try:
        logging.info(f"Starting download from {url}")
        
        response = requests.get(url)
        response.raise_for_status()  # Handle HTTP errors
        
        df = pd.read_csv(url, header=None)
        logging.info("Iris dataset loaded into a DataFrame successfully.")
        file_path = Variable.get("iris_dataset_file_path", default_var="./output/iris_dataset.csv")

        parent_dir = os.path.dirname(file_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)  # Create the output directory if it doesn't exist.
        
        df.to_csv(file_path, index=False, header=False)
        logging.info(f"Iris dataset saved to {file_path} successfully.")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading Iris dataset: {e}")
        raise

# Define the download task
download_task = PythonOperator(
    task_id='download_iris_dataset_task',
    python_callable=download_iris_dataset,
    execution_timeout=timedelta(minutes=1),
    dag=dag,
)
