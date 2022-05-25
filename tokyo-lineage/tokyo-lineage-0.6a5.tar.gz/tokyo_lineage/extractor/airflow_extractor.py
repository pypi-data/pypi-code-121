import time
from typing import Optional, Type, List

from airflow.models import BaseOperator
from airflow.models.dagrun import DagRun
from airflow.models.taskinstance import TaskInstance
from airflow.utils.state import State
from airflow.utils.db import create_session
from openlineage.airflow.extractors.base import TaskMetadata
from openlineage.airflow.utils import (
    DagUtils,
    JobIdMapping,
    get_custom_facets,
    new_lineage_run_id
)

from tokyo_lineage.extractor.base import BaseExtractor
from tokyo_lineage.metadata_extractor.base import BaseMetadataExtractor
from tokyo_lineage.metadata_extractor.airflow.airflow_default import AIRFLOW_METADATA_EXTRACTORS
from tokyo_lineage.models.base import BaseJob, BaseTask
from tokyo_lineage.models.airflow_task import AirflowTask
from tokyo_lineage.models.airflow_dag import AirflowDag
from tokyo_lineage.utils.airflow import (
    get_dagbag,
    get_task_instances_from_dagrun,
    get_dag_from_dagbag,
    get_task_from_dag,
    instantiate_task_from_ti,
    get_location
)
from tokyo_lineage.adapter import OpenLineageAdapter
from tokyo_lineage.utils.airflow import get_connection

def openlineage_job_name(dag_id: str, task_id: str) -> str:
    return f'{dag_id}.{task_id}'


class AirflowExtractor(BaseExtractor):
    def __init__(
        self,
        custom_metadata_extractors: Optional[List[Type[BaseMetadataExtractor]]] = None,
        openlineage_conn_id: Optional[str] = None
    ):
        super(AirflowExtractor, self).__init__(AIRFLOW_METADATA_EXTRACTORS)
        
        if custom_metadata_extractors:
            self.register_custom_metadata_extractors(
                custom_metadata_extractors
            )
        
        if openlineage_conn_id:
            conn = get_connection(openlineage_conn_id)

            try:
                assert conn.conn_type == 'http'

                openlineage_url = 'http://{host}:{port}' \
                                    .format(host=conn.host, port=conn.port)

                openlineage_api_key = conn.get_password()
                openlineage_namespace = conn.schema

                BaseExtractor._ADAPTER = OpenLineageAdapter(
                    openlineage_url=openlineage_url,
                    openlineage_api_key=openlineage_api_key,
                    openlineage_namespace=openlineage_namespace
                )
            except Exception as e:
                self.log.debug(e)

    def get_metadata_extractor(
        self,
        task: Type[BaseTask]
    ) -> Type[BaseMetadataExtractor]:
        extractor = super().get_metadata_extractor(task)

        return extractor if extractor is not None else AirflowMetaExtractor(task)

    def handle_jobs_from_dagrun(self, jobs: List[DagRun]) -> None:
        _jobs = []
        dagbag = get_dagbag()

        for job in jobs:
            dag = get_dag_from_dagbag(dagbag, job.dag_id)
            _jobs.append(AirflowDag(dag.dag_id, dag, job))

        return self.handle_jobs_run(_jobs)

    def handle_job_run(self, job: AirflowDag):
        task_instances = get_task_instances_from_dagrun(job.dagrun)

        if len(task_instances) < 1:
            return

        for task_instance in task_instances:
            _task = get_task_from_dag(job.dag, task_instance.task_id)
            _task, _ = instantiate_task_from_ti(_task, task_instance)

            self._handle_task_run(_task, task_instance, job)

    def _handle_task_run(
        self,
        task: Type[BaseOperator],
        task_instance: TaskInstance,
        job: Type[BaseJob]
    ):
        task_id = task.task_id
        operator_name = task_instance.operator
        _task = AirflowTask(task_id, operator_name, task, task_instance)
        self.handle_task_run(_task, job)

    def handle_task_run(self, task: Type[BaseTask], job: Type[BaseJob]):
        # Register start_task
        self._register_task_start(task, job)

        # Register finish_task or fail_task
        self._register_task_state(task, job)

    def _register_task_start(self, task: AirflowTask, job: AirflowDag):
        _task = task.task
        task_instance = task.task_instance
        dag = job.dag
        dagrun = job.dagrun

        meta_extractor = self.get_metadata_extractor(task)
        task_metadata = meta_extractor.extract()

        run_id = new_lineage_run_id(dagrun.run_id, task.task_id)
        job_name = f'{dag.dag_id}.{task.task_id}'
        job_description = dag.description
        event_time = DagUtils.get_start_time(task_instance.start_date)
        parent_run_id = dagrun.run_id
        code_location = get_location(dag.full_filepath)
        nominal_start_time = DagUtils.get_start_time(task_instance.start_date)
        nominal_end_time = task_instance.end_date

        if nominal_end_time is None:
            nominal_end_time = DagUtils.get_end_time(
                task_instance.execution_date,
                dag.following_schedule(task_instance.execution_date))
        else:
            nominal_end_time = DagUtils.to_iso_8601(nominal_end_time)

        run_facets = {**task_metadata.run_facets, **get_custom_facets(_task, dagrun.external_trigger)}

        task_run_id = self.register_task_start(
            run_id,
            job_name,
            job_description,
            event_time,
            parent_run_id,
            code_location,
            nominal_start_time,
            nominal_end_time,
            task_metadata,
            run_facets
        )

        JobIdMapping.set(
            job_name,
            dagrun.run_id,
            task_run_id
        )

    def _register_task_state(self, task: AirflowTask, job: AirflowDag):
        _task = task.task
        task_instance = task.task_instance
        dag = job.dag
        dagrun = job.dagrun
        
        meta_extractor = self.get_metadata_extractor(task)

        with create_session() as session:
            task_run_id = JobIdMapping.pop(
                self._openlineage_job_name_from_task_instance(task_instance), dagrun.run_id, session)

        task_metadata = meta_extractor.extract()

        # Note: task_run_id could be missing if it was removed from airflow
        # or the job could not be registered.
        job_name = openlineage_job_name(dag.dag_id, task.task_id)
        run_id = new_lineage_run_id(dagrun.run_id, task.task_id)
        
        if not task_run_id:
            task_run_id = self.register_task_start(
                run_id,
                job_name,
                dag.description,
                DagUtils.to_iso_8601(task_instance.start_date),
                dagrun.run_id,
                get_location(dag.full_filepath),
                DagUtils.to_iso_8601(task_instance.start_date),
                DagUtils.to_iso_8601(task_instance.end_date),
                task_metadata,
                {**task_metadata.run_facets, **get_custom_facets(_task, dagrun.external_trigger)}
            )

        end_date = DagUtils.to_iso_8601(task_instance.end_date)
        
        if task_instance.state in {State.SUCCESS, State.SKIPPED}:
            self.register_task_finish(
                task_run_id,
                job_name,
                end_date,
                task_metadata
            )
        else:
            self.register_task_fail(
                task_run_id,
                job_name,
                end_date,
                task_metadata
            )

    @staticmethod
    def _openlineage_job_name_from_task_instance(task_instance) -> str:
        return openlineage_job_name(task_instance.dag_id, task_instance.task_id)

    @staticmethod
    def _now_ms():
        return int(round(time.time() * 1000))

class AirflowMetaExtractor(BaseMetadataExtractor):
    def __init__(self, task):
        super(AirflowMetaExtractor, self).__init__(task)

    @classmethod
    def get_operator_classnames(cls) -> List[str]:
        return ['*']
    
    def validate(self):
        assert True
    
    def extract(self) -> Optional[TaskMetadata]:
        return TaskMetadata(
            name=f'{self.task.task.dag_id}.{self.task.task_id}'
        )