import copy
import json
import importlib
import pandas as pd

############################################
# Pandas add a simple helper function
############################################
def _get_generic_dtype(self, colname):
    d = self.dtypes[colname]
    d = str(d)
    if (d not in ["int64", "float64", "int8", "bool", "category"]) and (
        not d.startswith("datetime")
    ):
        d = "str"
    return d


pd.DataFrame.get_generic_dtype = _get_generic_dtype

############################################
# Subclass to Add Metadata
############################################
class PandasDFWithMetadata(pd.DataFrame):
    """
    Custom subclass of PandasDataFrame to support
    metadata collection.
    """

    _metadata = ["enrich_attrs"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enrich_attrs = {"name": "", "lineage": []}

    @property
    def _constructor(self):
        return PandasDFWithMetadata

    @property
    def lineage(self):
        return self.enrich_attrs.get("lineage", [])

    def set_lineage(self, value):
        self.enrich_attrs["lineage"] = value

    def clear_lineage(self):
        self.enrich_attrs["lineage"] = []

    def derive(self, inputcols, outputcols, inputname=None):
        """
        Note how a new column is derived from an existing
        columns from the same or different dataframe with
        a name
        """

        if isinstance(inputcols, str):
            inputcols = [inputcols]
        if isinstance(outputcols, str):
            outputcols = [outputcols]

        outputname = self.enrich_attrs.get("name", None)

        self.enrich_attrs["lineage"].append(
            {
                "outputname": outputname,
                "inputname": inputname,
                "input": inputcols,
                "output": outputcols,
            }
        )

    def derive_from_map(self, mapping):
        for old, new in mapping.items():
            self.derive([old], [new])

    def get_lineage(self):
        return self.enrich_attrs["lineage"]

    # https://github.com/pandas-dev/pandas/issues/2485
    def _combine_frame(self, other, *args, **kwargs):
        return super()._combine_frame(other, *args, **kwargs).__finalize__(self)

    # Overrides the rename pandas function.
    def rename(self, *args, **kwargs):

        columns = None
        if ("columns" in kwargs) and (isinstance(kwargs["columns"], dict)):
            columns = copy.copy(kwargs["columns"])
        value = super().rename(*args, **kwargs)
        if columns is not None:
            self.derive_from_map(columns)

        return value


spec = importlib.util.find_spec("pyspark")
if spec is not None:
    """
    Handle the case wheen pyspark is not installed on the localmachine
    """
    from pyspark import SparkContext
    from pyspark.sql import Column
    from pyspark.sql.functions import col

    #
    # https://stackoverflow.com/questions/46667810/how-to-update-pyspark-dataframe-metadata-on-spark-2-1
    def withMeta(self, alias, meta):
        """
        Add metadata to spark RDD


         Example::

             # new metadata:
             meta = {"ml_attr": {"name": "label_with_meta",
                                 "type": "nominal",
                                 "vals": [str(x) for x in range(6)]}}

             df_with_meta = df.withColumn("label_with_meta", col("label").withMeta("", meta))

        """
        sc = SparkContext._active_spark_context
        jmeta = sc._gateway.jvm.org.apache.spark.sql.types.Metadata
        return Column(getattr(self._jc, "as")(alias, jmeta.fromJson(json.dumps(meta))))

    Column.withMeta = withMeta
