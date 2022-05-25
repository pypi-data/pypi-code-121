"""! @brief Skeleton for implementing a specific stage to be used in a DataProc Workflow template."""
import sys
from typing import Any
from json import loads as json_loads

from dsframework.base.batch.stage_base import ZIDS_Stage


##
# @file
# @brief Stage main class, implements ZIDS_Stage base class.
class generatedStageName(ZIDS_Stage):
    """! Stage class

    Implement a stage that will later be converted to an executable job in a specific workflow.
    """

    def __init__(self, stage_config):
        """! The Stage class (generatedStageName) initializer.
        Base class will load basic configuration parameters, additional fields should be added here

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(stage_config)

    def get_stage_name(self):
        """! Get the stage name

            Returns:
                A string, containing the stage's name
        """
        return self.__class__.__name__

    def main(self, **kwargs: Any):
        """! Executes the main functionality of the stage.

            Args:
                **kwargs : Whatever is needed for the stage to run properly.
            Returns:

        """
        raise NotImplementedError


if __name__ == "__main__":
    """! Executes the stage by instantiating it and calling the main function.
    Set up argument condition according to the usage of the written stage
    
        Args:
            System argument 1 - Configuration file
            System argument 2 - Start date, received from Airflow
    """
    if sys.argv and len(sys.argv) > 1:
        config = json_loads(sys.argv[1])
        stage = generatedStageName(config)
        try:
            start_date = sys.argv[2]
            end_date = sys.argv[3]
            params = sys.argv[4]
            stage.update_stage_params(start_date, end_date, params)
            stage.main()
        except Exception as e:
            print(f" Stage failed with error: {e}")
    else:
        print(f"Stage configuration not provided, Can't run stage")


