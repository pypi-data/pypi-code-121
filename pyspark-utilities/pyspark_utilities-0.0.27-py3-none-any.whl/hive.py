from .datastorage import DataStorage
from .utils import get_dataset_property
import os


class Hive(DataStorage):

    # overriding abstract method
    def load_dataset(self, name, read_all=True, input_dest='', header=True):

        input_columns = get_dataset_property(name, "input-columns")

        if input_dest == '':
            input_dataset = get_dataset_property(name)
        else:
            input_dataset = input_dest

        # # To manage supervised algorithms
        # if "labelCol" in self.args:
        #     label_col = self.args["labelCol"]
        #     columns_list = input_columns.split(",")
        #     if label_col not in columns_list:
        #         columns_list.append(label_col)
        #     input_columns = ','.join(columns_list)

        if read_all:
            df = self.spark.sql("SELECT * FROM " + input_dataset)
        else:
            df = self.spark.sql("SELECT " + input_columns + " FROM " + input_dataset)

        # rename column
        for column in input_columns.split(","):
            df = df.withColumnRenamed(column.lower(), column)
        return df

    # overriding abstract method
    def save_dataset(self, name, df, output_dest):

        if output_dest == '':
            output_dataset = get_dataset_property(name)
        else:
            output_dataset = output_dest

        os.environ["HADOOP_USER_NAME"] = get_dataset_property(name, "hiveHadoopUserName")

        database_name = output_dataset.split(".")[0]
        self.spark.sql("CREATE DATABASE IF NOT EXISTS " + database_name)
        df.write.mode("overwrite").saveAsTable(output_dataset)
