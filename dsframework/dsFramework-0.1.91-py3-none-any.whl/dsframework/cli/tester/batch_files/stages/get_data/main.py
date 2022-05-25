"""! @brief Get Data stage, for obtaining data from a generic source, such as a database."""
import sys
from typing import Any
from json import loads as json_loads

from dsframework.base.batch.stage_base import ZIDS_Stage


##
# @file
# @brief Stage main class, implements ZIDS_Stage base class.
class GetDataStage(ZIDS_Stage):
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
        print(f"Initializing Stage: {self.get_name()}")
        super().__init__(stage_config)

    def get_name(self):
        """! Get the stage name
        """
        return self.__class__.__name__

    def main(self, **kwargs: Any):
        """! Executes the main functionality of the stage.

            Args:
                **kwargs : Whatever is needed for the stage to run properly.
        """
        spark_session = self.load_spark()
        df = spark_session.read.\
            options(header='true', inferSchema='true').csv(f"gs://{self.bucket_name}/example_data/retail_day.csv")

        df.printSchema()
        df.createOrReplaceTempView("sales")
        highest_price_unit_df = spark_session.sql("select * from sales where UnitPrice >= 3.0")
        # highestPriceUnitDF.write.parquet("gs://us-east1-test-4ba22677-bucket/data/highest_prices.parquet")
        highest_price_unit_df.write.mode("overwrite").parquet(f"{self.bucket_path}"
                                                              f"/example_data/highest_prices_{self.project_id}.parquet")


if __name__ == "__main__":
    """! Executes the stage by instantiating it and calling the main function.
    Set up argument condition according to the usage of the written stage

        Args:
            System argument 1 - Configuration file
            System argument 2 - Start date
    """
    if sys.argv and len(sys.argv) > 1:
        config = json_loads(sys.argv[1])
        stage = GetDataStage(config)
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


