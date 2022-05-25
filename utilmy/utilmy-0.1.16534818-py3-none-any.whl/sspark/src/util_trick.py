
"""

https://gist.github.com/search?p=4&q=pyspark+UDF


"""

def pyudf():
    Different_ways_of_UDF
    1. Standalone function:

    def _add_one(x):
        """Adds one"""
        if x is not None:
            return x + 1
            
    add_one = udf(_add_one, IntegerType())

    Importance: This allows for full control flow, including exception handling, but duplicates variables.

    2. lambda expression:
    =====================
    add_one = udf(lambda x: x + 1 if x is not None else None, IntegerType())

    Importance: No variable duplication but only pure expressions.

    3. Using nested functions:
    ==========================
    def add_one(c):
        def add_one_(x):
            if x is not None:
                return x + 1
        return udf(add_one_, IntegerType())(c)
        
    Importance : Quite verbose but enables full control flow and clearly indicates expected number of arguments.

    4. Using decorator:
    ===================
    @udf
    def add_one(x):
        """Adds one"""
        if x is not None:
            return x + 1
            
    functions_usage
    Step 1: Define functions:
    ==========================
    from pyspark.sql.functions import lit
    def with_greeting(df):
        return df.withColumn("greeting", lit("hi"))

    def with_something(df, something):
        return df.withColumn("something", lit(something))
        
    #Create Dataframe and use the above functions
    data = [("jose", 1), ("li", 2), ("liz", 3)]
    source_df = spark.createDataFrame(data, ["name", "age"])
    df1 = with_greeting(source_df)
    actual_df = with_something(df1, "moo")

    # Creating multiple variables gets especially ugly when 5+ transformations need to be run — you don’t want df1, df2, df3, df4, and df5

    Use Monkey patch and chain the functions:
    =========================================
    1. Customize dataframe's transform method

    from pyspark.sql.dataframe import DataFrame
    def transform(self, f):
        return f(self)
    DataFrame.transform = transform

    actual_df = (source_df
        .transform(lambda df: with_greeting(df))
        .transform(lambda df: with_something(df, "crazy")))
        
    print(actual_df.show())

    +----+---+--------+---------+
    |name|age|greeting|something|
    +----+---+--------+---------+
    |jose|  1|      hi|    crazy|
    |  li|  2|      hi|    crazy|
    | liz|  3|      hi|    crazy|
    +----+---+--------+---------+
    Using functools.partial:
    =======================
    def with_asset(word, df):
        return df.withColumn("asset", lit(word)) 
        
    from functools import partial
    actual_df = (source_df
    .transform(with_greeting)
    .transform(partial(with_asset, "stocks")))
    print(actual_df.show())


    
    pyspark_UDFs
    import pyspark
    from pyspark.sql import SparkSession
    import pandas as pd
    from pyspark.sql.functions import udf
    spark = SparkSession.builder.getOrCreate()

    df_pd = pd.DataFrame(
        data={'integers': [1, 2, 3], 
        'floats': [-1.0, 0.5, 2.7],
        'integer_arrays': [[1, 2], [3, 4, 5], [6, 7, 8, 9]]}
    )

    df = spark.createDataFrame(df_pd)
    # Declare function
    def square(x):
        return x**2
    # Registering UDF with integer type output
    from pyspark.sql.types import IntegerType
    square_udf_int = udf(lambda z: square(z), IntegerType())    
    df.select('integers',
                'floats',
                square_udf_int('integers').alias('int_squared')).show()
    # float type output
    from pyspark.sql.types import FloatType
    square_udf_float = udf(lambda z: square(z), FloatType())
    df.select('integers', 
                'floats', 
                square_udf_float('integers').alias('int_squared'), 
                square_udf_float('floats').alias('float_squared')).show()

    ## Force the output to be float
    def square_float(x):
        return float(x**2)
    square_udf_float2 = udf(lambda z: square_float(z), FloatType())

    Composite UDF:
    ===============
    def square_list(x):
        return [float(val)**2 for val in x]
    from pyspark.sql.types import ArrayType
    square_list_udf = udf(lambda y: square_list(y), ArrayType(FloatType()))
    df.select('integer_arrays', square_list_udf('integer_arrays')).show()


    Using Struct Type:
    ==================
    from pyspark.sql.types import StructType, StructField, StringType
    array_schema = StructType([
        StructField('number', IntegerType(), nullable=False),
        StructField('letters', StringType(), nullable=False)
    ])

    import string
    def convert_ascii(number):
        return [number, string.ascii_letters[number]]
    convert_ascii(1) # validate functions
    spark_convert_ascii = udf(lambda z: convert_ascii(z), array_schema)
    df_ascii = df.select('integers', spark_convert_ascii('integers').alias('ascii_map'))
    df_ascii.show()










def info1():
    from pyspark.sql.functions import countDistinct, avg, stddev
    from pyspark.sql.functions import format_number
    # aggregations
    df.select(countDistinct("Sales")).show()
    df.select(avg("Sales").alias("avgSales")).show()
    df.orderBy("Sales").show()
    df.orderBy("Company").show()
    df.orderBy(df["Sales"].desc()).show()

    sales_std = df.select(stddev("Sales").alias("Sales Std"))
    sales_std.select(format_number("Sales Std",2).alias("Sales Std")).show()

    # datetime 
    from pyspark.sql.functions import dayofmonth,dayofyear,weekofyear,date_format
    from pyspark.sql.functions import month,year
    from pyspark.sql.functions import hour,minute,format_number
    df.select(dayofmonth(df["Date"])).show()
    df.select(year(df["Date"])).show()

    # Row format
    from pyspark.sql import Row
    from pyspark.sql.types import *
    from pyspark.sql.functions import *
    df = rdd.map(lambda line: Row(longitude=line[0], 
                                  latitude=line[1], 
                                  housingMedianAge=line[2],
                                  totalRooms=line[3],
                                  totalBedRooms=line[4],
                                  population=line[5], 
                                  households=line[6],
                                  medianIncome=line[7],
                                  medianHouseValue=line[8])).toDF()

    df = df.select("medianHouseValue", "totalBedRooms", "population") 
    df = df.withColumn("roomsPerHousehold", col("totalRooms")/col("households"))
    df = df.withColumn("medianHouseValue",  col("medianHouseValue")/100000)
    df = df.withColumn( "longitude", df["longitude"].cast(FloatType()) ) 
          .withColumn( "latitude",  df["latitude"].cast(FloatType())  ) 
    df.select(col("population")/col("households"))
    df.select('population','totalBedRooms').show(10)
    df.describe().show()

    # aggregations
    df.groupBy("housingMedianAge").count().sort("housingMedianAge",ascending=False).show()

    
    # udf functions
    def convertColumn(df, names, newType):
      for name in names: 
        df = df.withColumn(name, df[name].cast(newType))
      return df 

    columns = ['households', 'housingMedianAge', 'latitude', 'longitude', 
              'medianHouseValue', 'medianIncome', 'population', 'totalBedRooms', 'totalRooms']
    df = convertColumn(df, columns, FloatType())


    # udf functions
    from pyspark.sql.functions import *
    get_domain = udf(lambda x: re.search("@([^@]*)", x = "@").group(1))
    df.select(get_domain(df.commiteremail).alias("domain"))
      .groupBy("domain").count()
      .orderBy(desc("count")).take(5)

    # efficient joins
    myUDF = udf(lambda x,y: x == y)
    df1.join(df2, myUDF(col("x"), col("y")) )




def info2():
    # experiment with processing complex objects (arrays) in pyspark
    import os
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as f
    from pyspark.sql.types import *
    import pandas as pd
    from time import perf_counter
    # get a spark session
    spark = SparkSession.builder.appName('learn').getOrCreate()
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as f
    from pyspark.sql.types import *
    spark = SparkSession.builder.enableHiveSupport().appName('learn').getOrCreate()
    data = [('a', 1, [1, 3, 5]),
            ('b', 2, [4, 6, 9]),
            ('c', 3, [50, 60, 70, 80])]
    df = spark.createDataFrame(data, ['nam', 'q', 'compl'])

    # process complex object, method 1 using explode and collect_list (dataframe API)
    res = df.withColumn('id', f.monotonically_increasing_id()).withColumn('compl_exploded', f.explode(f.col('compl')))
    res = res.withColumn('compl_exploded', f.col('compl_exploded')+1)
    res = res.groupby('id').agg(f.first('nam'), f.first('q'), f.collect_list('compl_exploded').alias('compl')).drop('id')
    res.show()

    # process complex object, method 2 using explode and collect_list (SQL)
    df.withColumn('id', f.monotonically_increasing_id()).createOrReplaceTempView('tmp_view')
    res = spark.sql("""
    SELECT first(nam) AS nam, first(q) AS q, collect_list(compl_exploded+1) AS compl FROM (
        SELECT *, explode(compl) AS compl_exploded FROM tmp_view
        ) x
        GROUP BY id
    """)
    res.show()

    # process complex object, method 3 using python UDF
    from typing import List
    def process(x: List[int]) -> List[int]:
        return [_+1 for _ in x]
    process_udf = f.udf(process, ArrayType(LongType()))
    res = df.withColumn('compl', process_udf('compl'))
    res.show()

    # method 4, using the higher order function transform (dataframe API)
    res = df.withColumn('compl', f.transform('compl', lambda x: x+1))
    res.show()

    # method 5, using the higher order function transform (SQL)
    res = df.withColumn('compl', f.expr("transform(compl, t -> t + 1)"))
    res.show()

















##### Muticlass prediciton
@F.pandas_udf(returnType=ArrayType(DoubleType()))
def predict_pandas_udf(*cols):
    X = pd.concat(cols, axis=1)
    return pd.Series(row.tolist() for row in gs_rf.predict_proba(X))

df_pred_multi = (
    df_unlabeled.select(
        F.col('id'),
        predict_pandas_udf(*column_names).alias('predictions')
    )
    # Select each item of the prediction array into its own column.
    .select(
        F.col('id'),
        *[F.col('predictions')[i].alias(f'prediction_{c}')
          for i, c in enumerate(gs_rf.classes_)]
    )
)
df_pred_multi.take(5)


















