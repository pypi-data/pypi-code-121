import base64
import datetime
import logging
import re
import time
import uuid
from typing import Optional, List, Callable, Any, Dict

import dateutil.parser
import dill
import numpy as np
import pytz
from qiskit.ignis.mitigation import CompleteMeasFitter
from qiskit.providers import BaseBackend, BaseJob, JobStatus
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.qobj import QasmQobj
from qiskit.result import Result
from qiskit.result.models import ExperimentResult

from .util import to_backend

LOG = logging.getLogger(__name__)


class BaseExperiment:
    _callback_pickled: Optional[bytes]
    tags: List[str]
    transpiler_backend_provider: str
    transpiler_backend_hub: Optional[str]
    transpiler_backend_group: Optional[str]
    transpiler_backend_project: Optional[str]
    transpiler_backend_name: str
    arguments: np.ndarray
    noise_model: Dict[datetime.datetime, NoiseModel]
    date: datetime.datetime
    external_id: str
    parameters: Optional[dict]
    qobj_list: List[QasmQobj]

    def __init__(self, external_id: str,
                 tags: List[str],
                 qobj_list: List[QasmQobj],
                 arguments: np.array,
                 transpiler_backend: Optional[BaseBackend],
                 noise_model: Optional[Dict[datetime.datetime, NoiseModel]] = None,
                 parameters: Optional[dict] = None,
                 callback: 'Optional[Callable[[FinishedExperiment, Optional[CompleteMeasFitter]], Any]]' = None):
        self._callback_pickled = dill.dumps(callback, recurse=True) if callback is not None else None
        self.tags = tags
        if transpiler_backend is not None:
            self.transpiler_backend_provider = type(transpiler_backend.provider()).__name__
            self.transpiler_backend_hub = transpiler_backend.hub if hasattr(transpiler_backend, 'hub') else None
            self.transpiler_backend_group = transpiler_backend.group if hasattr(transpiler_backend, 'group') else None
            self.transpiler_backend_project = transpiler_backend.project if hasattr(transpiler_backend, 'project') else None
            self.transpiler_backend_name = transpiler_backend.name()
        else:
            self.transpiler_backend_provider = ''
            self.transpiler_backend_name = ''
            self.transpiler_backend_hub = None
            self.transpiler_backend_group = None
            self.transpiler_backend_project = None
        self.arguments = arguments
        self.parameters = parameters
        self.external_id = external_id
        self.qobj_list = qobj_list
        self.date = datetime.datetime.now(tz=pytz.utc)
        self.noise_model = noise_model

    def find_tag(self, regex_pattern: str) -> List[str]:
        return [t for t in self.tags if len(re.findall(regex_pattern, t)) > 0]

    def get_tag_param(self, parameter: str) -> Optional[str]:
        results = [t.replace(f'{parameter}=', '') for t in self.tags if t.startswith(f'{parameter}=')]
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        else:
            raise AssertionError(f"For the parameter {parameter} there are more than one entries found: {results}")

    @property
    def transpiler_backend(self) -> Optional[BaseBackend]:
        return to_backend(
            self.transpiler_backend_provider, self.transpiler_backend_name, hub=self.transpiler_backend_hub,
            group=self.transpiler_backend_group, project=self.transpiler_backend_project
        )

    @property
    def callback(self) -> 'Optional[Callable[[FinishedExperiment, Optional[CompleteMeasFitter]], Any]]':
        return dill.loads(self._callback_pickled)

    def get_id(self) -> str:
        return f'{type(self).__name__}_{self.external_id}'

    @staticmethod
    def _attempt_to_serialize(data):
        try:
            import json
            return json.loads(json.dumps(data))
        except Exception:
            LOG.debug(f"Could not create json from {type(data)}...")
        if isinstance(data, np.ndarray):
            return data.tolist()
        else:
            raise AssertionError(f'Data was not serializable: {type(data)}')
            # LOG.debug(f'Hardcore serialization!')
            # return base64.standard_b64encode(dill.dumps(data).decode('utf8'))

    def to_dict(self) -> dict:
        return {
            'qobj_list': [qobj.to_dict() for qobj in self.qobj_list],
            'date': self.date.isoformat(),
            'transpiler_backend_name': self.transpiler_backend_name,
            'transpiler_backend_hub': self.transpiler_backend_hub,
            'transpiler_backend_group': self.transpiler_backend_group,
            'transpiler_backend_project': self.transpiler_backend_project,
            'transpiler_backend_provider': self.transpiler_backend_provider,
            'noise_model': dict((cd.isoformat(), n.to_dict(serializable=True)) for cd, n in (self.noise_model or {}).items()),
            'parameters': dict(
                (k, base64.standard_b64encode(dill.dumps(v)).decode('utf8'))
                for k, v in self.parameters.items()),
            'external_id': self.external_id,
            'arguments': BaseExperiment._attempt_to_serialize(self.arguments),
            'callback': base64.standard_b64encode(self._callback_pickled).decode('utf8'),
            'tags': self.tags
        }

    @staticmethod
    def from_dict(input_dict: Optional[dict]) -> Optional['BaseExperiment']:
        import copy
        input_dict = copy.deepcopy(input_dict)

        if input_dict is None:
            return None
        experiment = BaseExperiment(
            transpiler_backend=None,
            qobj_list=[QasmQobj.from_dict(qobj_dict) for qobj_dict in input_dict.get('qobj_list', [])],
            noise_model=dict((datetime.datetime.fromisoformat(cd), NoiseModel.from_dict(n))
                             for cd, n in input_dict.get('noise_model', {}).items()),
            external_id=input_dict.get('external_id', None),
            arguments=np.asarray(input_dict.get('arguments', [])),
            parameters=dict([
                (k, dill.loads(base64.standard_b64decode(v.encode('utf8'))))
                for k, v in input_dict.get('parameters', {}).items()]),
            callback=None,
            tags=input_dict.get('tags', [])
        )
        experiment.date = dateutil.parser.parse(input_dict['date']) if 'date' in input_dict else None
        experiment.transpiler_backend_name = input_dict.get('transpiler_backend_name', '')
        experiment.transpiler_backend_hub = input_dict.get('transpiler_backend_hub', None)
        experiment.transpiler_backend_group = input_dict.get('transpiler_backend_group', None)
        experiment.transpiler_backend_project = input_dict.get('transpiler_backend_project', None)
        experiment.transpiler_backend_provider = input_dict.get('transpiler_backend_provider', None)
        if 'callback' in input_dict:
            experiment._callback_pickled = base64.standard_b64decode(input_dict.get('callback').encode('utf8'))

        return experiment

    def serialize(self) -> bytes:
        import dill
        return dill.dumps(self.to_dict())

    @staticmethod
    def deserialize(b: bytes) -> 'BaseExperiment':
        import dill
        dictionary = dill.loads(b)
        return BaseExperiment.from_dict(dictionary)


class PreparedExperiment(BaseExperiment):

    def __init__(self, external_id: str, tags: List[str], qobj_list: List[QasmQobj], arguments: np.array,
                 transpiler_backend: Optional[BaseBackend],
                 noise_model: Optional[Dict[datetime.datetime, NoiseModel]] = None,
                 parameters: Optional[dict] = None,
                 callback: 'Optional[Callable[[FinishedExperiment], np.array]]' = None):
        super().__init__(external_id, tags, qobj_list, arguments, transpiler_backend, noise_model, parameters, callback)

    def to_dict(self) -> dict:
        return super().to_dict()

    @staticmethod
    def from_dict(input_dict: Optional[dict]) -> Optional['PreparedExperiment']:
        base = BaseExperiment.from_dict(input_dict)
        prepared_experiment = PreparedExperiment(
            external_id=base.external_id,
            tags=base.tags,
            qobj_list=base.qobj_list,
            arguments=base.arguments,
            transpiler_backend=None,
            noise_model=base.noise_model,
            parameters=base.parameters,
            callback=base.callback
        )
        prepared_experiment.transpiler_backend_name = base.transpiler_backend_name
        prepared_experiment.transpiler_backend_provider = base.transpiler_backend_provider
        prepared_experiment.transpiler_backend_hub = base.transpiler_backend_hub
        prepared_experiment.transpiler_backend_group = base.transpiler_backend_group
        prepared_experiment.transpiler_backend_project = base.transpiler_backend_project
        return prepared_experiment

    def serialize(self) -> bytes:
        import dill
        return dill.dumps(self.to_dict())

    @staticmethod
    def deserialize(b: bytes) -> 'PreparedExperiment':
        import dill
        dictionary = dill.loads(b)
        return PreparedExperiment.from_dict(dictionary)


class RunningExperiment(PreparedExperiment):
    execution_backend_provider: str
    execution_backend_hub: Optional[str]
    execution_backend_group: Optional[str]
    execution_backend_project: Optional[str]
    execution_backend_name: str
    job_list: List[BaseJob]

    def __init__(self, prepared_experiment: PreparedExperiment, job_list: List[BaseJob],
                 execution_backend: Optional[BaseBackend] = None):
        super().__init__(
            prepared_experiment.external_id,
            prepared_experiment.tags,
            prepared_experiment.qobj_list,
            prepared_experiment.arguments,
            prepared_experiment.transpiler_backend,
            prepared_experiment.noise_model,
            prepared_experiment.parameters,
            prepared_experiment.callback
        )
        self.date = prepared_experiment.date
        self.job_list = job_list
        if execution_backend is not None:
            self.execution_backend_provider = type(execution_backend.provider()).__name__
            self.execution_backend_name = execution_backend.name()
            self.execution_backend_hub = execution_backend.hub if hasattr(execution_backend, 'hub') else None
            self.execution_backend_group = execution_backend.group if hasattr(execution_backend, 'group') else None
            self.execution_backend_project = execution_backend.project if hasattr(execution_backend, 'project') else None
        else:
            self.execution_backend_provider = ''
            self.execution_backend_name = ''
            self.execution_backend_hub = None
            self.execution_backend_group = None
            self.execution_backend_project = None

    def is_execution_pending(self):
        if len(self.job_list) < len(self.qobj_list):
            LOG.info(f'Not all qobjs are run in a job! Not done yet!')
            return True
        return False

    def is_done(self):
        if self.is_execution_pending():
            return False
        status = [job.status() for job in self.job_list]
        LOG.info(f'Status of all jobs: {status}')
        if JobStatus.ERROR in status:
            LOG.error([s for s in status if s is JobStatus.ERROR])
            raise Exception("Job Error occurred!")
        return all([s in JOB_FINAL_STATES for s in status])

    def wait(self, timeout=None, wait=5, callback=None) -> 'Optional[FinishedExperiment]':
        start_time = time.time()
        while not self.is_done():
            elapsed_time = time.time() - start_time
            if timeout is not None and elapsed_time >= timeout:
                return None
            time.sleep(wait)
            if callback:
                callback(self)
            else:
                LOG.info(f'Experminent runnning: {self.external_id}.')

        return self._to_finished_experiment()

    @property
    def execution_backend(self) -> Optional[BaseBackend]:
        return to_backend(
            self.execution_backend_provider, self.execution_backend_name, hub=self.execution_backend_hub,
            group=self.execution_backend_group, project=self.execution_backend_project
        )

    def _to_finished_experiment(self) -> 'FinishedExperiment':
        LOG.info(f'Experminent done: {self.external_id}. To FinishedExperiment...')
        status_list = [job.status() for job in self.job_list]
        results_list = [job.result().results for job in self.job_list]

        return FinishedExperiment(
            running_experiment=self,
            status_list=status_list,
            results=results_list
        )

    def to_dict(self) -> dict:
        output_dict = super().to_dict()
        backend = self.transpiler_backend
        from qiskit.providers.ibmq import IBMQBackend
        if isinstance(backend, IBMQBackend):
            output_dict['job_id_list'] = [j.job_id() for j in self.job_list]
        else:
            LOG.warning(f'A running experiment can only be saved and loaded when using a backend that supports'
                        f'loading from job_ids. This backend {backend} does not support this!')
            output_dict['job_id_list'] = []
        output_dict['execution_backend_name'] = self.execution_backend_name
        output_dict['execution_backend_hub'] = self.execution_backend_hub
        output_dict['execution_backend_group'] = self.execution_backend_group
        output_dict['execution_backend_project'] = self.execution_backend_project
        output_dict['execution_backend_provider'] = self.execution_backend_provider
        return output_dict

    @staticmethod
    def from_dict(input_dict: Optional[dict]) -> Optional['RunningExperiment']:
        prepared_experiment = PreparedExperiment.from_dict(input_dict)

        running_experiment = RunningExperiment(prepared_experiment, job_list=[])

        running_experiment.execution_backend_name = input_dict.get('execution_backend_name', '')
        running_experiment.execution_backend_provider = input_dict.get('execution_backend_provider', '')
        running_experiment.execution_backend_hub = input_dict.get('execution_backend_hub')
        running_experiment.execution_backend_group = input_dict.get('execution_backend_group')
        running_experiment.execution_backend_project = input_dict.get('execution_backend_project')

        from qiskit.providers.ibmq import IBMQBackend
        backend = running_experiment.execution_backend
        if isinstance(backend, IBMQBackend):
            job_list = [backend.retrieve_job(job_id) for job_id in input_dict.get('job_id_list', [])]
        else:
            LOG.warning(f'A running experiment can only be saved and loaded when using a backend that supports'
                        f'loading from job_ids. This backend {backend} does not support this!')
            job_list = []

        running_experiment.job_list = job_list

        return running_experiment

    def serialize(self) -> bytes:
        import dill
        return dill.dumps(self.to_dict())

    @staticmethod
    def deserialize(b: bytes) -> 'RunningExperiment':
        import dill
        dictionary = dill.loads(b)
        return RunningExperiment.from_dict(dictionary)


class FinishedExperiment(RunningExperiment):
    status_list: List[JobStatus]
    results: List[List[ExperimentResult]]

    def __init__(self, running_experiment: RunningExperiment, status_list: List[JobStatus],
                 results: List[List[ExperimentResult]]):
        super().__init__(prepared_experiment=running_experiment, job_list=running_experiment.job_list,
                         execution_backend=running_experiment.execution_backend)
        self.results = results
        self.status_list = status_list

    def get_prepared_experiment(self):
        return PreparedExperiment(
            self.external_id,
            self.tags,
            self.qobj_list,
            self.arguments,
            self.transpiler_backend,
            self.noise_model,
            self.parameters,
            self.callback
        )

    def get_output(self, meas_fitter: Optional[CompleteMeasFitter] = None) -> np.array:
        return self.callback(self, meas_fitter)

    def to_result(self, qobj_index: int) -> Result:
        # In case we serialized and deserialzed a local job, then the job_id will be there. Create a random new one.
        job_id = self.job_list[qobj_index].job_id() if len(self.job_list) > qobj_index else str(uuid.uuid4())
        backend = self.execution_backend
        return Result(backend_name=backend.name(), backend_version=backend.version,
                      qobj_id=self.qobj_list[qobj_index].qobj_id, job_id=job_id,
                      success=self.status_list[qobj_index] is JobStatus.DONE, results=self.results[qobj_index])

    def to_dict(self) -> dict:
        output_dict = super().to_dict()

        output_dict['results'] = [[e.to_dict() for e in results] for results in self.results]
        output_dict['status_list'] = [status.name for status in self.status_list]

        return output_dict

    @staticmethod
    def from_dict(input_dict: Optional[dict]) -> Optional['FinishedExperiment']:
        if input_dict is None:
            return None

        running_experiment = RunningExperiment.from_dict(input_dict)
        experiment = FinishedExperiment(
            running_experiment=running_experiment,
            status_list=[JobStatus[status] for status in input_dict.get('status_list', [])],
            results=[[ExperimentResult.from_dict(d) for d in results] for results in input_dict.get('results', [])]
        )

        return experiment

    def serialize(self) -> bytes:
        import dill
        return dill.dumps(self.to_dict())

    @staticmethod
    def deserialize(b: bytes) -> 'FinishedExperiment':
        import dill
        dictionary = dill.loads(b)
        return FinishedExperiment.from_dict(dictionary)


class TransientError(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PermanentError(Exception):

    inner_exception: Exception

    def __init__(self, inner_exception, *args: object) -> None:
        super().__init__(inner_exception, *args)
        self.inner_exception = inner_exception


class RepeatAgainError(Exception):

    suggested_delay: int

    def __init__(self, suggested_delay: int, *args: object) -> None:
        super().__init__(suggested_delay, *args)
        self.suggested_delay = suggested_delay