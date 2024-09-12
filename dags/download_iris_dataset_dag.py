from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta
import requests
import logging
from airflow.models import Variable  # Best practice to use Airflow Variables for configuration
import pendulum
import pandas as pd
import os

# Best Practice: Use Airflow Variables for URLs and file paths.
# Using Airflow Variables allows configuration flexibility without modifying the code, improving maintainability and enabling changes through the Airflow UI or API.
url = Variable.get("iris_dataset_url", default_var="https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data")
file_path = Variable.get("iris_dataset_file_path", default_var="./output/iris_dataset.csv")

# Define default arguments for the DAG
# Best Practice: Standardize retries and error handling
# Set parameters like retries to make DAGs resilient to temporary issues (e.g., network errors) and avoid unnecessary failures.
default_args = {
    'owner': 'Ian',  # Ownership visibility improves accountability in production environments.
    'depends_on_past': False,  # Ensures each DAG run is independent of past runs, making it resilient to prior failures.
    'email_on_failure': False,  # Email alerts are often enabled in production but are set to False here for simplicity.
    'email_on_retry': False,  # Same reasoning as above; notifications can prevent alert fatigue in production environments.
    'retries': 1,  # Retry once on failure to handle transient issues such as network problems.
    'retry_delay': timedelta(minutes=1),  # A delay before retrying to ensure that issues (e.g., temporary network downtime) have time to resolve.
}

# Define the DAG
# Best Practice: Use descriptive names and disable unnecessary backfilling.
# Use descriptive DAG names for clarity, and disable backfilling (catchup=False) to prevent unnecessary past DAG runs.
dag = DAG(
    'download_iris_dataset',  # A clear, descriptive DAG name helps with traceability and clarity.
    default_args=default_args,  # Attach default arguments to ensure consistency in all task behaviors.
    description='A DAG to download the Iris dataset periodically',  # Clear description of what this DAG is for.
    schedule_interval="*/5 * * * *",  # Run the DAG every 5 minutes for continuous monitoring.
    start_date=pendulum.today('UTC').add(days=-2),  # Start the DAG from a couple of days ago to align with the schedule.
    catchup=False  # Disable backfilling to avoid rerunning past instances unnecessarily.
)

# Best Practice: Modularize the task logic
# Modularizing task logic ensures that the task can be reused in other DAGs and is easier to test.
def download_iris_dataset():
    try:
        logging.info(f"Starting download from {url}")
        
        # Request data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Best Practice: Always handle HTTP errors to avoid corrupt data or silent failures.
        
        # Load the response content into a pandas DataFrame
        df = pd.read_csv(url, header=None)
        logging.info("Iris dataset loaded into a DataFrame successfully.")

        # Save the dataset to a CSV file
        file_path = Variable.get("iris_dataset_file_path", default_var="./output/iris_dataset.csv")

        # Check if the parent directory exists; if not, create it
        parent_dir = os.path.dirname(file_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)  # Ensure that the output directory exists before saving the file.
        
        # Save the DataFrame as a CSV file
        df.to_csv(file_path, index=False, header=False)
        logging.info(f"Iris dataset saved to {file_path} successfully.")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading Iris dataset: {e}")
        raise  # Raise the exception to allow Airflow to capture the task failure.

# Best Practice: Use descriptive task IDs to make tasks identifiable and their purpose clear in the Airflow UI.
download_task = PythonOperator(
    task_id='download_iris_dataset_task',  # Clear, descriptive task ID for easy identification in the UI.
    python_callable=download_iris_dataset,  # The function to run when this task executes.
    execution_timeout=timedelta(minutes=1),  # Limit task runtime to 1 minute to prevent hanging tasks in production.
    dag=dag,  # Associate this task with the DAG defined earlier.
)
