"""
This file is intended to be used as a DAG in Airflow.
It should be placed in the dags folder of the Airflow installation.
It is not meant to be run as a standalone script in the current environment.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# local directory where the scripts will be run
SCRIPTS_DIR = "/home/rusen/github-repos/mastodon-trending-statuses/scripts/"
# conda environment name to activate
CONDA_ENV = "mastodon-trending-statuses"

with DAG(
    "mastodon_trending_statuses",
    description = "A DAG to ELT trending statuses and their adjacent statuses from mastodon",
    start_date = datetime(2025, 3, 1), 
    schedule = "0 3,9,15,21 * * 6,0,1", # to capture the weekend trends
) as dag:
    
    extract_and_load = BashOperator(
        task_id = "extract_and_load",
        bash_command = f"cd {SCRIPTS_DIR} && \
            conda run -n {CONDA_ENV} python collect_data.py"
    )

    transform = BashOperator(
        task_id = "transform",
        bash_command = f"cd {SCRIPTS_DIR} && \
            conda run -n {CONDA_ENV} python clean_data.py"
    )

    extract_and_load >> transform