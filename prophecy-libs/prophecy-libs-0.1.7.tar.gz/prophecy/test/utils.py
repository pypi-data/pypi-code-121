from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime
import json


def readResource(path: str) -> str:
    f = open(path, "r")
    content = f.read()
    f.close()
    return content


def defaultForDatatype(type: DataType):
    if isinstance(type, StringType):
        return ""
    elif isinstance(type, IntegerType) or isinstance(type, ShortType) or isinstance(type, LongType):
        return 0
    elif isinstance(type, ByteType):
        return 0
    elif isinstance(type, FloatType) or isinstance(type, DoubleType):
        return 0.0
    elif isinstance(type, BinaryType):
        return bytearray(0)
    elif isinstance(type, BooleanType):
        return False
    elif isinstance(type, DateType):
        return datetime.now()
    elif isinstance(type, TimestampType):
        return datetime.now()
    elif isinstance(type, DecimalType):
        return DecimalType(0)
    else:
        raise Exception(f"default value for datatype: {type} not found")


def defaultsForSchema(schema: StructType):
    pairs = list(map(lambda f: (f.name, defaultForDatatype(f.dataType)), schema.fields))
    return dict(pairs)


def convertStringValueToDatatype(dataType: DataType, value: str):
    if isinstance(dataType, StringType):
        newValue = value
    elif isinstance(dataType, IntegerType) or isinstance(dataType, ShortType) or isinstance(dataType, LongType):
        newValue = 0 if (value == "" or value == "null") else int(value)
    elif isinstance(dataType, ByteType):
        newValue = 0 if (value == "" or value == "null") else str.encode(value)
    elif isinstance(dataType, FloatType) or isinstance(dataType, DoubleType):
        newValue = 0.0 if (value == "" or value == "null") else float(value)
    elif isinstance(dataType, BinaryType):
        newValue = bytearray(0) if (value == "" or value == "null") else bytearray(value)
    elif isinstance(dataType, BooleanType):
        newValue = False if (value == "" or value == "null") else value == "true"
    elif isinstance(dataType, DateType):
        newValue = datetime.now() if (value == "" or value == "null") else datetime.strptime(value, '%Y-%m-%d')
    elif isinstance(dataType, TimestampType):
        newValue = datetime.now() if (value == "" or value == "null") else datetime.strptime(value, '%y-%m-%d %H:%M:%S')
    elif isinstance(dataType, DecimalType):
        newValue = DecimalType(0) if (value == "" or value == "null") else float(value)
    else:
        raise Exception("unexpected data type", dataType)
    return newValue


def createDF(spark, columns, values, schema, typeMap, port) -> DataFrame:
    defaults = defaultsForSchema(schema)
    missingColumns = list(set(defaults.keys()) - set(columns))
    allColumns = columns + missingColumns
    missingValues = list(map(lambda c: defaults[c.lower()], missingColumns))
    allValues = list(map(lambda row: row + missingValues, values))

    reorderedSchema = StructType(list(map(lambda column: StructField(column, typeMap[column]), allColumns)))
    df = spark.createDataFrame(allValues, reorderedSchema)
    return df


def createDfFromResourceFiles(spark: SparkSession, schemaDefinitionPath: str, dataPath: str, port: str) -> DataFrame:
    schemaJson = json.loads(readResource(schemaDefinitionPath))
    schema = StructType.fromJson(schemaJson)

    colDataMap = {}
    for col in schema:
        colDataMap[col.name.lower()] = col.dataType

    data = json.loads(readResource(dataPath))
    cols = []
    for col in data["columns"]:
        cols.append(col.lower())

    values = []
    for row in data["values"]:
        newRow = []
        for (value, colName) in zip(row, cols):
            type = colDataMap[colName]
            newValue = convertStringValueToDatatype(type, value)
            newRow.append(newValue)
        values.append(newRow)

    # dataSchema = StructType(list(filter(lambda c: c.name.lower() in cols, schema.fields)))
    return createDF(spark, cols, values, schema, colDataMap, port)


def rowEquals(r1, r2):
    if len(r1) != len(r2):
        return False

    for i in range(len(r1)):
        if r1[i] != r2[i]:
            return False

    return True


def postProcess(origDf: DataFrame) -> DataFrame:
    df = origDf.na.fill("null")
    return df.sql_ctx.createDataFrame(df.rdd, df.schema)


def assertDFEquals(expectedUnsorted: DataFrame, resultUnsorted: DataFrame, maxUnequalRowsToShow: int) -> str:
    def _sort(df: DataFrame):
        if len(df.columns) == 0:
            return df
        return df.sort(*[col(x) for x in df.columns])

    def fetchTypes(df: DataFrame):
        return [(f.name, f.dataType) for f in df.schema.fields]

    def _assertEqualsTypes(dfExpected: DataFrame, dfActual: DataFrame):
        expectedTypes = fetchTypes(dfExpected)
        actualTypes = fetchTypes(dfActual)
        if expectedTypes != actualTypes:
            raise Exception("Types NOT equal! " + str(expectedTypes) + " != " + str(actualTypes))

    def _assertEqualsCount(dfExpected: DataFrame, dfActual: DataFrame):
        dfExpectedCount = dfExpected.rdd.count()
        dfActualCount = dfActual.rdd.count()
        if dfExpectedCount != dfActualCount:
            raise Exception(f"Length not Equal.\n{str(dfExpectedCount)} vs {dfActualCount}")

    def _assertEqualsValues(dfExpected: DataFrame, dfActual: DataFrame):
        expectedVal = dfExpected.rdd.zipWithIndex().map(lambda x: (x[1], x[0]))
        resultVal = dfActual.rdd.zipWithIndex().map(lambda x: (x[1], x[0]))

        joined = expectedVal.join(resultVal)
        unequalRDD = joined.filter(lambda x: (not rowEquals(x[1][0], x[1][1])))

        if len(unequalRDD.take(maxUnequalRowsToShow)) != 0:
            raise Exception("Expected != Actual\nMismatch: " + str(unequalRDD.take(maxUnequalRowsToShow)))

    expected = _sort(postProcess(expectedUnsorted))
    result = _sort(postProcess(resultUnsorted))

    try:
        expected.rdd.cache()
        result.rdd.cache()

        # assert equality by means of count, types and data
        _assertEqualsCount(expected, result)
        _assertEqualsTypes(expected, result)
        _assertEqualsValues(expected, result)
    except:
        raise Exception("Dataframe match error")
    finally:
        expected.rdd.unpersist()
        result.rdd.unpersist()


def assertPredicates(port: str, df: DataFrame, predicates):
    for (pred, name) in predicates:
        if df.filter(pred).count() != df.count():
            raise Exception(f"Predicate {name} [[`{pred}`]] not universally true for port {port}")


def readData(spark: SparkSession, schema: StructType, path: str) -> DataFrame:
    jsonData = json.loads(readResource(path))
    colDataMap = {}
    for col in schema:
        colDataMap[col.name] = col.dataType
    data = []
    for row in jsonData:
        newRow = []
        for idx, element in enumerate(row):
            newElement = convertStringValueToDatatype(schema.fields[idx].dataType, element)
            newRow.append(newElement)
        data.append(newRow)
    df = spark.createDataFrame(data, schema)
    df.show()
    return df


def writeData(pathPrefix: str, fileName: str, df: DataFrame, separator: str, maxRows: int = 100):
    from pathlib import Path
    Path(pathPrefix).mkdir(parents=True, exist_ok=True)
    file = open(f"{pathPrefix}/{fileName}", "w")
    headers = separator.join(df.schema.fieldNames()) + "\n"
    for row in df.rdd.collect():
        print(row)
    fields = "\n".join(list(map(lambda row: separator.join(list(map(str, row))), df.take(maxRows))))
    content = headers + fields
    file.write(content)
    file.close()

