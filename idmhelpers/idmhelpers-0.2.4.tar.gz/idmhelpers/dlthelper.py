# Delta Live Metadata framework
# Using the framework
#
# from idmhelper.dlthelper import TaskBuilder
# TH=TaskBuilder(spark=spark,storage="abfss://container@account.dfs.core.windows.net/im/mylocation")
# # define the pipeline array of tasks
# TaskBuilder.generate(pipeline)
#
import json
try:
    import dlt
except ImportError:
    print('Module missing: dlt.')
    print('1. Run this notebook in a pipeline, dlt is not available outside a pipeline.')
    raise ImportError('idmhelpers requires dlt')

from pyspark.sql.functions import collect_list, struct


def createNestedFrame(df1, name, keycolumns=[], partitionkeys=[]):
    newcolumns = []
    newcolumns.extend(keycolumns)
    newcolumns.append(name)

    # Do not put key joining columns into nested structures
    nonkeycolumns = list(set(df1.columns)-set(keycolumns)-set(partitionkeys))

    df = df1.withColumn(name, struct(nonkeycolumns)).select(newcolumns)
    df = df.groupby(keycolumns).agg(collect_list(name).alias(name))
    return df


class TaskBuilder:

    storage = None
    spark = None

    def __init__(self, spark, storage):
        self.spark = spark
        self.storage = storage

    def generateFromFile(self, pipelineJSONFile, params={}):
        try:
            with open(pipelineJSONFile) as f:
                contentlines = f.readlines()
                pipelineJSON = "\n".join(contentlines)
                self.generateFromJSON(pipelineJSON, params)
        except FileNotFoundError as err:
            raise Exception(
                "Please check path of JSON file. {0}".format(err))

    def generateFromJSON(self, pipelineJSON, params={}):
        try:
            pipeline = json.loads(pipelineJSON)
            for task in pipeline:
                for key, value in task.items():
                    if (type(value) is str) and (value.__contains__("{")):
                        task[key] = value.format(**params)
                self.generateTask(**task)
        except json.decoder.JSONDecodeError as err:
            raise Exception(
                "Please check JSON for syntax error. {0}".format(err))

    def generate(self, pipeline):
        for task in pipeline:
            self.generateTask(**task)

    def generateTask(self, name, sql, type="dlt-view", comment="", temporary=True,
                     nested=None, spark_conf=None, table_properties=None, path=None,
                     partition_cols=None, schema=None, **extraargs):
        kwargs = {}
        # Define a Live Table
        if type == "dlt-table":
            # Create Keyword Args for dlt.table
            if path == None:
                if self.storage != None:
                    path = f'{self.storage}/{name}'
            if path != None:
                kwargs.update({'path': path})
            if schema != None:
                kwargs.update({'schema': schema})
            if spark_conf != None:
                kwargs.update({'spark_conf': spark_conf})
            if table_properties != None:
                kwargs.update({'table_properties': table_properties})
            if partition_cols != None:
                kwargs.update({'partition_cols': partition_cols})
            kwargs.update({'name': name})
            kwargs.update({'comment': f"SQL:{name}:{comment}"})
            kwargs.update({'temporary': temporary})

            @dlt.table(**kwargs)
            def define_dlt_table():
                print(f'Live table: {name} ({comment}) {path})')
                df = self.spark.sql(sql)
                return df
        # Define a Live View
        if type == "dlt-view":
            @dlt.view(
                name=f"{name}",
                comment=f"SQL:{name}:{comment}"
            )
            def define_dlt_table():
                print(f'Live view: {name} ({comment})')
                df = self.spark.sql(sql)
                return df
        # Create a nested table - which folds sale line items into a table with a order,lineitem array.
        if type == "dlt-nest":
            if nested == None:
                raise Exception(
                    f'{name} uses dlt-nest but is missing the nested attribute.')

            @dlt.view(
                name=f"{name}",
                comment=f"SQL:Nested:{name}:{comment}"
            )
            def define_nested_table():
                print(f'Live view: {name} ({comment})')
                df = self.spark.sql(sql)
                df_n = createNestedFrame(
                    df, nested['name'], nested['keycolumns'], nested['partitionkeys'])
                return df_n
