


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


















