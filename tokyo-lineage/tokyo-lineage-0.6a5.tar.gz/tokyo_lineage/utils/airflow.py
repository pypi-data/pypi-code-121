import random
import logging
from typing import Type, Optional, List, Tuple, Dict
from datetime import datetime

from airflow.operators import BaseOperator
from airflow.models import DAG as AirflowDag
from airflow.utils.db import create_session
from airflow.models.dagrun import DagRun
from airflow.models.taskinstance import TaskInstance

from airflow import secrets
from airflow.models import Connection

from openlineage.airflow.utils import get_location as openlineage_get_location

log = logging.getLogger(__name__)

def get_dagbag():
    from airflow.models.dagbag import DagBag # Prevent circular import
    return DagBag()

def get_dagruns(*filters) -> Optional[List[DagRun]]:
    dagruns = None

    with create_session() as session:
        q = session.query(DagRun).filter(*filters)
        dagruns = q.all()
    
    return dagruns

def get_task_instances(*filters) -> Optional[List[TaskInstance]]:
    taskinstances = None

    with create_session() as session:
        q = session.query(TaskInstance).filter(*filters)
        taskinstances = q.all()
    
    return taskinstances

def get_task_instances_from_dagrun(
    dagrun: DagRun,
    state=None
) -> Optional[List[TaskInstance]]:
    with create_session() as session:
        return dagrun.get_task_instances(state, session)

def get_task_instance_from_dagrun(
    dagrun: DagRun,
    task_id: str
) -> Optional[List[TaskInstance]]:
    with create_session() as session:
        return dagrun.get_task_instance(task_id, session)

def get_dag_from_dagbag(dagbag, dag_id: str) -> Optional[AirflowDag]:
    return dagbag.get_dag(dag_id)

def get_task_from_dag(dag: AirflowDag, task_id: str) -> Type[BaseOperator]:
    return dag.get_task(task_id)

def instantiate_task(
    task: Type[BaseOperator],
    execution_date: datetime
) -> Tuple[Type[BaseOperator], TaskInstance]:
    task_instance = TaskInstance(task=task, execution_date=execution_date)
    
    task_instance.refresh_from_db()
    task_instance.render_templates()

    return task, task_instance

def instantiate_task_from_ti(
    task: Type[BaseOperator],
    task_instance: TaskInstance
) -> Tuple[Type[BaseOperator], TaskInstance]:
    task_instance.task = task
    task_instance.refresh_from_db()
    task_instance.render_templates()

    return task, task_instance

def get_template_context(task_instance: TaskInstance) -> Optional[Dict]:
    with create_session() as session:
        return task_instance.get_template_context(session)

def get_location(file_path) -> str:
    location = openlineage_get_location(file_path)

    return location if location is not None else file_path

def get_connections(conn_id: str) -> List[Connection]:
    return secrets.get_connections(conn_id=conn_id)

def get_connection(conn_id: str) -> Connection:
    # Choosing random connection to allow basic load balancing
    # See https://airflow.apache.org/docs/apache-airflow/1.10.2/concepts.html
    conn = random.choice(list(get_connections(conn_id)))

    if conn.host:
        log.info("Using connection to: %s", conn.log_info())
    return conn