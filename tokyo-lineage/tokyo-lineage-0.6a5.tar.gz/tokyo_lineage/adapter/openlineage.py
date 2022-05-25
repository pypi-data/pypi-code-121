#    Copyright 2022 OpenLineage
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
import logging
from typing import Optional, Dict, Type

from openlineage.airflow import __version__ as OPENLINEAGE_AIRFLOW_VERSION
from openlineage.airflow.extractors import TaskMetadata

from openlineage.client import OpenLineageClient, OpenLineageClientOptions, set_producer
from openlineage.client.facet import DocumentationJobFacet, SourceCodeLocationJobFacet, \
    NominalTimeRunFacet, ParentRunFacet, BaseFacet
from openlineage.client.run import RunEvent, RunState, Run, Job

_DAG_DEFAULT_OWNER = 'anonymous'
_DAG_DEFAULT_NAMESPACE = 'default'

_DAG_NAMESPACE = os.getenv('OPENLINEAGE_NAMESPACE', None)
if not _DAG_NAMESPACE:
    _DAG_NAMESPACE = os.getenv(
        'MARQUEZ_NAMESPACE', _DAG_DEFAULT_NAMESPACE
    )

_PRODUCER = f"https://github.com/OpenLineage/OpenLineage/tree/" \
            f"{OPENLINEAGE_AIRFLOW_VERSION}/integration/airflow"

set_producer(_PRODUCER)


log = logging.getLogger(__name__)


class OpenLineageAdapter:
    """
    Adapter for translating Airflow metadata to OpenLineage events,
    instead of directly creating them from Airflow code.
    """
    _client = None

    def __init__(
        self,
        openlineage_url: Optional[str] = None,
        openlineage_api_key: Optional[str] = None,
        openlineage_namespace: Optional[str] = None,
        openlineage_client_options: Optional[OpenLineageClientOptions] = None
    ):
        self.openlineage_namespace = openlineage_namespace

        if openlineage_url:
            log.info(f"Sending lineage events to {openlineage_url}")
            self._client = OpenLineageClient(
                openlineage_url,
                OpenLineageClientOptions(
                    api_key=openlineage_api_key
                ))

            if openlineage_client_options:
                if not openlineage_client_options.api_key and openlineage_api_key:
                    openlineage_client_options.api_key = openlineage_api_key

                self._client = OpenLineageClient(
                    openlineage_url,
                    openlineage_client_options
                )

    @property
    def dag_namespace(self):
        if self.openlineage_namespace:
            return self.openlineage_namespace
        return _DAG_NAMESPACE or _DAG_DEFAULT_NAMESPACE

    def get_or_create_openlineage_client(self) -> OpenLineageClient:
        if not self._client:

            # Backcomp with Marquez integration
            marquez_url = os.getenv('MARQUEZ_URL')
            marquez_api_key = os.getenv('MARQUEZ_API_KEY')
            if marquez_url:
                log.info(f"Sending lineage events to {marquez_url}")
                self._client = OpenLineageClient(marquez_url, OpenLineageClientOptions(
                    api_key=marquez_api_key
                ))
            else:
                self._client = OpenLineageClient.from_environment()

        return self._client

    def start_task(
        self,
        run_id: str,
        job_name: str,
        job_description: str,
        event_time: str,
        parent_run_id: Optional[str],
        code_location: Optional[str],
        nominal_start_time: str,
        nominal_end_time: str,
        task: Optional[TaskMetadata],
        run_facets: Optional[Dict[str, Type[BaseFacet]]] = None,  # Custom run facets
    ) -> str:
        """
        Emits openlineage event of type START
        :param run_id: globally unique identifier of task in dag run
        :param job_name: globally unique identifier of task in dag
        :param job_description: user provided description of job
        :param event_time:
        :param parent_run_id: identifier of job spawning this task
        :param code_location: file path or URL of DAG file
        :param nominal_start_time: scheduled time of dag run
        :param nominal_end_time: following schedule of dag run
        :param task: metadata container with information extracted from operator
        :param run_facets:
        :return:
        """

        event = RunEvent(
            eventType=RunState.START,
            eventTime=event_time,
            run=self._build_run_self(
                run_id, parent_run_id, job_name, nominal_start_time, nominal_end_time, run_facets
            ),
            job=self._build_job_self(
                job_name, job_description, code_location, task.job_facets
            ),
            inputs=task.inputs if task else None,
            outputs=task.outputs if task else None,
            producer=_PRODUCER
        )
        self.get_or_create_openlineage_client().emit(event)
        return event.run.runId

    def complete_task(
        self,
        run_id: str,
        job_name: str,
        end_time: str,
        task: TaskMetadata
    ):
        """
        Emits openlineage event of type COMPLETE
        :param run_id: globally unique identifier of task in dag run
        :param job_name: globally unique identifier of task between dags
        :param end_time: time of task completion
        :param task: metadata container with information extracted from operator
        """

        event = RunEvent(
            eventType=RunState.COMPLETE,
            eventTime=end_time,
            run=self._build_run_self(
                run_id
            ),
            job=self._build_job_self(
                job_name, job_facets=task.job_facets
            ),
            inputs=task.inputs,
            outputs=task.outputs,
            producer=_PRODUCER
        )
        self.get_or_create_openlineage_client().emit(event)

    def fail_task(
        self,
        run_id: str,
        job_name: str,
        end_time: str,
        task: TaskMetadata
    ):
        """
        Emits openlineage event of type FAIL
        :param run_id: globally unique identifier of task in dag run
        :param job_name: globally unique identifier of task between dags
        :param end_time: time of task completion
        :param task: metadata container with information extracted from operator
        """
        event = RunEvent(
            eventType=RunState.FAIL,
            eventTime=end_time,
            run=self._build_run_self(
                run_id
            ),
            job=self._build_job_self(
                job_name
            ),
            inputs=task.inputs,
            outputs=task.outputs,
            producer=_PRODUCER
        )
        self.get_or_create_openlineage_client().emit(event)

    @staticmethod
    def _build_run(
        run_id: str,
        parent_run_id: Optional[str] = None,
        job_name: Optional[str] = None,
        nominal_start_time: Optional[str] = None,
        nominal_end_time: Optional[str] = None,
        custom_facets: Dict[str, Type[BaseFacet]] = None
    ) -> Run:
        facets = {}
        if nominal_start_time:
            facets.update({
                "nominalTime": NominalTimeRunFacet(nominal_start_time, nominal_end_time)
            })
        if parent_run_id:
            facets.update({"parentRun": ParentRunFacet.create(
                parent_run_id,
                _DAG_NAMESPACE,
                job_name
            )})

        if custom_facets:
            facets.update(custom_facets)

        return Run(run_id, facets)

    def _build_run_self(
        self,
        run_id: str,
        parent_run_id: Optional[str] = None,
        job_name: Optional[str] = None,
        nominal_start_time: Optional[str] = None,
        nominal_end_time: Optional[str] = None,
        custom_facets: Dict[str, Type[BaseFacet]] = None
    ) -> Run:
        facets = {}
        if nominal_start_time:
            facets.update({
                "nominalTime": NominalTimeRunFacet(nominal_start_time, nominal_end_time)
            })
        if parent_run_id:
            facets.update({"parentRun": ParentRunFacet.create(
                parent_run_id,
                self.dag_namespace,
                job_name
            )})

        if custom_facets:
            facets.update(custom_facets)

        return Run(run_id, facets)

    @staticmethod
    def _build_job(
        job_name: str,
        job_description: Optional[str] = None,
        code_location: Optional[str] = None,
        job_facets: Dict[str, BaseFacet] = None
    ):
        facets = {}

        if job_description:
            facets.update({
                "documentation": DocumentationJobFacet(job_description)
            })
        if code_location:
            facets.update({
                "sourceCodeLocation": SourceCodeLocationJobFacet("", code_location)
            })
        if job_facets:
            facets = {**facets, **job_facets}

        return Job(_DAG_NAMESPACE, job_name, facets)

    def _build_job_self(
        self,
        job_name: str,
        job_description: Optional[str] = None,
        code_location: Optional[str] = None,
        job_facets: Dict[str, BaseFacet] = None
    ):
        facets = {}

        if job_description:
            facets.update({
                "documentation": DocumentationJobFacet(job_description)
            })
        if code_location:
            facets.update({
                "sourceCodeLocation": SourceCodeLocationJobFacet("", code_location)
            })
        if job_facets:
            facets = {**facets, **job_facets}

        return Job(self.dag_namespace, job_name, facets)