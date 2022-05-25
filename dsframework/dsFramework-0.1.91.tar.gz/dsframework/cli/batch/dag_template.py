"""! @brief Skeleton for implementing a specific stage to be used in a DataProc Workflow template."""
import sys
from typing import Any
from json import loads as json_loads

from dsframework.base.batch.dag_base import ZIDS_Dag


##
# @file
# @brief Stage main class, implements ZIDS_Stage base class.
class generatedDagName(ZIDS_Dag):
    """! Stage class

    Implement a stage that will later be converted to an executable job in a specific workflow.
    """

    def __init__(self, dag_config):
        """! The Stage class (generatedStageName) initializer.
        Base class will load basic configuration parameters, additional fields should be added here

        Args:
            dag_config : Configuration dictionary, loaded from configuration file.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(dag_config)

    def create_dag(self, **kwargs: Any):
        """! ZIDS_Stage main function.
        This function is the "entrypoint" for the stage, this will run when the job is executed.

            Args:
                **kwargs : Whatever is needed for the stage to run properly.
        """
        raise NotImplementedError


if __name__ == "__main__":
    """! Executes the dag by instantiating it and calling the main function.
    Set up argument condition according to the usage of the written stage
    
        Args:
            System argument 1 - Configuration file
    """
    if sys.argv and len(sys.argv) > 1:
        config = json_loads(sys.argv[1])
        dag = generatedStageName(config)
        dag.create_dag()
    else:
        print(f"project configuration not provided, Can't run dag")
