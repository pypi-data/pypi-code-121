import attr

from airflow.models import DAG
from airflow.models.dagrun import DagRun

from tokyo_lineage.models.base import BaseJob

class JobIdMismatch(Exception):
    pass

@attr.s
class AirflowDag(BaseJob):
    dag: DAG = attr.ib(init=True, default=None)
    dagrun: DagRun = attr.ib(init=True, default=None)

    @dag.validator
    def _check_dag_id(self, attribute, value):
        try:
            assert (value.dag_id == self.job_id)
        except:
            raise JobIdMismatch("Job id != DAG id."
                    "{} != {}".format(self.job_id, value.dag_id))