"""Hadoop, hive related.
Doc:

    sspark  spark_config_check

    HDFS command
    cat: Copies source paths to stdout.
    Usage: hdfs dfs -cat URI [URI ?]

    Example:
        hdfs dfs -cat hdfs://<path>/file1
        hdfs dfs -cat file:///file2 /user/hadoop/file3

    chgrp: Changes the group association of files. With -R, makes the change recursively by way of the directory structure. The user must be the file owner or the superuser.
    Usage: hdfs dfs -chgrp [-R] GROUP URI [URI ?]

    chmod: Changes the permissions of files. With -R, makes the change recursively by way of the directory structure. The user must be the file owner or the superuser
    Usage: hdfs dfs -chmod [-R] <MODE[,MODE]? | OCTALMODE> URI [URI ?]
    Example: hdfs dfs -chmod 777 test/data1.txt

    chown: Changes the owner of files. With -R, makes the change recursively by way of the directory structure. The user must be the superuser.
    Usage: hdfs dfs -chown [-R] [OWNER][:[GROUP]] URI [URI ]
    Example: hdfs dfs -chown -R hduser2 /opt/hadoop/logs

    copyFromLocal: Works similarly to the put command, except that the source is restricted to a local file reference.
    Usage: hdfs dfs -copyFromLocal <localsrc> URI
    Example: hdfs dfs -copyFromLocal input/docs/data2.txt hdfs://localhost/user/rosemary/data2.txt

    copyToLocal: Works similarly to the get command, except that the destination is restricted to a local file reference.
    Usage: hdfs dfs -copyToLocal [-ignorecrc] [-crc] URI <localdst>
    Example: hdfs dfs -copyToLocal data2.txt data2.copy.txt

    count: Counts the number of directories, files, and bytes under the paths that match the specified file pattern.
    Usage: hdfs dfs -count [-q] <paths>
    Example: hdfs dfs -count hdfs://nn1.example.com/file1 hdfs://nn2.example.com/file2

    cp: Copies one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory.
    Usage: hdfs dfs -cp URI [URI ?] <dest>
    Example: hdfs dfs -cp /user/hadoop/file1 /user/hadoop/file2 /user/hadoop/dir

    du: Displays the size of the specified file, or the sizes of files and directories that are contained in the specified directory. If you specify the -s option, displays an aggregate summary of file sizes rather than individual file sizes. If you specify the -h option, formats the file sizes in a �ghuman-readable�h way.
    Usage: hdfs dfs -du [-s] [-h] URI [URI ?]
    Example: hdfs dfs -du /user/hadoop/dir1 /user/hadoop/file1

    dus: Displays a summary of file sizes; equivalent to hdfs dfs -du ?s.
    Usage: hdfs dfs -dus <args>

    expunge: Empties the trash. When you delete a file, it isn�ft removed immediately from HDFS, but is renamed to a file in the /trash directory. As long as the file remains there, you can undelete it if you change your mind, though only the latest copy of the deleted file can be restored.
    Usage: hdfs dfs ?expunge

    get: Copies files to the local file system. Files that fail a cyclic redundancy check (CRC) can still be copied if you specify the ?ignorecrc option. The CRC is a common technique for detecting data transmission errors. CRC checksum files have the .crc extension and are used to verify the data integrity of another file. These files are copied if you specify the -crc option.
    Usage: hdfs dfs -get [-ignorecrc] [-crc] <src> <localdst>
    Example: hdfs dfs -get /user/hadoop/file3 localfile

    getmerge: Concatenates the files in src and writes the result to the specified local destination file. To add a newline character at the end of each file, specify the addnl option.
    Usage: hdfs dfs -getmerge <src> <localdst> [addnl]
    Example: hdfs dfs -getmerge /user/hadoop/mydir/ ~/result_file addnl

    ls: Returns statistics for the specified files or directories.
    Usage: hdfs dfs -ls <args>
    Example: hdfs dfs -ls /user/hadoop/file1

    lsr: Serves as the recursive version of ls; similar to the Unix command ls -R.
    Usage: hdfs dfs -lsr <args>
    Example: hdfs dfs -lsr /user/hadoop

    mkdir: Creates directories on one or more specified paths. Its behavior is similar to the Unix mkdir -p command, which creates all directories that lead up to the specified directory if they don�ft exist already.
    Usage: hdfs dfs -mkdir <paths>
    Example: hdfs dfs -mkdir /user/hadoop/dir5/temp

    moveFromLocal: Works similarly to the put command, except that the source is deleted after it is copied.
    Usage: hdfs dfs -moveFromLocal <localsrc> <dest>
    Example: hdfs dfs -moveFromLocal localfile1 localfile2 /user/hadoop/hadoopdir

    mv: Moves one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory. Moving files across file systems isn�ft permitted.
    Usage: hdfs dfs -mv URI [URI ?] <dest>
    Example: hdfs dfs -mv /user/hadoop/file1 /user/hadoop/file2

    put: Copies files from the local file system to the destination file system. This command can also read input from stdin and write to the destination file system.
    Usage: hdfs dfs -put <localsrc> ? <dest>
    Example: hdfs dfs -put localfile1 localfile2 /user/hadoop/hadoopdir; hdfs dfs -put ? /user/hadoop/hadoopdir (reads input from stdin)


    rm: Deletes one or more specified files. This command doesn�ft delete empty directories or files. To bypass the trash (if it�fs enabled) and delete the specified files immediately, specify the -skipTrash option.
    Usage: hdfs dfs -rm [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rm hdfs://nn.example.com/file9
    
    rmr: Serves as the recursive version of ?rm.
    Usage: hdfs dfs -rmr [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rmr /user/hadoop/dir

    setrep: Changes the replication factor for a specified file or directory. With ?R, makes the change recursively by way of the directory structure.
    Usage: hdfs dfs -setrep <rep> [-R] <path>

    Example: hdfs dfs -setrep 3 -R /user/hadoop/dir1
    stat: Displays information about the specified path.

    Usage: hdfs dfs -stat URI [URI ?]
    Example: hdfs dfs -stat /user/hadoop/dir1
    tail: Displays the last kilobyte of a specified file to stdout. The syntax supports the Unix -f option, which enables the specified file to be monitored. As new lines are added to the file by another process, tail updates the display.

    Usage: hdfs dfs -tail [-f] URI
    Example: hdfs dfs -tail /user/hadoop/dir1

    test: Returns attributes of the specified file or directory. Specifies ?e to determine whether the file or directory exists; -z to determine whether the file or directory is empty; and -d to determine whether the URI is a directory.
    Usage: hdfs dfs -test -[ezd] URI
    Example: hdfs dfs -test /user/hadoop/dir1

    text: Outputs a specified source file in text format. Valid input file formats are zip and TextRecordInputStream.
    Usage: hdfs dfs -text <src>
    Example: hdfs dfs -text /user/hadoop/file8.zip  

    touchz: Creates a new, empty file of size 0 in the specified path.
    Usage: hdfs dfs -touchz <path>
    Example: hdfs dfs -touchz /user/hadoop/file12  

"""
import os,sys, subprocess
import pandas as pd


def log(*s):
  print(*s, flush=True)




def aa_spark_docs():
   """ Spark SQL API
   Doc::

        Core Classes
        SparkSession(sparkContext[, jsparkSession])

        The entry point to programming Spark with the Dataset and DataFrame API.

        Catalog(sparkSession)

        User-facing catalog API, accessible through SparkSession.catalog.

        DataFrame(jdf, sql_ctx)

        A distributed collection of data grouped into named columns.

        Column(jc)

        A column in a DataFrame.

        Row

        A row in DataFrame.

        GroupedData(jgd, df)

        A set of methods for aggregations on a DataFrame, created by DataFrame.groupBy().

        PandasCogroupedOps(gd1, gd2)

        A logical grouping of two GroupedData, created by GroupedData.cogroup().

        DataFrameNaFunctions(df)

        Functionality for working with missing data in DataFrame.

        DataFrameStatFunctions(df)

        Functionality for statistic functions with DataFrame.

        Window

        Utility functions for defining window in DataFrames.

        Spark Session APIs
        The entry point to programming Spark with the Dataset and DataFrame API. To create a Spark session, you should use SparkSession.builder attribute. See also SparkSession.

        SparkSession.builder.appName(name)

        Sets a name for the application, which will be shown in the Spark web UI.

        SparkSession.builder.config([key, value, conf])

        Sets a config option.

        SparkSession.builder.enableHiveSupport()

        Enables Hive support, including connectivity to a persistent Hive metastore, support for Hive SerDes, and Hive user-defined functions.

        SparkSession.builder.getOrCreate()

        Gets an existing SparkSession or, if there is no existing one, creates a new one based on the options set in this builder.

        SparkSession.builder.master(master)

        Sets the Spark master URL to connect to, such as “local” to run locally, “local[4]” to run locally with 4 cores, or “spark://master:7077” to run on a Spark standalone cluster.

        SparkSession.catalog

        Interface through which the user may create, drop, alter or query underlying databases, tables, functions, etc.

        SparkSession.conf

        Runtime configuration interface for Spark.

        SparkSession.createDataFrame(data[, schema, …])

        Creates a DataFrame from an RDD, a list or a pandas.DataFrame.

        SparkSession.getActiveSession()

        Returns the active SparkSession for the current thread, returned by the builder

        SparkSession.newSession()

        Returns a new SparkSession as new session, that has separate SQLConf, registered temporary views and UDFs, but shared SparkContext and table cache.

        SparkSession.range(start[, end, step, …])

        Create a DataFrame with single pyspark.sql.types.LongType column named id, containing elements in a range from start to end (exclusive) with step value step.

        SparkSession.read

        Returns a DataFrameReader that can be used to read data in as a DataFrame.

        SparkSession.readStream

        Returns a DataStreamReader that can be used to read data streams as a streaming DataFrame.

        SparkSession.sparkContext

        Returns the underlying SparkContext.

        SparkSession.sql(sqlQuery)

        Returns a DataFrame representing the result of the given query.

        SparkSession.stop()

        Stop the underlying SparkContext.

        SparkSession.streams

        Returns a StreamingQueryManager that allows managing all the StreamingQuery instances active on this context.

        SparkSession.table(tableName)

        Returns the specified table as a DataFrame.

        SparkSession.udf

        Returns a UDFRegistration for UDF registration.

        SparkSession.version

        The version of Spark on which this application is running.

        Configuration
        RuntimeConfig(jconf)

        User-facing configuration API, accessible through SparkSession.conf.

        Input and Output
        DataFrameReader.csv(path[, schema, sep, …])

        Loads a CSV file and returns the result as a DataFrame.

        DataFrameReader.format(source)

        Specifies the input data source format.

        DataFrameReader.jdbc(url, table[, column, …])

        Construct a DataFrame representing the database table named table accessible via JDBC URL url and connection properties.

        DataFrameReader.json(path[, schema, …])

        Loads JSON files and returns the results as a DataFrame.

        DataFrameReader.load([path, format, schema])

        Loads data from a data source and returns it as a DataFrame.

        DataFrameReader.option(key, value)

        Adds an input option for the underlying data source.

        DataFrameReader.options(**options)

        Adds input options for the underlying data source.

        DataFrameReader.orc(path[, mergeSchema, …])

        Loads ORC files, returning the result as a DataFrame.

        DataFrameReader.parquet(*paths, **options)

        Loads Parquet files, returning the result as a DataFrame.

        DataFrameReader.schema(schema)

        Specifies the input schema.

        DataFrameReader.table(tableName)

        Returns the specified table as a DataFrame.

        DataFrameWriter.bucketBy(numBuckets, col, *cols)

        Buckets the output by the given columns.

        DataFrameWriter.csv(path[, mode, …])

        Saves the content of the DataFrame in CSV format at the specified path.

        DataFrameWriter.format(source)

        Specifies the underlying output data source.

        DataFrameWriter.insertInto(tableName[, …])

        Inserts the content of the DataFrame to the specified table.

        DataFrameWriter.jdbc(url, table[, mode, …])

        Saves the content of the DataFrame to an external database table via JDBC.

        DataFrameWriter.json(path[, mode, …])

        Saves the content of the DataFrame in JSON format (JSON Lines text format or newline-delimited JSON) at the specified path.

        DataFrameWriter.mode(saveMode)

        Specifies the behavior when data or table already exists.

        DataFrameWriter.option(key, value)

        Adds an output option for the underlying data source.

        DataFrameWriter.options(**options)

        Adds output options for the underlying data source.

        DataFrameWriter.orc(path[, mode, …])

        Saves the content of the DataFrame in ORC format at the specified path.

        DataFrameWriter.parquet(path[, mode, …])

        Saves the content of the DataFrame in Parquet format at the specified path.

        DataFrameWriter.partitionBy(*cols)

        Partitions the output by the given columns on the file system.

        DataFrameWriter.save([path, format, mode, …])

        Saves the contents of the DataFrame to a data source.

        DataFrameWriter.saveAsTable(name[, format, …])

        Saves the content of the DataFrame as the specified table.

        DataFrameWriter.sortBy(col, *cols)

        Sorts the output in each bucket by the given columns on the file system.

        DataFrameWriter.text(path[, compression, …])

        Saves the content of the DataFrame in a text file at the specified path.

        DataFrame APIs
        DataFrame.agg(*exprs)

        Aggregate on the entire DataFrame without groups (shorthand for df.groupBy().agg()).

        DataFrame.alias(alias)

        Returns a new DataFrame with an alias set.

        DataFrame.approxQuantile(col, probabilities, …)

        Calculates the approximate quantiles of numerical columns of a DataFrame.

        DataFrame.cache()

        Persists the DataFrame with the default storage level (MEMORY_AND_DISK).

        DataFrame.checkpoint([eager])

        Returns a checkpointed version of this DataFrame.

        DataFrame.coalesce(numPartitions)

        Returns a new DataFrame that has exactly numPartitions partitions.

        DataFrame.colRegex(colName)

        Selects column based on the column name specified as a regex and returns it as Column.

        DataFrame.collect()

        Returns all the records as a list of Row.

        DataFrame.columns

        Returns all column names as a list.

        DataFrame.corr(col1, col2[, method])

        Calculates the correlation of two columns of a DataFrame as a double value.

        DataFrame.count()

        Returns the number of rows in this DataFrame.

        DataFrame.cov(col1, col2)

        Calculate the sample covariance for the given columns, specified by their names, as a double value.

        DataFrame.createGlobalTempView(name)

        Creates a global temporary view with this DataFrame.

        DataFrame.createOrReplaceGlobalTempView(name)

        Creates or replaces a global temporary view using the given name.

        DataFrame.createOrReplaceTempView(name)

        Creates or replaces a local temporary view with this DataFrame.

        DataFrame.createTempView(name)

        Creates a local temporary view with this DataFrame.

        DataFrame.crossJoin(other)

        Returns the cartesian product with another DataFrame.

        DataFrame.crosstab(col1, col2)

        Computes a pair-wise frequency table of the given columns.

        DataFrame.cube(*cols)

        Create a multi-dimensional cube for the current DataFrame using the specified columns, so we can run aggregations on them.

        DataFrame.describe(*cols)

        Computes basic statistics for numeric and string columns.

        DataFrame.distinct()

        Returns a new DataFrame containing the distinct rows in this DataFrame.

        DataFrame.drop(*cols)

        Returns a new DataFrame that drops the specified column.

        DataFrame.dropDuplicates([subset])

        Return a new DataFrame with duplicate rows removed, optionally only considering certain columns.

        DataFrame.drop_duplicates([subset])

        drop_duplicates() is an alias for dropDuplicates().

        DataFrame.dropna([how, thresh, subset])

        Returns a new DataFrame omitting rows with null values.

        DataFrame.dtypes

        Returns all column names and their data types as a list.

        DataFrame.exceptAll(other)

        Return a new DataFrame containing rows in this DataFrame but not in another DataFrame while preserving duplicates.

        DataFrame.explain([extended, mode])

        Prints the (logical and physical) plans to the console for debugging purpose.

        DataFrame.fillna(value[, subset])

        Replace null values, alias for na.fill().

        DataFrame.filter(condition)

        Filters rows using the given condition.

        DataFrame.first()

        Returns the first row as a Row.

        DataFrame.foreach(f)

        Applies the f function to all Row of this DataFrame.

        DataFrame.foreachPartition(f)

        Applies the f function to each partition of this DataFrame.

        DataFrame.freqItems(cols[, support])

        Finding frequent items for columns, possibly with false positives.

        DataFrame.groupBy(*cols)

        Groups the DataFrame using the specified columns, so we can run aggregation on them.

        DataFrame.head([n])

        Returns the first n rows.

        DataFrame.hint(name, *parameters)

        Specifies some hint on the current DataFrame.

        DataFrame.inputFiles()

        Returns a best-effort snapshot of the files that compose this DataFrame.

        DataFrame.intersect(other)

        Return a new DataFrame containing rows only in both this DataFrame and another DataFrame.

        DataFrame.intersectAll(other)

        Return a new DataFrame containing rows in both this DataFrame and another DataFrame while preserving duplicates.

        DataFrame.isLocal()

        Returns True if the collect() and take() methods can be run locally (without any Spark executors).

        DataFrame.isStreaming

        Returns True if this DataFrame contains one or more sources that continuously return data as it arrives.

        DataFrame.join(other[, on, how])

        Joins with another DataFrame, using the given join expression.

        DataFrame.limit(num)

        Limits the result count to the number specified.

        DataFrame.localCheckpoint([eager])

        Returns a locally checkpointed version of this DataFrame.

        DataFrame.mapInPandas(func, schema)

        Maps an iterator of batches in the current DataFrame using a Python native function that takes and outputs a pandas DataFrame, and returns the result as a DataFrame.

        DataFrame.na

        Returns a DataFrameNaFunctions for handling missing values.

        DataFrame.orderBy(*cols, **kwargs)

        Returns a new DataFrame sorted by the specified column(s).

        DataFrame.persist([storageLevel])

        Sets the storage level to persist the contents of the DataFrame across operations after the first time it is computed.

        DataFrame.printSchema()

        Prints out the schema in the tree format.

        DataFrame.randomSplit(weights[, seed])

        Randomly splits this DataFrame with the provided weights.

        DataFrame.rdd

        Returns the content as an pyspark.RDD of Row.

        DataFrame.registerTempTable(name)

        Registers this DataFrame as a temporary table using the given name.

        DataFrame.repartition(numPartitions, *cols)

        Returns a new DataFrame partitioned by the given partitioning expressions.

        DataFrame.repartitionByRange(numPartitions, …)

        Returns a new DataFrame partitioned by the given partitioning expressions.

        DataFrame.replace(to_replace[, value, subset])

        Returns a new DataFrame replacing a value with another value.

        DataFrame.rollup(*cols)

        Create a multi-dimensional rollup for the current DataFrame using the specified columns, so we can run aggregation on them.

        DataFrame.sameSemantics(other)

        Returns True when the logical query plans inside both DataFrames are equal and therefore return same results.

        DataFrame.sample([withReplacement, …])

        Returns a sampled subset of this DataFrame.

        DataFrame.sampleBy(col, fractions[, seed])

        Returns a stratified sample without replacement based on the fraction given on each stratum.

        DataFrame.schema

        Returns the schema of this DataFrame as a pyspark.sql.types.StructType.

        DataFrame.select(*cols)

        Projects a set of expressions and returns a new DataFrame.

        DataFrame.selectExpr(*expr)

        Projects a set of SQL expressions and returns a new DataFrame.

        DataFrame.semanticHash()

        Returns a hash code of the logical query plan against this DataFrame.

        DataFrame.show([n, truncate, vertical])

        Prints the first n rows to the console.

        DataFrame.sort(*cols, **kwargs)

        Returns a new DataFrame sorted by the specified column(s).

        DataFrame.sortWithinPartitions(*cols, **kwargs)

        Returns a new DataFrame with each partition sorted by the specified column(s).

        DataFrame.stat

        Returns a DataFrameStatFunctions for statistic functions.

        DataFrame.storageLevel

        Get the DataFrame’s current storage level.

        DataFrame.subtract(other)

        Return a new DataFrame containing rows in this DataFrame but not in another DataFrame.

        DataFrame.summary(*statistics)

        Computes specified statistics for numeric and string columns.

        DataFrame.tail(num)

        Returns the last num rows as a list of Row.

        DataFrame.take(num)

        Returns the first num rows as a list of Row.

        DataFrame.toDF(*cols)

        Returns a new DataFrame that with new specified column names

        DataFrame.toJSON([use_unicode])

        Converts a DataFrame into a RDD of string.

        DataFrame.toLocalIterator([prefetchPartitions])

        Returns an iterator that contains all of the rows in this DataFrame.

        DataFrame.toPandas()

        Returns the contents of this DataFrame as Pandas pandas.DataFrame.

        DataFrame.transform(func)

        Returns a new DataFrame.

        DataFrame.union(other)

        Return a new DataFrame containing union of rows in this and another DataFrame.

        DataFrame.unionAll(other)

        Return a new DataFrame containing union of rows in this and another DataFrame.

        DataFrame.unionByName(other[, …])

        Returns a new DataFrame containing union of rows in this and another DataFrame.

        DataFrame.unpersist([blocking])

        Marks the DataFrame as non-persistent, and remove all blocks for it from memory and disk.

        DataFrame.where(condition)

        where() is an alias for filter().

        DataFrame.withColumn(colName, col)

        Returns a new DataFrame by adding a column or replacing the existing column that has the same name.

        DataFrame.withColumnRenamed(existing, new)

        Returns a new DataFrame by renaming an existing column.

        DataFrame.withWatermark(eventTime, …)

        Defines an event time watermark for this DataFrame.

        DataFrame.write

        Interface for saving the content of the non-streaming DataFrame out into external storage.

        DataFrame.writeStream

        Interface for saving the content of the streaming DataFrame out into external storage.

        DataFrame.writeTo(table)

        Create a write configuration builder for v2 sources.

        DataFrame.to_pandas_on_spark([index_col])

        Converts the existing DataFrame into a pandas-on-Spark DataFrame.

        DataFrameNaFunctions.drop([how, thresh, subset])

        Returns a new DataFrame omitting rows with null values.

        DataFrameNaFunctions.fill(value[, subset])

        Replace null values, alias for na.fill().

        DataFrameNaFunctions.replace(to_replace[, …])

        Returns a new DataFrame replacing a value with another value.

        DataFrameStatFunctions.approxQuantile(col, …)

        Calculates the approximate quantiles of numerical columns of a DataFrame.

        DataFrameStatFunctions.corr(col1, col2[, method])

        Calculates the correlation of two columns of a DataFrame as a double value.

        DataFrameStatFunctions.cov(col1, col2)

        Calculate the sample covariance for the given columns, specified by their names, as a double value.

        DataFrameStatFunctions.crosstab(col1, col2)

        Computes a pair-wise frequency table of the given columns.

        DataFrameStatFunctions.freqItems(cols[, support])

        Finding frequent items for columns, possibly with false positives.

        DataFrameStatFunctions.sampleBy(col, fractions)

        Returns a stratified sample without replacement based on the fraction given on each stratum.

        Column APIs
        Column.alias(*alias, **kwargs)

        Returns this column aliased with a new name or names (in the case of expressions that return more than one column, such as explode).

        Column.asc()

        Returns a sort expression based on ascending order of the column.

        Column.asc_nulls_first()

        Returns a sort expression based on ascending order of the column, and null values return before non-null values.

        Column.asc_nulls_last()

        Returns a sort expression based on ascending order of the column, and null values appear after non-null values.

        Column.astype(dataType)

        astype() is an alias for cast().

        Column.between(lowerBound, upperBound)

        True if the current column is between the lower bound and upper bound, inclusive.

        Column.bitwiseAND(other)

        Compute bitwise AND of this expression with another expression.

        Column.bitwiseOR(other)

        Compute bitwise OR of this expression with another expression.

        Column.bitwiseXOR(other)

        Compute bitwise XOR of this expression with another expression.

        Column.cast(dataType)

        Casts the column into type dataType.

        Column.contains(other)

        Contains the other element.

        Column.desc()

        Returns a sort expression based on the descending order of the column.

        Column.desc_nulls_first()

        Returns a sort expression based on the descending order of the column, and null values appear before non-null values.

        Column.desc_nulls_last()

        Returns a sort expression based on the descending order of the column, and null values appear after non-null values.

        Column.dropFields(*fieldNames)

        An expression that drops fields in StructType by name.

        Column.endswith(other)

        String ends with.

        Column.eqNullSafe(other)

        Equality test that is safe for null values.

        Column.getField(name)

        An expression that gets a field by name in a StructType.

        Column.getItem(key)

        An expression that gets an item at position ordinal out of a list, or gets an item by key out of a dict.

        Column.isNotNull()

        True if the current expression is NOT null.

        Column.isNull()

        True if the current expression is null.

        Column.isin(*cols)

        A boolean expression that is evaluated to true if the value of this expression is contained by the evaluated values of the arguments.

        Column.like(other)

        SQL like expression.

        Column.name(*alias, **kwargs)

        name() is an alias for alias().

        Column.otherwise(value)

        Evaluates a list of conditions and returns one of multiple possible result expressions.

        Column.over(window)

        Define a windowing column.

        Column.rlike(other)

        SQL RLIKE expression (LIKE with Regex).

        Column.startswith(other)

        String starts with.

        Column.substr(startPos, length)

        Return a Column which is a substring of the column.

        Column.when(condition, value)

        Evaluates a list of conditions and returns one of multiple possible result expressions.

        Column.withField(fieldName, col)

        An expression that adds/replaces a field in StructType by name.

        Data Types
        ArrayType(elementType[, containsNull])

        Array data type.

        BinaryType

        Binary (byte array) data type.

        BooleanType

        Boolean data type.

        ByteType

        Byte data type, i.e.

        DataType

        Base class for data types.

        DateType

        Date (datetime.date) data type.

        DecimalType([precision, scale])

        Decimal (decimal.Decimal) data type.

        DoubleType

        Double data type, representing double precision floats.

        FloatType

        Float data type, representing single precision floats.

        IntegerType

        Int data type, i.e.

        LongType

        Long data type, i.e.

        MapType(keyType, valueType[, valueContainsNull])

        Map data type.

        NullType

        Null type.

        ShortType

        Short data type, i.e.

        StringType

        String data type.

        StructField(name, dataType[, nullable, metadata])

        A field in StructType.

        StructType([fields])

        Struct type, consisting of a list of StructField.

        TimestampType

        Timestamp (datetime.datetime) data type.

        Row
        Row.asDict([recursive])

        Return as a dict

        Functions
        abs(col)

        Computes the absolute value.

        acos(col)

        New in version 1.4.0.

        acosh(col)

        Computes inverse hyperbolic cosine of the input column.

        add_months(start, months)

        Returns the date that is months months after start

        aggregate(col, initialValue, merge[, finish])

        Applies a binary operator to an initial state and all elements in the array, and reduces this to a single state.

        approxCountDistinct(col[, rsd])

        Deprecated since version 2.1.0.
        approx_count_distinct(col[, rsd])

        Aggregate function: returns a new Column for approximate distinct count of column col.

        array(*cols)

        Creates a new array column.

        array_contains(col, value)

        Collection function: returns null if the array is null, true if the array contains the given value, and false otherwise.

        array_distinct(col)

        Collection function: removes duplicate values from the array.

        array_except(col1, col2)

        Collection function: returns an array of the elements in col1 but not in col2, without duplicates.

        array_intersect(col1, col2)

        Collection function: returns an array of the elements in the intersection of col1 and col2, without duplicates.

        array_join(col, delimiter[, null_replacement])

        Concatenates the elements of column using the delimiter.

        array_max(col)

        Collection function: returns the maximum value of the array.

        array_min(col)

        Collection function: returns the minimum value of the array.

        array_position(col, value)

        Collection function: Locates the position of the first occurrence of the given value in the given array.

        array_remove(col, element)

        Collection function: Remove all elements that equal to element from the given array.

        array_repeat(col, count)

        Collection function: creates an array containing a column repeated count times.

        array_sort(col)

        Collection function: sorts the input array in ascending order.

        array_union(col1, col2)

        Collection function: returns an array of the elements in the union of col1 and col2, without duplicates.

        arrays_overlap(a1, a2)

        Collection function: returns true if the arrays contain any common non-null element; if not, returns null if both the arrays are non-empty and any of them contains a null element; returns false otherwise.

        arrays_zip(*cols)

        Collection function: Returns a merged array of structs in which the N-th struct contains all N-th values of input arrays.

        asc(col)

        Returns a sort expression based on the ascending order of the given column name.

        asc_nulls_first(col)

        Returns a sort expression based on the ascending order of the given column name, and null values return before non-null values.

        asc_nulls_last(col)

        Returns a sort expression based on the ascending order of the given column name, and null values appear after non-null values.

        ascii(col)

        Computes the numeric value of the first character of the string column.

        asin(col)

        New in version 1.3.0.

        asinh(col)

        Computes inverse hyperbolic sine of the input column.

        assert_true(col[, errMsg])

        Returns null if the input column is true; throws an exception with the provided error message otherwise.

        atan(col)

        New in version 1.4.0.

        atanh(col)

        Computes inverse hyperbolic tangent of the input column.

        atan2(col1, col2)

        New in version 1.4.0.

        avg(col)

        Aggregate function: returns the average of the values in a group.

        base64(col)

        Computes the BASE64 encoding of a binary column and returns it as a string column.

        bin(col)

        Returns the string representation of the binary value of the given column.

        bitwise_not(col)

        Computes bitwise not.

        bitwiseNOT(col)

        Computes bitwise not.

        broadcast(df)

        Marks a DataFrame as small enough for use in broadcast joins.

        bround(col[, scale])

        Round the given value to scale decimal places using HALF_EVEN rounding mode if scale >= 0 or at integral part when scale < 0.

        bucket(numBuckets, col)

        Partition transform function: A transform for any type that partitions by a hash of the input column.

        cbrt(col)

        Computes the cube-root of the given value.

        ceil(col)

        Computes the ceiling of the given value.

        coalesce(*cols)

        Returns the first column that is not null.

        col(col)

        Returns a Column based on the given column name.’ Examples ——– >>> col(‘x’) Column<’x’> >>> column(‘x’) Column<’x’>

        collect_list(col)

        Aggregate function: returns a list of objects with duplicates.

        collect_set(col)

        Aggregate function: returns a set of objects with duplicate elements eliminated.

        column(col)

        Returns a Column based on the given column name.’ Examples ——– >>> col(‘x’) Column<’x’> >>> column(‘x’) Column<’x’>

        concat(*cols)

        Concatenates multiple input columns together into a single column.

        concat_ws(sep, *cols)

        Concatenates multiple input string columns together into a single string column, using the given separator.

        conv(col, fromBase, toBase)

        Convert a number in a string column from one base to another.

        corr(col1, col2)

        Returns a new Column for the Pearson Correlation Coefficient for col1 and col2.

        cos(col)

        New in version 1.4.0.

        cosh(col)

        New in version 1.4.0.

        count(col)

        Aggregate function: returns the number of items in a group.

        count_distinct(col, *cols)

        Returns a new Column for distinct count of col or cols.

        countDistinct(col, *cols)

        Returns a new Column for distinct count of col or cols.

        covar_pop(col1, col2)

        Returns a new Column for the population covariance of col1 and col2.

        covar_samp(col1, col2)

        Returns a new Column for the sample covariance of col1 and col2.

        crc32(col)

        Calculates the cyclic redundancy check value (CRC32) of a binary column and returns the value as a bigint.

        create_map(*cols)

        Creates a new map column.

        cume_dist()

        Window function: returns the cumulative distribution of values within a window partition, i.e.

        current_date()

        Returns the current date at the start of query evaluation as a DateType column.

        current_timestamp()

        Returns the current timestamp at the start of query evaluation as a TimestampType column.

        date_add(start, days)

        Returns the date that is days days after start

        date_format(date, format)

        Converts a date/timestamp/string to a value of string in the format specified by the date format given by the second argument.

        date_sub(start, days)

        Returns the date that is days days before start

        date_trunc(format, timestamp)

        Returns timestamp truncated to the unit specified by the format.

        datediff(end, start)

        Returns the number of days from start to end.

        dayofmonth(col)

        Extract the day of the month of a given date as integer.

        dayofweek(col)

        Extract the day of the week of a given date as integer.

        dayofyear(col)

        Extract the day of the year of a given date as integer.

        days(col)

        Partition transform function: A transform for timestamps and dates to partition data into days.

        decode(col, charset)

        Computes the first argument into a string from a binary using the provided character set (one of ‘US-ASCII’, ‘ISO-8859-1’, ‘UTF-8’, ‘UTF-16BE’, ‘UTF-16LE’, ‘UTF-16’).

        degrees(col)

        Converts an angle measured in radians to an approximately equivalent angle measured in degrees.

        dense_rank()

        Window function: returns the rank of rows within a window partition, without any gaps.

        desc(col)

        Returns a sort expression based on the descending order of the given column name.

        desc_nulls_first(col)

        Returns a sort expression based on the descending order of the given column name, and null values appear before non-null values.

        desc_nulls_last(col)

        Returns a sort expression based on the descending order of the given column name, and null values appear after non-null values.

        element_at(col, extraction)

        Collection function: Returns element of array at given index in extraction if col is array.

        encode(col, charset)

        Computes the first argument into a binary from a string using the provided character set (one of ‘US-ASCII’, ‘ISO-8859-1’, ‘UTF-8’, ‘UTF-16BE’, ‘UTF-16LE’, ‘UTF-16’).

        exists(col, f)

        Returns whether a predicate holds for one or more elements in the array.

        exp(col)

        Computes the exponential of the given value.

        explode(col)

        Returns a new row for each element in the given array or map.

        explode_outer(col)

        Returns a new row for each element in the given array or map.

        expm1(col)

        Computes the exponential of the given value minus one.

        expr(str)

        Parses the expression string into the column that it represents

        factorial(col)

        Computes the factorial of the given value.

        filter(col, f)

        Returns an array of elements for which a predicate holds in a given array.

        first(col[, ignorenulls])

        Aggregate function: returns the first value in a group.

        flatten(col)

        Collection function: creates a single array from an array of arrays.

        floor(col)

        Computes the floor of the given value.

        forall(col, f)

        Returns whether a predicate holds for every element in the array.

        format_number(col, d)

        Formats the number X to a format like ‘#,–#,–#.–’, rounded to d decimal places with HALF_EVEN round mode, and returns the result as a string.

        format_string(format, *cols)

        Formats the arguments in printf-style and returns the result as a string column.

        from_csv(col, schema[, options])

        Parses a column containing a CSV string to a row with the specified schema.

        from_json(col, schema[, options])

        Parses a column containing a JSON string into a MapType with StringType as keys type, StructType or ArrayType with the specified schema.

        from_unixtime(timestamp[, format])

        Converts the number of seconds from unix epoch (1970-01-01 00:00:00 UTC) to a string representing the timestamp of that moment in the current system time zone in the given format.

        from_utc_timestamp(timestamp, tz)

        This is a common function for databases supporting TIMESTAMP WITHOUT TIMEZONE.

        get_json_object(col, path)

        Extracts json object from a json string based on json path specified, and returns json string of the extracted json object.

        greatest(*cols)

        Returns the greatest value of the list of column names, skipping null values.

        grouping(col)

        Aggregate function: indicates whether a specified column in a GROUP BY list is aggregated or not, returns 1 for aggregated or 0 for not aggregated in the result set.

        grouping_id(*cols)

        Aggregate function: returns the level of grouping, equals to

        hash(*cols)

        Calculates the hash code of given columns, and returns the result as an int column.

        hex(col)

        Computes hex value of the given column, which could be pyspark.sql.types.StringType, pyspark.sql.types.BinaryType, pyspark.sql.types.IntegerType or pyspark.sql.types.LongType.

        hour(col)

        Extract the hours of a given date as integer.

        hours(col)

        Partition transform function: A transform for timestamps to partition data into hours.

        hypot(col1, col2)

        Computes sqrt(a^2 + b^2) without intermediate overflow or underflow.

        initcap(col)

        Translate the first letter of each word to upper case in the sentence.

        input_file_name()

        Creates a string column for the file name of the current Spark task.

        instr(str, substr)

        Locate the position of the first occurrence of substr column in the given string.

        isnan(col)

        An expression that returns true iff the column is NaN.

        isnull(col)

        An expression that returns true iff the column is null.

        json_tuple(col, *fields)

        Creates a new row for a json column according to the given field names.

        kurtosis(col)

        Aggregate function: returns the kurtosis of the values in a group.

        lag(col[, offset, default])

        Window function: returns the value that is offset rows before the current row, and default if there is less than offset rows before the current row.

        last(col[, ignorenulls])

        Aggregate function: returns the last value in a group.

        last_day(date)

        Returns the last day of the month which the given date belongs to.

        lead(col[, offset, default])

        Window function: returns the value that is offset rows after the current row, and default if there is less than offset rows after the current row.

        least(*cols)

        Returns the least value of the list of column names, skipping null values.

        length(col)

        Computes the character length of string data or number of bytes of binary data.

        levenshtein(left, right)

        Computes the Levenshtein distance of the two given strings.

        lit(col)

        Creates a Column of literal value.

        locate(substr, str[, pos])

        Locate the position of the first occurrence of substr in a string column, after position pos.

        log(arg1[, arg2])

        Returns the first argument-based logarithm of the second argument.

        log10(col)

        Computes the logarithm of the given value in Base 10.

        log1p(col)

        Computes the natural logarithm of the given value plus one.

        log2(col)

        Returns the base-2 logarithm of the argument.

        lower(col)

        Converts a string expression to lower case.

        lpad(col, len, pad)

        Left-pad the string column to width len with pad.

        ltrim(col)

        Trim the spaces from left end for the specified string value.

        map_concat(*cols)

        Returns the union of all the given maps.

        map_entries(col)

        Collection function: Returns an unordered array of all entries in the given map.

        map_filter(col, f)

        Returns a map whose key-value pairs satisfy a predicate.

        map_from_arrays(col1, col2)

        Creates a new map from two arrays.

        map_from_entries(col)

        Collection function: Returns a map created from the given array of entries.

        map_keys(col)

        Collection function: Returns an unordered array containing the keys of the map.

        map_values(col)

        Collection function: Returns an unordered array containing the values of the map.

        map_zip_with(col1, col2, f)

        Merge two given maps, key-wise into a single map using a function.

        max(col)

        Aggregate function: returns the maximum value of the expression in a group.

        md5(col)

        Calculates the MD5 digest and returns the value as a 32 character hex string.

        mean(col)

        Aggregate function: returns the average of the values in a group.

        min(col)

        Aggregate function: returns the minimum value of the expression in a group.

        minute(col)

        Extract the minutes of a given date as integer.

        monotonically_increasing_id()

        A column that generates monotonically increasing 64-bit integers.

        month(col)

        Extract the month of a given date as integer.

        months(col)

        Partition transform function: A transform for timestamps and dates to partition data into months.

        months_between(date1, date2[, roundOff])

        Returns number of months between dates date1 and date2.

        nanvl(col1, col2)

        Returns col1 if it is not NaN, or col2 if col1 is NaN.

        next_day(date, dayOfWeek)

        Returns the first date which is later than the value of the date column.

        nth_value(col, offset[, ignoreNulls])

        Window function: returns the value that is the offsetth row of the window frame (counting from 1), and null if the size of window frame is less than offset rows.

        ntile(n)

        Window function: returns the ntile group id (from 1 to n inclusive) in an ordered window partition.

        overlay(src, replace, pos[, len])

        Overlay the specified portion of src with replace, starting from byte position pos of src and proceeding for len bytes.

        pandas_udf([f, returnType, functionType])

        Creates a pandas user defined function (a.k.a.

        percent_rank()

        Window function: returns the relative rank (i.e.

        percentile_approx(col, percentage[, accuracy])

        Returns the approximate percentile of the numeric column col which is the smallest value in the ordered col values (sorted from least to greatest) such that no more than percentage of col values is less than the value or equal to that value.

        posexplode(col)

        Returns a new row for each element with position in the given array or map.

        posexplode_outer(col)

        Returns a new row for each element with position in the given array or map.

        pow(col1, col2)

        Returns the value of the first argument raised to the power of the second argument.

        product(col)

        Aggregate function: returns the product of the values in a group.

        quarter(col)

        Extract the quarter of a given date as integer.

        radians(col)

        Converts an angle measured in degrees to an approximately equivalent angle measured in radians.

        raise_error(errMsg)

        Throws an exception with the provided error message.

        rand([seed])

        Generates a random column with independent and identically distributed (i.i.d.) samples uniformly distributed in [0.0, 1.0).

        randn([seed])

        Generates a column with independent and identically distributed (i.i.d.) samples from the standard normal distribution.

        rank()

        Window function: returns the rank of rows within a window partition.

        regexp_extract(str, pattern, idx)

        Extract a specific group matched by a Java regex, from the specified string column.

        regexp_replace(str, pattern, replacement)

        Replace all substrings of the specified string value that match regexp with rep.

        repeat(col, n)

        Repeats a string column n times, and returns it as a new string column.

        reverse(col)

        Collection function: returns a reversed string or an array with reverse order of elements.

        rint(col)

        Returns the double value that is closest in value to the argument and is equal to a mathematical integer.

        round(col[, scale])

        Round the given value to scale decimal places using HALF_UP rounding mode if scale >= 0 or at integral part when scale < 0.

        row_number()

        Window function: returns a sequential number starting at 1 within a window partition.

        rpad(col, len, pad)

        Right-pad the string column to width len with pad.

        rtrim(col)

        Trim the spaces from right end for the specified string value.

        schema_of_csv(csv[, options])

        Parses a CSV string and infers its schema in DDL format.

        schema_of_json(json[, options])

        Parses a JSON string and infers its schema in DDL format.

        second(col)

        Extract the seconds of a given date as integer.

        sentences(string[, language, country])

        Splits a string into arrays of sentences, where each sentence is an array of words.

        sequence(start, stop[, step])

        Generate a sequence of integers from start to stop, incrementing by step.

        session_window(timeColumn, gapDuration)

        Generates session window given a timestamp specifying column.

        sha1(col)

        Returns the hex string result of SHA-1.

        sha2(col, numBits)

        Returns the hex string result of SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384, and SHA-512).

        shiftleft(col, numBits)

        Shift the given value numBits left.

        shiftright(col, numBits)

        (Signed) shift the given value numBits right.

        shiftrightunsigned(col, numBits)

        Unsigned shift the given value numBits right.

        shuffle(col)

        Collection function: Generates a random permutation of the given array.

        signum(col)

        Computes the signum of the given value.

        sin(col)

        New in version 1.4.0.

        sinh(col)

        New in version 1.4.0.

        size(col)

        Collection function: returns the length of the array or map stored in the column.

        skewness(col)

        Aggregate function: returns the skewness of the values in a group.

        slice(x, start, length)

        Collection function: returns an array containing all the elements in x from index start (array indices start at 1, or from the end if start is negative) with the specified length.

        sort_array(col[, asc])

        Collection function: sorts the input array in ascending or descending order according to the natural ordering of the array elements.

        soundex(col)

        Returns the SoundEx encoding for a string

        spark_partition_id()

        A column for partition ID.

        split(str, pattern[, limit])

        Splits str around matches of the given pattern.

        sqrt(col)

        Computes the square root of the specified float value.

        stddev(col)

        Aggregate function: alias for stddev_samp.

        stddev_pop(col)

        Aggregate function: returns population standard deviation of the expression in a group.

        stddev_samp(col)

        Aggregate function: returns the unbiased sample standard deviation of the expression in a group.

        struct(*cols)

        Creates a new struct column.

        substring(str, pos, len)

        Substring starts at pos and is of length len when str is String type or returns the slice of byte array that starts at pos in byte and is of length len when str is Binary type.

        substring_index(str, delim, count)

        Returns the substring from string str before count occurrences of the delimiter delim.

        sum(col)

        Aggregate function: returns the sum of all values in the expression.

        sum_distinct(col)

        Aggregate function: returns the sum of distinct values in the expression.

        sumDistinct(col)

        Aggregate function: returns the sum of distinct values in the expression.

        tan(col)

        New in version 1.4.0.

        tanh(col)

        New in version 1.4.0.

        timestamp_seconds(col)

        New in version 3.1.0.

        toDegrees(col)

        Deprecated since version 2.1.0.
        toRadians(col)

        Deprecated since version 2.1.0.
        to_csv(col[, options])

        Converts a column containing a StructType into a CSV string.

        to_date(col[, format])

        Converts a Column into pyspark.sql.types.DateType using the optionally specified format.

        to_json(col[, options])

        Converts a column containing a StructType, ArrayType or a MapType into a JSON string.

        to_timestamp(col[, format])

        Converts a Column into pyspark.sql.types.TimestampType using the optionally specified format.

        to_utc_timestamp(timestamp, tz)

        This is a common function for databases supporting TIMESTAMP WITHOUT TIMEZONE.

        transform(col, f)

        Returns an array of elements after applying a transformation to each element in the input array.

        transform_keys(col, f)

        Applies a function to every key-value pair in a map and returns a map with the results of those applications as the new keys for the pairs.

        transform_values(col, f)

        Applies a function to every key-value pair in a map and returns a map with the results of those applications as the new values for the pairs.

        translate(srcCol, matching, replace)

        A function translate any character in the srcCol by a character in matching.

        trim(col)

        Trim the spaces from both ends for the specified string column.

        trunc(date, format)

        Returns date truncated to the unit specified by the format.

        udf([f, returnType])

        Creates a user defined function (UDF).

        unbase64(col)

        Decodes a BASE64 encoded string column and returns it as a binary column.

        unhex(col)

        Inverse of hex.

        unix_timestamp([timestamp, format])

        Convert time string with given pattern (‘yyyy-MM-dd HH:mm:ss’, by default) to Unix time stamp (in seconds), using the default timezone and the default locale, return null if fail.

        upper(col)

        Converts a string expression to upper case.

        var_pop(col)

        Aggregate function: returns the population variance of the values in a group.

        var_samp(col)

        Aggregate function: returns the unbiased sample variance of the values in a group.

        variance(col)

        Aggregate function: alias for var_samp

        weekofyear(col)

        Extract the week number of a given date as integer.

        when(condition, value)

        Evaluates a list of conditions and returns one of multiple possible result expressions.

        window(timeColumn, windowDuration[, …])

        Bucketize rows into one or more time windows given a timestamp specifying column.

        xxhash64(*cols)

        Calculates the hash code of given columns using the 64-bit variant of the xxHash algorithm, and returns the result as a long column.

        year(col)

        Extract the year of a given date as integer.

        years(col)

        Partition transform function: A transform for timestamps and dates to partition data into years.

        zip_with(left, right, f)

        Merge two given arrays, element-wise, into a single array using a function.

        from_avro(data, jsonFormatSchema[, options])

        Converts a binary column of Avro format into its corresponding catalyst value.

        to_avro(data[, jsonFormatSchema])

        Converts a column into binary of avro format.

        Window
        Window.currentRow

        Window.orderBy(*cols)

        Creates a WindowSpec with the ordering defined.

        Window.partitionBy(*cols)

        Creates a WindowSpec with the partitioning defined.

        Window.rangeBetween(start, end)

        Creates a WindowSpec with the frame boundaries defined, from start (inclusive) to end (inclusive).

        Window.rowsBetween(start, end)

        Creates a WindowSpec with the frame boundaries defined, from start (inclusive) to end (inclusive).

        Window.unboundedFollowing

        Window.unboundedPreceding

        WindowSpec.orderBy(*cols)

        Defines the ordering columns in a WindowSpec.

        WindowSpec.partitionBy(*cols)

        Defines the partitioning columns in a WindowSpec.

        WindowSpec.rangeBetween(start, end)

        Defines the frame boundaries, from start (inclusive) to end (inclusive).

        WindowSpec.rowsBetween(start, end)

        Defines the frame boundaries, from start (inclusive) to end (inclusive).

        Grouping
        GroupedData.agg(*exprs)

        Compute aggregates and returns the result as a DataFrame.

        GroupedData.apply(udf)

        It is an alias of pyspark.sql.GroupedData.applyInPandas(); however, it takes a pyspark.sql.functions.pandas_udf() whereas pyspark.sql.GroupedData.applyInPandas() takes a Python native function.

        GroupedData.applyInPandas(func, schema)

        Maps each group of the current DataFrame using a pandas udf and returns the result as a DataFrame.

        GroupedData.avg(*cols)

        Computes average values for each numeric columns for each group.

        GroupedData.cogroup(other)

        Cogroups this group with another group so that we can run cogrouped operations.

        GroupedData.count()

        Counts the number of records for each group.

        GroupedData.max(*cols)

        Computes the max value for each numeric columns for each group.

        GroupedData.mean(*cols)

        Computes average values for each numeric columns for each group.

        GroupedData.min(*cols)

        Computes the min value for each numeric column for each group.

        GroupedData.pivot(pivot_col[, values])

        Pivots a column of the current DataFrame and perform the specified aggregation.

        GroupedData.sum(*cols)

        Computes the sum for each numeric columns for each group.

        PandasCogroupedOps.applyInPandas(func, schema)

        Applies a function to each cogroup using pandas and returns the result as a DataFrame.

        Catalog APIs
        Catalog.cacheTable(tableName)

        Caches the specified table in-memory.

        Catalog.clearCache()

        Removes all cached tables from the in-memory cache.

        Catalog.createExternalTable(tableName[, …])

        Creates a table based on the dataset in a data source.

        Catalog.createTable(tableName[, path, …])

        Creates a table based on the dataset in a data source.

        Catalog.currentDatabase()

        Returns the current default database in this session.

        Catalog.dropGlobalTempView(viewName)

        Drops the global temporary view with the given view name in the catalog.

        Catalog.dropTempView(viewName)

        Drops the local temporary view with the given view name in the catalog.

        Catalog.isCached(tableName)

        Returns true if the table is currently cached in-memory.

        Catalog.listColumns(tableName[, dbName])

        Returns a list of columns for the given table/view in the specified database.

        Catalog.listDatabases()

        Returns a list of databases available across all sessions.

        Catalog.listFunctions([dbName])

        Returns a list of functions registered in the specified database.

        Catalog.listTables([dbName])

        Returns a list of tables/views in the specified database.

        Catalog.recoverPartitions(tableName)

        Recovers all the partitions of the given table and update the catalog.

        Catalog.refreshByPath(path)

        Invalidates and refreshes all the cached data (and the associated metadata) for any DataFrame that contains the given data source path.

        Catalog.refreshTable(tableName)

        Invalidates and refreshes all the cached data and metadata of the given table.

        Catalog.registerFunction(name, f[, returnType])

        An alias for spark.udf.register().

        Catalog.setCurrentDatabase(dbName)

        Sets the current default database in this session.

        Catalog.uncacheTable(tableName)

        Removes the specified table from the in-memory cache.


   """
   pass

##################################################################################
def hadoop_print_config(dirout=None):
  """ Print configuration variable for Hadoop, Spark


  """
  names =[
    'SPARK_HOME',
    'HADOOP_HOME'


  ]

  dd= []
  for ni in names:
    dd.append( [ni, os.environ.get(ni, '') ] )

  ### Print configuration files on disk
  ### SPARK_HOME/conf/spark_env.sh
  
   



###############################################################################################################
def hdfs_ls(path, filename_only=False):
    from subprocess import Popen, PIPE
    process = Popen(f"hdfs dfs -ls -h '{path}'", shell=True, stdout=PIPE, stderr=PIPE)
    std_out, std_err = process.communicate()

    if filename_only:
       list_of_file_names = [fn.split(' ')[-1].split('/')[-1] for fn in std_out.decode().split('\n')[1:]][:-1]
       return list_of_file_names

    flist_full_address = [fn.split(' ')[-1] for fn in std_out.decode().split('\n')[1:]][:-1]
    return flist_full_address

     
def hdfs_mkdir(hdfs_dir):
    res = os_system( f"hdfs dfs -mkdir -p  '{hdfs_dir}' ", doprint=True)


def hdfs_copy_fromlocal(local_dir, hdfs_dir, overwrite=False):
    if overwrite: hdfs_rm_dir(hdfs_dir)
    res = os_system( f"hdfs dfs -copyFromLocal '{local_dir}'  '{hdfs_dir}' ", doprint=True)


def hdfs_copy_tolocal(hdfs_dir, local_dir):
    res = os_system( f"hdfs dfs -copyToLocal '{hdfs_dir}'  '{local_dir}' ", doprint=True)


def hdfs_rm_dir(path):
    if hdfs_dir_exists(path):
        print("removing old file "+path)
        cat = subprocess.call(["hdfs", "dfs", "-rm", path ])


def hdfs_dir_exists(path):
    return {0: True, 1: False}[subprocess.call(["hadoop", "fs", "-test", "-f", path ])]


def hdfs_file_exists(filename):
    ''' Return True when indicated file exists on HDFS.
    '''
    proc = subprocess.Popen(['hadoop', 'fs', '-test', '-e', filename])
    proc.communicate()

    if proc.returncode == 0:
        return True
    else:
        return False



############################################################################################################### 
############################################################################################################### 
def hdfs_pd_read_parquet(path=  'hdfs://user/test/myfile.parquet/', 
                 cols=None, n_rows=1000, file_start=0, file_end=100000, verbose=1, ) :
    """ Single Thread parquet file reading in HDFS
    Doc::
    
       Required HDFS connection
       conda install libhdfs3 pyarrow
       os.environ['ARROW_LIBHDFS_DIR'] = '/opt/cloudera/parcels/CDH/lib64/'
    """
    import pandas as pd
    import pyarrow as pa, gc
    import pyarrow.parquet as pq
    hdfs = pa.hdfs.connect()    
    
    n_rows = 999999999 if n_rows < 0  else n_rows
    
    flist = hdfs.ls( path )  
    flist = [ fi for fi in flist if  'hive' not in fi.split("/")[-1]  ]
    flist = flist[file_start:file_end]  #### Allow batch load by partition
    if verbose : print(flist)
    dfall = None
    for pfile in flist:
        if not "parquet" in pfile and not ".db" in pfile :
            continue
        if verbose > 0 :print( pfile )            
                    
        arr_table = pq.read_table(pfile, columns=cols)
        df        = arr_table.to_pandas()
        del arr_table; gc.collect()
        
        dfall = pd.concat((dfall, df)) if dfall is None else df
        del df
        if len(dfall) > n_rows :
            break

    if dfall is None : return None        
    if verbose > 0 : print( dfall.head(2), dfall.shape )          
    dfall = dfall.iloc[:n_rows, :]            
    return dfall


def hdfs_pd_write_parquet(df, hdfs_dir=  'hdfs:///user/pppp/clean_v01.parquet/', 
                 cols=None,n_rows=1000, partition_cols=None, overwrite=True, verbose=1, ) :
    """Pandas to HDFS
    Doc::

      pyarrow.parquet.write_table(table, where, row_group_size=None, version='1.0', use_dictionary=True, compression='snappy', write_statistics=True, use_deprecated_int96_timestamps=None, coerce_timestamps=None, allow_truncated_timestamps=False, data_page_size=None, flavor=None, filesystem=None, compression_level=None, use_byte_stream_split=False, data_page_version='1.0', **kwargs)
      
      https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_to_dataset.html#pyarrow.parquet.write_to_dataset
       
    """
    import pyarrow as pa
    import pyarrow.parquet as pq
    hdfs = pa.hdfs.connect()    
    n_rows = 999999999 if n_rows < 0  else n_rows
    df = df.iloc[:n_rows, :]
    
    table = pa.Table.from_pandas(df)
    
    if overwrite :
        hdfs.rm(hdfs_dir.replace("hdfs://", ""), recursive=True)
    hdfs.mkdir(hdfs_dir.replace("hdfs://", ""))
    pq.write_to_dataset(table, root_dir=hdfs_dir,
                        partition_cols=partition_cols, filesystem=hdfs)
    
    flist = hdfs.ls( hdfs_dir )  
    print(flist)


pd_write_file_hdfs   =  hdfs_pd_write_parquet
pd_read_parquet_hdfs =  hdfs_pd_read_parquet




def hdfs_download(dirin="", dirout="./", verbose=False, n_pool=1, **kw):
  """  Donwload files in parallel using pyarrow
  Doc::

        path_glob: list of HDFS pattern, or sep by ";"
        :return:
  """
  import glob, gc,os
  from multiprocessing.pool import ThreadPool

  def log(*s, **kw):
      print(*s, flush=True, **kw)

  #### File ############################################
  import pyarrow as pa
  hdfs  = pa.hdfs.connect()
  flist = [t for t in hdfs.ls(dirin)]

  def fun_async(x):
      hdfs.download(x[0], x[1])


  ######################################################
  file_list = sorted(list(set(flist)))
  n_file    = len(file_list)
  if verbose: log(file_list)

  #### Pool count
  if   n_pool < 1  :  n_pool = 1
  if   n_file <= 0 :  m_job  = 0
  elif n_file <= 2 :
    m_job  = n_file
    n_pool = 1
  else  :
    m_job  = 1 + n_file // n_pool  if n_file >= 3 else 1
  if verbose : log(n_file,  n_file // n_pool )

  pool   = ThreadPool(processes=n_pool)

  res_list=[]
  for j in range(0, m_job ) :
      if verbose : log("Pool", j, end=",")
      job_list = []
      for i in range(n_pool):
         if n_pool*j + i >= n_file  : break
         filei = file_list[n_pool*j + i]

         xi    = (filei, dirout + "/" + filei.split("/")[-1])

         job_list.append( pool.apply_async(fun_async, (xi, )))
         if verbose : log(j, filei)

      for i in range(n_pool):
        if i >= len(job_list): break
        res_list.append( job_list[ i].get() )


  pool.close()
  pool.join()
  pool = None
  if m_job>0 and verbose : log(n_file, j * n_file//n_pool )
  return res_list

 


############################################################################################################### 
############################################################################################################### 
CODE_SUCCESS = 0
CODE_SEMANTIC_ERROR = 22

hive_header_template =  '''
        set  hive.vectorized.execution.enabled = true;  set hive.vectorized.execution.reduce.enabled = true;
        set  hive.execution.engine=tez; set  hive.cli.print.header=true;    
        set mapreduce.fileoutputcommitter.algorithm.version=2;
        set hive.exec.parallel=true;  set hive.metastore.try.direct.sql=true;   set hive.metastore.client.socket.timeout=90000;

        -- Speed up writing
        set mapreduce.fileoutputcommitter.algorithm.version=2;

        -- duplicate column names
        set hive.support.quoted.identifiers=none;

        set  hive.auto.convert.join=true;
        set  hive.mapjoin.smalltable.filesize= 990000000;
        SET  hive.optimize.skewjoin=true;


        -- Cost based Optimization
        set hive.cbo.enable=true;
        set hive.compute.query.using.stats=true;
        set hive.stats.fetch.column.stats=true;
        set hive.stats.fetch.partition.stats=true;


        -- Default Value: 20 in Hive 0.7 through 0.13.1; 600 in Hive 0.14.0 and later
        -- Added In: Hive 0.7.0; default changed in Hive 0.14.0 with HIVE-7140


        --  Container RAM ####################################################
        SET hive.tez.container.size=5856;
        SET hive.tez.java.opts=-Xmx4096m;

        set mapreduce.map.memory.mb=4096;
        SET mapreduce.map.java.opts=-Xmx3096m;

        set mapreduce.reduce.memory.mb=4096;
        SET mapreduce.reduce.java.opts=-Xmx3096m;


        -- Impact the number of nodes used for Map - Reduce : Low --> high number of reducers ############
        -- set hive.exec.reducers.bytes.per.reducer=512000000 ;
        set hive.exec.reducers.bytes.per.reducer=512100100 ;

        SET mapred.max.split.size=512100100 ; 
        SET mapred.min.split.size=128100100 ; 


        -- JAR SERDE

        
'''.replace("    ", "")   ### Otherwise Hive queries failed





def hive_exec(query="", nohup:int=1, dry=False, end0=None):
        """  

        """
        hiveql = "./zhiveql_tmp.sql"
        print(query)    
        print(hiveql, flush=True) 

        with open(hiveql, mode='w') as f:
            f.write(query)      

        with open("nohup.out", mode='a') as f:
            f.write("\n\n\n\n###################################################################")
            f.write(query + "\n########################" )      

        # return 0

        if nohup > 0:
           os.system( f" nohup 2>&1   hive -f {hiveql}    & " )
        else :
           os.system( f" hive -f {hiveql}      " )        
        print('finish')   




def _quote_hive_query(query):
    return '"{}"'.format(query)


def hive_query_with_exception(query, args=[]):
    return_code, stdout, stderr = os_subprocess(['hive'] + args + ['-e', _quote_hive_query(query)])
    if return_code == CODE_SUCCESS:
        log('query %s is updated with message %s', query, stdout)
    else:
        raise Exception('Error for hive query :{} code: {}, stdout: {}, stderr: {}'.format(query, return_code, stdout, stderr))


def hive_query2(query, args=[]):
    return os_subprocess(['hive'] + args + ['-e', _quote_hive_query(query)])


def hive_update_partitions_table( hr, dt, location, table_name):
    log('Updating latest partition location in {table_name} table'.format(table_name=table_name))
    drop_partition_query =f"ALTER TABLE {table_name} DROP IF EXISTS PARTITION (dt='{dt}', hr={hr})"
    add_partition_query = f"ALTER TABLE {table_name} ADD PARTITION (dt='{dt}', hr={hr}) location '{location}'"
    hive_query_with_exception(drop_partition_query,args=['--hiveconf', 'hive.mapred.mode=unstrict'])
    hive_query_with_exception(add_partition_query, args=['--hiveconf', 'hive.mapred.mode=unstrict'])
    log(f'Updating latest partition location in {table_name} table completed successfully')




def hive_get_partitions(url="", user="myuser_hadoop",  table='mydb.mytable', dirout="myexport/" ):
    """Export Hive partition names on disk
     get_partitions


    """
    if "hdfs:" in url :
        fname = url.split("/")[-1].replace(".", "_")
        logfile  = dirout + f"/dt_{fname}.txt"
        cmd      = f"hadoop dfs -ls {url} |& tee -a    {logfile}"
        out,err  = os_system( cmd)
        return

    dbname, table = table.split(".")[0], table.split(".")[1]
    logfile  = f"ztmp/dt_{dbname}-{table}.txt"
    cmd      = f"hadoop dfs -ls hdfs://nameservice1/user/{user}/warehouse/{dbname}.db/{table}   |& tee -a    {logfile}"
    out,err  = os_system( cmd, doprint=True)



def hive_df_tohive(df, tableref="nono2.table2") :
    """ Export Dataframe to Hive table

    """
    ttable = tableref.replace(".", "_")
    ptmp   = "ztmp/ztmp_hive/" + ttable + "/"
    os.system("rm -rf " + ptmp )
    os.makedirs(ptmp, exist_ok=True )
    df.to_csv( ptmp + ttable + ".csv" , index=False, sep="\t")
    hive_csv_tohive( ptmp, tablename= tableref, tableref= tableref)



def hive_csv_tohive(folder, tablename="ztmp", tableref="nono2.table2"):
    """ Local CSV to Hive table

    """
    print("loading to hive ", tableref)
    try:
        hiveql   = "ztmp/hive_upload.sql"
        csvtable = tablename # + "_csv"
        foldr    = folder if folder[-1] == "/" else folder + "/"
        with open(hiveql, mode='w') as f:
            f.write( "DROP TABLE IF EXISTS {};\n".format(csvtable))
            f.write( "CREATE TABLE {0} ( ip STRING) ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' WITH SERDEPROPERTIES ('separatorChar' = '\t') STORED AS TEXTFILE TBLPROPERTIES('skip.header.line.count' = '1');\n".format(csvtable))
            f.write( "LOAD DATA LOCAL INPATH '{}*.csv' OVERWRITE INTO TABLE {};\n".format( foldr, csvtable))

        print(hiveql)
        os.system("hive -f " + hiveql)
        print('finish')

    except Exception as e:
        print(e)



def hive_sql_todf(sql, header_hive_sql:str='', verbose=1, save_dir=None, **kwargs):
    """  Load SQL Query result to pandas dataframe


    """
    import subprocess, os
    from collections import defaultdict
    sid = str(hash( str(sql) ))

    with open(header_hive_sql, mode='r') as fp:
        header_sql = fp.readlines()
    header_sql = "".join(header_sql)  + "\n"

    sql2 = header_sql + sql
    file1 = "ztmp/hive_receive.sql"
    with open( file1, 'w') as f1:
        f1.write(sql2)

    if verbose > 0 : print(sql2)

    cmd    = ["hive", '-f',  file1]
    result = subprocess.check_output(cmd)
    if verbose >= 1 : print( str(result)[:100] , len(result))
    n = len(result)

    try:
        result = result.decode("utf-8")  # bytes to string
        twod_list = [line.split('\t') for line in result.strip().split('\n')]
        columns = map(lambda x: x.split('.')[1] if '.' in x else x,
                      twod_list[0])

        # rename duplicated columns
        column_cnt = defaultdict(int)
        renamed_column = []
        for column in columns:
            column_cnt[column] += 1
            if column_cnt[column] > 1:
                renamed_column.append(column + '_' + str(column_cnt[column]))
            else:
                renamed_column.append(column)

        df = pd.DataFrame(twod_list[1:], columns=renamed_column)

        if save_dir is not None :
           fname = f'ztmp/hive_result/{sid}/'
           os.makedirs(os.path.dirname(fname), exist_ok=True)
           df.to_parquet( fname + '/table.parquet' )
           open(fname +'/sql.txt', mode='w').write(sql2)
           print('saved',  fname)

        print('hive table', df.columns, df.shape)
        return df

    except Exception as e:
        print(e)





def hive_update_partitions_table( hr, dt, location, table_name):
    logging.info('Updating latest partition location in {table_name} table'.format(table_name=table_name))
    drop_partition_query = "ALTER TABLE {table_name} DROP IF EXISTS PARTITION (dt='{dt}', hr={hr})".format \
            (table_name=table_name, dt=dt, hr=hr)
    add_partition_query = "ALTER TABLE {table_name} ADD PARTITION (dt='{dt}', hr={hr}) location '{loc}'".format \
            (table_name=table_name, dt=dt,  hr=hr, loc=location)
    run_hive_query_with_exception_on_failure(drop_partition_query,args=['--hiveconf', 'hive.mapred.mode=unstrict'])
    run_hive_query_with_exception_on_failure(add_partition_query, args=['--hiveconf', 'hive.mapred.mode=unstrict'])
    logging.info('Updating latest partition location in {table_name} table completed successfully'.format(table_name=table_name))

    


if 'insert_pandas_into_hive' :
    def convert_pyarrow(dirin, dirout):
        flist = reversed(glob_glob(dirin, 1000) )
        for fi in flist :
            log(fi)
            df = pd.read_parquet(fi)
            pd_to_file(df, dirout + fi.split("/")[-1] )


    def to_hive1(dirin=None, table=None, dirout=None):   ##  
        """  Need Pyarrow 3.0 to make it work.
             hive 1.2

             CREATE EXTERNAL TABLE n=st (
              siid   ,
            )
            STORED AS PARQUET TBLPROPERTIES ("parquet.compression"="SNAPPY")   ;


          hadoop dfs -put  /a/adigd_ranid_v15_140m_fast.parquet   /usload/

          hive -e "LOAD DATA LOCAL INPATH   '/us40m_fast.parquet'  OVERWRITE INTO TABLE  nono3.map_siid_ranid_v15test  ;"

          hadoop dfs  -rmr    /r/0/

          hadoop dfs  -put   /aur/0/   /useca_pur/


        """

        dirin2 = dirin if ".parquet" in dirin else dirin + "/*"
        log(dirin2, table)


        ########################################################################################################
        scheme = ""
        df, dirouti, fi = pd_to_hive_parquet(dirin2, dirout=dirout, nfile=1, verbose=True)
        scheme      = hive_schema(df)
        # log(df, dirouti)
        # dirouti = dir_cpa2 + "/ext/emb_map_siid_ranid_v15_145m/map_siid_ranid_145m.parquet/"
        log(dirouti)

        log('\n ################# Creating hive table')
        ss= f"""  CREATE EXTERNAL TABLE {table} ( 
                  {scheme} 
                  ) 
                  STORED AS PARQUET TBLPROPERTIES ("parquet.compression"="SNAPPY")   ;        
        """
        log(ss)
        to_file(ss, 'ztmp_hive_sql.sql', mode='w' )
        os_system('hive -f "ztmp_hive_sql.sql" ')


        log('\n ################# Metadata to Hive ')
        ss = f""" SET mapred.input.dir.recursive=true; SET hive.mapred.supports.subdirectories=true ;            
                  LOAD DATA LOCAL INPATH   '{dirouti}'  OVERWRITE INTO TABLE  {table}   ;  describe   {table}  ;              
        """
        to_file(ss, 'ztmp_hive_sql.sql', mode='w' )
        os_system(  'hive -f "ztmp_hive_sql.sql" ')


    def pd_to_hive_parquet(dirin, dirout="/ztmp_hive_parquet/", nfile=1, verbose=False):
        """  Hive parquet needs special headers  NEED PYARROW 3.0  for Hive compatibility
             Bug in fastparquet, cannot save float, int.,
        """
        import fastparquet as fp
        if isinstance(dirin, pd.DataFrame):
            fp.write(dirout, df, fixed_text=None, compression='SNAPPY', file_scheme='hive')
            return df.iloc[:10, :]

        flist = glob_glob(dirin, 1000)  ### only 1 file is for Meta-Data
        fi    = flist[-1]
        df    = pd.read_parquet( fi  )
        df    = df.iloc[:100, :]   ### Prevent RAM overflow
        if verbose: log(df, df.dtypes)

        # df = pd_schema_enforce_hive(df, int_default=0, dtype_dict = None)

        # df['p'] = 0

        df= df.rename(columns={ 'timestamp': 'timestamp1' })

        for c in df.columns :
            if c in ['shop_id', 'item_id', 'campaign_id', 'timekey'] :
                df[c] = df[c].astype('int64')
            else :
                df[c] = df[c].astype('str')


        os.system( f" rm -rf  {dirout}  ")
        os_makedirs(dirout)
        dirouti = dirout + "/" + fi.split("/")[-1]
        log('Exporting on disk', dirouti)
        fp.write(dirouti, df.iloc[:100,:], fixed_text=None, compression='SNAPPY', file_scheme='hive')


        ### Bug in Fastparquet with float, need to delete and replace by original files
        os.remove( f"{dirouti}/part.0.parquet"  )

        ### Replace by pyarrow 3.0
        df.to_parquet( f"{dirouti}/part.0.parquet"  )

        #### Need to KEEP ONE Parquet File, otherwise it creates issues
        dirout2 = dirouti +  '/' + fi.split("/")[-1]
        cmd = f"cp  {fi}    '{dirout2}' "
        # os_system( cmd   )

        return df.iloc[:10, :], dirouti, fi.split("/")[-1]


    def hive_schema(df):
        if isinstance(df, str):
            df = pd_read_parquet_schema(df)

        tt = ""
        for ci in df.columns :
            ss = str(df[ci].dtypes).lower()
            if 'object'  in ss:   tt = tt +  f"{ci} STRING ,\n"
            elif 'int64' in ss:   tt = tt +  f"{ci} BIGINT ,\n"
            elif 'float' in ss:   tt = tt +  f"{ci} DOUBLE ,\n"
            elif 'int'   in ss:   tt = tt +  f"{ci} INT ,\n"
        #log(tt[:-2])
        return tt[:-2]


    def pd_read_parquet_schema(uri: str) -> pd.DataFrame:
        """Return a Pandas dataframe corresponding to the schema of a local URI of a parquet file.

        The returned dataframe has the columns: column, pa_dtype
        """
        import pandas as pd, pyarrow.parquet
        # Ref: https://stackoverflow.com/a/64288036/
        schema = pyarrow.parquet.read_schema(uri, memory_map=True)
        schema = pd.DataFrame(({"column": name, "pa_dtype": str(pa_dtype)} for name, pa_dtype in zip(schema.names, schema.types)))
        schema = schema.reindex(columns=["column", "pa_dtype"], fill_value=pd.NA)  # Ensures columns in case the parquet file has an empty dataframe.
        return schema


    def hdfs_download_from_hive():  ### python runcopy.py  from_hive

        ss= f"""   hadoop dfs -get  "hdfs:/rehouse/no/{table}/"   {dirout} """
        os_system(ss)

        rename()  ### add .parquet


    def os_rename_parquet(dir0=None):   ## py rename
         import glob
         flist  = []

         if dir0 is not None :
            flist = flist + glob.glob( dir0 + "/*"  )

         flist += sorted( list(set(glob.glob( dir_cpa3 + "/input/*/*" ))) )
         flist += sorted( list(set(glob.glob( dir_cpa3 + "/input/*/*/*" ))) )

         log(len(flist))
         for fi in flist :
            fend = fi.split("/")[-1]
            if ".sh" in fend or ".py"  in fend or "COPY" in fend :
                continue

            if  '.parquet' in fend    : continue
            if not os.path.isfile(fi) : continue

            if '.' not in fend:
                try :
                  log(fi)
                  os.rename(fi, fi + ".parquet")
                except Exception as e :
                  log(e)




############################################################################################################### 
def os_makedirs(path:str):
  """function os_makedirs in HDFS or local
  """
  if 'hdfs:' not in path :
    os.makedirs(path, exist_ok=True)
  else :
    os.system(f"hdfs dfs mkdir -p '{path}'")

def os_system(cmd, doprint=False):
  """ os.system  and retrurn stdout, stderr values
  """
  import subprocess
  try :
    p          = subprocess.run( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, )
    mout, merr = p.stdout.decode('utf-8'), p.stderr.decode('utf-8')
    if doprint:
      l = mout  if len(merr) < 1 else mout + "\n\nbash_error:\n" + merr
      print(l)

    return mout, merr
  except Exception as e :
    print( f"Error {cmd}, {e}")


def date_format(datestr:str="", fmt="%Y%m%d", add_days=0, add_hours=0, timezone='Asia/Tokyo', fmt_input="%Y-%m-%d", 
                returnval='str,int,datetime'):
    """ One liner for date Formatter
    Doc::

        datestr: 2012-02-12  or ""  emptry string for today's date.
        fmt:     output format # "%Y-%m-%d %H:%M:%S %Z%z"

        date_format(timezone='Asia/Tokyo')    -->  "20200519" 
        date_format(timezone='Asia/Tokyo', fmt='%Y-%m-%d')    -->  "2020-05-19" 
        date_format(timezone='Asia/Tokyo', fmt='%Y%m%d', add_days=-1, returnval='int')    -->  20200518 


    """
    from pytz import timezone as tzone
    import datetime

    if len(str(datestr )) >7 :  ## Not None
        now_utc = datetime.datetime.strptime( str(datestr), fmt_input)       
    else:
        now_utc = datetime.datetime.now(tzone('UTC'))  # Current time in UTC

    now_new = now_utc + datetime.timedelta(days=add_days, hours=add_hours)

    if timezone != 'utc':
        now_new = now_new.astimezone(tzone(timezone))


    if   returnval == 'datetime': return now_new ### datetime
    elif returnval == 'int':      return int(now_new.strftime(fmt))
    else:                        return now_new.strftime(fmt)


def os_subprocess(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    import subprocess
    proc = subprocess.Popen(args_list, stdout=stdout, stderr=stderr)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr





def hdfs_help():
 print("""
    cat: Copies source paths to stdout.
    Usage: hdfs dfs -cat URI [URI ?]

    Example:
        hdfs dfs -cat hdfs://<path>/file1
        hdfs dfs -cat file:///file2 /user/hadoop/file3

    chgrp: Changes the group association of files. With -R, makes the change recursively by way of the directory structure. The user must be the file owner or the superuser.
    Usage: hdfs dfs -chgrp [-R] GROUP URI [URI ?]

    chmod: Changes the permissions of files. With -R, makes the change recursively by way of the directory structure. The user must be the file owner or the superuser
    Usage: hdfs dfs -chmod [-R] <MODE[,MODE]? | OCTALMODE> URI [URI ?]
    Example: hdfs dfs -chmod 777 test/data1.txt

    chown: Changes the owner of files. With -R, makes the change recursively by way of the directory structure. The user must be the superuser.
    Usage: hdfs dfs -chown [-R] [OWNER][:[GROUP]] URI [URI ]
    Example: hdfs dfs -chown -R hduser2 /opt/hadoop/logs

    copyFromLocal: Works similarly to the put command, except that the source is restricted to a local file reference.
    Usage: hdfs dfs -copyFromLocal <localsrc> URI
    Example: hdfs dfs -copyFromLocal input/docs/data2.txt hdfs://localhost/user/rosemary/data2.txt

    copyToLocal: Works similarly to the get command, except that the destination is restricted to a local file reference.
    Usage: hdfs dfs -copyToLocal [-ignorecrc] [-crc] URI <localdst>
    Example: hdfs dfs -copyToLocal data2.txt data2.copy.txt

    count: Counts the number of directories, files, and bytes under the paths that match the specified file pattern.
    Usage: hdfs dfs -count [-q] <paths>
    Example: hdfs dfs -count hdfs://nn1.example.com/file1 hdfs://nn2.example.com/file2

    cp: Copies one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory.
    Usage: hdfs dfs -cp URI [URI ?] <dest>
    Example: hdfs dfs -cp /user/hadoop/file1 /user/hadoop/file2 /user/hadoop/dir

    du: Displays the size of the specified file, or the sizes of files and directories that are contained in the specified directory. If you specify the -s option, displays an aggregate summary of file sizes rather than individual file sizes. If you specify the -h option, formats the file sizes in a �ghuman-readable�h way.
    Usage: hdfs dfs -du [-s] [-h] URI [URI ?]
    Example: hdfs dfs -du /user/hadoop/dir1 /user/hadoop/file1

    dus: Displays a summary of file sizes; equivalent to hdfs dfs -du ?s.
    Usage: hdfs dfs -dus <args>

    expunge: Empties the trash. When you delete a file, it isn�ft removed immediately from HDFS, but is renamed to a file in the /trash directory. As long as the file remains there, you can undelete it if you change your mind, though only the latest copy of the deleted file can be restored.
    Usage: hdfs dfs ?expunge

    get: Copies files to the local file system. Files that fail a cyclic redundancy check (CRC) can still be copied if you specify the ?ignorecrc option. The CRC is a common technique for detecting data transmission errors. CRC checksum files have the .crc extension and are used to verify the data integrity of another file. These files are copied if you specify the -crc option.
    Usage: hdfs dfs -get [-ignorecrc] [-crc] <src> <localdst>
    Example: hdfs dfs -get /user/hadoop/file3 localfile

    getmerge: Concatenates the files in src and writes the result to the specified local destination file. To add a newline character at the end of each file, specify the addnl option.
    Usage: hdfs dfs -getmerge <src> <localdst> [addnl]
    Example: hdfs dfs -getmerge /user/hadoop/mydir/ ~/result_file addnl

    ls: Returns statistics for the specified files or directories.
    Usage: hdfs dfs -ls <args>
    Example: hdfs dfs -ls /user/hadoop/file1

    lsr: Serves as the recursive version of ls; similar to the Unix command ls -R.
    Usage: hdfs dfs -lsr <args>
    Example: hdfs dfs -lsr /user/hadoop

    mkdir: Creates directories on one or more specified paths. Its behavior is similar to the Unix mkdir -p command, which creates all directories that lead up to the specified directory if they don�ft exist already.
    Usage: hdfs dfs -mkdir <paths>
    Example: hdfs dfs -mkdir /user/hadoop/dir5/temp

    moveFromLocal: Works similarly to the put command, except that the source is deleted after it is copied.
    Usage: hdfs dfs -moveFromLocal <localsrc> <dest>
    Example: hdfs dfs -moveFromLocal localfile1 localfile2 /user/hadoop/hadoopdir

    mv: Moves one or more files from a specified source to a specified destination. If you specify multiple sources, the specified destination must be a directory. Moving files across file systems isn�ft permitted.
    Usage: hdfs dfs -mv URI [URI ?] <dest>
    Example: hdfs dfs -mv /user/hadoop/file1 /user/hadoop/file2

    put: Copies files from the local file system to the destination file system. This command can also read input from stdin and write to the destination file system.
    Usage: hdfs dfs -put <localsrc> ? <dest>
    Example: hdfs dfs -put localfile1 localfile2 /user/hadoop/hadoopdir; hdfs dfs -put ? /user/hadoop/hadoopdir (reads input from stdin)


    rm: Deletes one or more specified files. This command doesn�ft delete empty directories or files. To bypass the trash (if it�fs enabled) and delete the specified files immediately, specify the -skipTrash option.
    Usage: hdfs dfs -rm [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rm hdfs://nn.example.com/file9
    
    rmr: Serves as the recursive version of ?rm.
    Usage: hdfs dfs -rmr [-skipTrash] URI [URI ?]
    Example: hdfs dfs -rmr /user/hadoop/dir

    setrep: Changes the replication factor for a specified file or directory. With ?R, makes the change recursively by way of the directory structure.
    Usage: hdfs dfs -setrep <rep> [-R] <path>

    Example: hdfs dfs -setrep 3 -R /user/hadoop/dir1
    stat: Displays information about the specified path.

    Usage: hdfs dfs -stat URI [URI ?]
    Example: hdfs dfs -stat /user/hadoop/dir1
    tail: Displays the last kilobyte of a specified file to stdout. The syntax supports the Unix -f option, which enables the specified file to be monitored. As new lines are added to the file by another process, tail updates the display.

    Usage: hdfs dfs -tail [-f] URI
    Example: hdfs dfs -tail /user/hadoop/dir1

    test: Returns attributes of the specified file or directory. Specifies ?e to determine whether the file or directory exists; -z to determine whether the file or directory is empty; and -d to determine whether the URI is a directory.
    Usage: hdfs dfs -test -[ezd] URI
    Example: hdfs dfs -test /user/hadoop/dir1

    text: Outputs a specified source file in text format. Valid input file formats are zip and TextRecordInputStream.
    Usage: hdfs dfs -text <src>
    Example: hdfs dfs -text /user/hadoop/file8.zip  

    touchz: Creates a new, empty file of size 0 in the specified path.
    Usage: hdfs dfs -touchz <path>
    Example: hdfs dfs -touchz /user/hadoop/file12   """)
     
     

###############################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()

