"""
Code that goes along with the Airflow tutorial located at:
https://github.com/airbnb/airflow/blob/master/airflow/example_dags/tutorial.py
"""

import os
import sys
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2018, 4, 4, 0, 0, 0),
    "email": ["support@scribbledata.io"],
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "catchup": False,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG(
    "contrib-pipeline-v1",
    schedule_interval=timedelta(hours=2),
    catchup=False,
    depends_on_past=False,
    default_args=default_args,
)

cli = os.path.join(os.environ["ENRICH_ROOT"], "manage", "bin", "run_enrichcli.sh")

conf = os.path.join(
    os.environ["ENRICH_CUSTOMERS"], "scribble", "Contrib", "conf", "test.json"
)

t1 = BashOperator(
    task_id="run_test_pipeline",
    bash_command="{} run-pipeline -c {}".format(cli, conf),
    dag=dag,
)


t2 = EmailOperator(
    task_id="notification",
    to="support@scribbledata.io",
    subject="Completed task",
    html_content="Completed ",
    dag=dag,
)

t2.set_upstream(t1)
