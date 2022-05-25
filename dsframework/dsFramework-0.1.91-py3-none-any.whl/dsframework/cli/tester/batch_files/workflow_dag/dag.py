import os
import sys
import subprocess
from textwrap import dedent

from dsframework.base.batch.dag_base import ZIDS_Dag


class Dag(ZIDS_Dag):
    def __init__(self):
        """! Loads config file and initializes parameters.
        """

        # dag params from airflow 1 - https://airflow.apache.org/docs/apache-airflow/1.10.3/macros.html
        # dag params from airflow 2 - https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
        super().__init__()

        if self.target:
            self.file_name = self.project_name + "_" + self.target + "_dag.py"
        else:
            self.file_name = self.project_name + "_dag.py"

    def create_dag(self):
        """! Dag creation.
        This function creates the python file which contains the DAG itself.
        """

        with open(self.file_name, 'w') as dag_text_file:
            dag_text_file.write(dedent(self.get_basic_dag_code()))
        print(f"DAG file created: {self.file_name}")


if __name__ == "__main__":
    """! Triggers the creation of the workflow dag, which will instantiate a
    workflow template into an actual workflow, executing it.
    Through this module, we can create a dag file which contains instructions, regarding how to execute the 
    workflow template, and we can also import / remove it into / from an active GCP composer (Only for dev mode)
        Args:
            System argument 1 - Action to be performed on a dag (create, import, delete)
    """

    if sys.argv and len(sys.argv) > 1:
        dag_action = sys.argv[1]
    dag = Dag()

    if dag_action == 'create':
        dag.create_dag()

    elif dag_action == 'import':
        dag.import_dag()

    elif dag_action == 'delete':
        dag.delete_dag()
