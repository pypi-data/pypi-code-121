# Framework
from pyspark.sql.functions import countDistinct, expr, lit, count, avg, concat_ws, desc
from pyspark.sql.types import StringType
from delta.tables import DeltaTable
import re
global spark
global dbutils
global display


class PartitionAnalyzer:
    def __init__(self, tablename, columns, dryRun=True, basepath="abfss://silver@az21p1sewe02.dfs.core.windows.net/tmp/partitiontest/"):
        """
        tablename: <schema>.table
        columns: Array of columns to use for partitioning
        The column can be an expression like substring(d,1,2) as _part1
        """

        self.dryRun = dryRun
        self.tablename = tablename
        self._tableOnly = tablename.split('.')[1]
        self.df = spark.table(tablename)
        self.path = f"{basepath}{self.tablename}"
        self.targetTable = f"delta.`{self.path}`"
        self.clonepath = f"{basepath}{self.tablename}_clone"
        self.targetClone = f"delta.`{self.clonepath}`"

        # Columns in the target table - used in update / insert statements
        self.target_columns = self.df.columns
        self.df_history = spark.sql(f'DESCRIBE history {tablename}')
        self.columns = columns
        self.column_names = []  # List of fieldnames for partitioning
        # field or the expression; indexed by column name.
        self.column_expr = {}
        self.expr = []  # columns that have an expression.
        regex = re.compile(r'(.*)\sas\s([a-z0-9_]+)', re.I)
        for c in columns:
            m = regex.match(c)
            if m:
                # Expr found
                colname = m.group(2).lower()
                self.column_names.append(colname)
                self.expr.append(colname)
                self.column_expr[colname] = m.group(1)
            else:
                # No expression
                colname = c.lower()
                self.column_names.append(colname)
                self.column_expr[colname] = colname

    def profileFields(self):
        df = self.df
        columns = self.columns
        fieldname = columns[0]
        field = expr(fieldname)
        df_out = df.agg(countDistinct(field).alias('distinct'),
                        min(field).alias('min'),
                        max(field).alias('max')).\
            withColumn('field', lit(fieldname)).\
            select('field', 'distinct', 'min', 'max')
        for fieldname in columns[1:]:
            field = expr(fieldname)
            df_next = df.agg(countDistinct(field).alias('distinct'),
                             min(field).alias('min'),
                             max(field).alias('max')).\
                withColumn('field', lit(fieldname)).\
                select('field', 'distinct', 'min', 'max')
            df_out = df_out.union(df_next)

        return df_out

    def partitionSizes(self):
        df = self.df
        columns = list(map(lambda x: expr(x), self.columns))
        df_out = df.groupBy(*columns).agg(count(lit(1)).alias('rows'))
        df_out = df_out.select(
            concat_ws(':', *self.column_names).alias('value'), 'rows')
        df_out = df_out.orderBy(desc('rows'))
        df_summary = df_out.agg(avg('rows').alias('avg'),
                                min('rows').alias('min'),
                                max('rows').alias('max'))\
            .withColumn('fields', lit(":".join(self.column_names)))
        return [df_summary, df_out]

    def partitionCount(self):
        df = self.df
        columns = list(map(lambda x: expr(x), self.columns))
        df_out = df.select(countDistinct(*columns).alias('count'))
        count = df_out.collect()[0]['count']
        return count

    def partitionsInTableChange(self, version):
        tablename = self.tablename
        columns = list(map(lambda x: expr(x), self.column_expr.values()))
        query = f"select {','.join(self.columns)} from table_changes('{tablename}',{version},{version})"
        df = spark.sql(query)
        df_out = df.select(lit(version).alias('version'),
                           countDistinct(*self.column_names).alias('count'))
        return df_out

    def partitionsInHistory(self):
        tablename = self.tablename
        try:
            versions = self.df_history.select('version').limit(30).collect()
            df_out = None
            for row in versions:
                try:
                    # print(row['version'])
                    df_step = self.partitionsInTableChange(row['version'])
                    if df_out == None:
                        df_out = df_step
                    else:
                        df_out = df_out.union(df_step)
                except Exception as e:
                    print(f"Skipping version {row['version']}. Error:")
                    print(e)
            lst = df_out.select(avg('count').alias('avg')).collect()
            averagePartitionCount = lst[0]['avg']
            return [df_out, averagePartitionCount]
        except Exception as e:
            print('Error calculating average partition size.')
            print(e)

    def fullAnalysis(self):
        df_fields = self.profileFields()
        [df_size_summary, df_sizes] = self.partitionSizes()
        count = self.partitionCount()
        [df_partitions, averagePartitionCount] = self.partitionsInHistory()
        print(f"Table:      {self.tablename}")
        print(f"Columns:    {','.join(self.columns)}")
        print(f"Partitions: {count}")
        print(
            f"Average partitions touched every change: {averagePartitionCount}")
        print("Profile of fields")
        df_fields.show(truncate=False)
        print("Summary of partition sizes")
        df_size_summary.show(truncate=False)
        print("Details of changes and impacted partitions")
        df_partitions.show(truncate=False)
        print("Details of partition sizes")
        display(df_sizes)
        return

    def nonPartitionBasedMerge(self, targetTable, version):
        mquery = self.getMergeQueryForVersion(
            targetTable, version, '', '')
        if (self.dryRun == False):
            spark.sql(mquery)
        else:
            print(mquery)

    def partitionBasedMerge(self, targetTable, version):
        """
        This merges the changes in table_changes @ version - with the targetTable.
        The changed rows - are grouped by partition values.
        Each combination of partition values - will trigger a separate merge.
        """
        query_changes = f"select {','.join(self.columns)} from table_changes('{self.tablename}',{version},{version})  where _change_type!='update_preimage'"
        df_changes = spark.sql(query_changes)
        columns = list(map(lambda x: expr(x), self.column_expr.keys()))
        df_partitionValues = df_changes.select(*columns).distinct()
        mqueryTemplate = self.getMergeQueryForVersion(
            targetTable, version, "###SOURCE####", "###TARGET####")
        # Helper for Lambda.

        for pv in df_partitionValues.toLocalIterator():
            clauseListTarget = map(
                lambda x: f" a.{x}='{pv[x]}' ", self.column_names)
            clauseListSource = map(
                lambda x: f" ({self.column_expr[x]}='{pv[x]}') ", self.column_names)
            clauseTarget = "and (" + "and".join(clauseListTarget) + ") "
            clauseSource = "and (" + "and".join(clauseListSource) + ") "
            # clauseTarget = where condition with partition fields to restrict the partition (MERGE partition skipping)
            # clauseSource = where condition with partition fields to restrict the changes
            mquery = mqueryTemplate.replace("###SOURCE####", clauseSource).replace(
                "###TARGET####", clauseTarget)
            if self.dryRun == False:
                # print(mquery)
                spark.sql(mquery)
            else:
                print(mquery)

    def getMergeQueryForVersion(self, targetTable, version, clauseSource="", clauseTarget=""):
        """
        returns SQL MERGE query from table version, into the targetTable.
        clauseTarget = where condition with partition fields to restrict the partition (MERGE partition skipping)
        clauseSource = where condition with partition fields to restrict the changes
        """
        df = self.df_history.filter(
            f'operation="MERGE" and version={version}').limit(1)
        df = df.select('operationParameters')
        list = df.collect()
        if (len(list) > 0):
            mergeParams = list[0].__getattr__('operationParameters')
            p_main = mergeParams['predicate'].replace(
                'm.`merge', 'm.`').replace('m.merge', 'm.')
            # p_matched=mergeParams['matchedPredicates']
            # p_notmatched=mergeParams['notMatchedPredicates']
            p_update_list = map(
                lambda x: f" a.`{x}` = m.`{x}` ", self.target_columns)
            p_update_clause = ",".join(p_update_list)
            p_insert_set_clause = ",".join(
                map(lambda x: f"`{x}`", self.target_columns))
            p_insert_values_clause = ",".join(
                map(lambda x: f"m.`{x}`", self.target_columns))
            query = f"""
            MERGE INTO {targetTable} a
            USING ( SELECT * from table_changes('{self.tablename}',{version},{version})  where _change_type!='update_preimage' {clauseSource}) m
            ON {p_main} {clauseTarget}
            WHEN MATCHED
                AND m._change_type = 'delete' THEN
                DELETE
            WHEN MATCHED
                AND m._change_type != 'delete' THEN
                UPDATE SET {p_update_clause}
            WHEN NOT MATCHED
                AND m._change_type != 'delete' THEN
                INSERT ({p_insert_set_clause}) VALUES ({p_insert_values_clause})
            """
            return query
        else:
            return ""

    def makeDeepClone(self, path, version):
        """
        Make a Deep clone of a table to a path
        """
        if self.dryRun:
            print('Skipping deep clone due to dryRun')
        else:
            dbutils.fs.rm(path, True)
            query = f"CREATE TABLE delta.`{path}` DEEP CLONE {self.tablename}@v{version}"
            print(query)
            spark.sql(query)

    def getTableProperties(self, table):
        df = spark.sql(f"DESCRIBE TABLE EXTENDED {table}").filter(
            'col_name="Table Properties"')
        properties = df.collect()[0].data_type
        properties = properties.rstrip(']').lstrip('[')
        return properties

    def makePartitionedClone(self, path, version):
        """
        Make a partitioned clone of a table to a path
        """
        dbutils.fs.rm(path, True)
        input = spark.table(f"{self.tablename}@v{version}")
        dtc = DeltaTable.createOrReplace(spark) \
            .location(path) \
            .addColumns(input.schema)
        for calculatedColumn in self.expr:
            calculatedExpr = self.column_expr[calculatedColumn]
            # Use generated columns to calculate the expressions used to partition.
            dtc = dtc.addColumn(calculatedColumn, StringType(
            ), generatedAlwaysAs=f"CAST({calculatedExpr} AS STRING)")
            # Add generated columns to the input DF hopefully to speed up the copy.
            input = input.withColumn(calculatedColumn, expr(calculatedExpr))
        dtc.partitionedBy(*self.column_names).execute()
        properties = self.getTableProperties(self.tablename)
        sqlProperties = f"ALTER TABLE delta.`{path}` SET TBLPROPERTIES ({properties})"
        if self.dryRun:
            print(sqlProperties)
            print('Skipping load of data since this is a dryRun')
        else:
            spark.sql(sqlProperties)
            input.write.format("delta") \
                 .mode("overwrite") \
                 .save(path)

    def summarizeMergePerformance(self, df, label):
        """
        Summary the operationMetrics from MERGE history
        """
        df = df.agg(
            sum('operationMetrics.executionTimeMs').alias('executionTimeMs'),
            sum('operationMetrics.scanTimeMs').alias('scanTimeMs'),
            sum('operationMetrics.rewriteTimeMs').alias('rewriteTimeMs'),
            sum('operationMetrics.numSourceRows').alias('numSourceRows'),
            sum('operationMetrics.numOutputRows').alias('numOutputRows'),
            sum('operationMetrics.numTargetRowsInserted').alias(
                'numTargetRowsInserted'),
            sum('operationMetrics.numTargetRowsUpdated').alias(
                'numTargetRowsUpdated'),
            sum('operationMetrics.numTargetRowsDeleted').alias(
                'numTargetRowsDeleted'),
            sum('operationMetrics.numTargetRowsCopied').alias(
                'numTargetRowsCopied'),
            sum('operationMetrics.numTargetFilesAdded').alias(
                'numTargetFilesAdded'),
            sum('operationMetrics.numTargetFilesRemoved').alias(
                'numTargetFilesRemoved'),
            sum('operationMetrics.numTargetChangeFilesAdded').alias(
                'numTargetChangeFilesAdded'),
        )
        df = df.withColumn('label', lit(label))
        return df

    def testPartition(self, changes=10, basepath=""):
        # basepath - is ignored. Please use basepath in the class constructor.
        # Get version 10 merge steps earlier.
        df = spark.sql(f'describe history {self.tablename}').filter(
            'operation="MERGE"').limit(changes)
        df = df.orderBy('version').select(
            'version', 'readVersion', 'operationMetrics')
        list = df.collect()
        if (len(list) > 0):
            startVersion = list[0]['readVersion']
        else:
            startVersion = ""
            print(
                f'Did not find a version. Reduce the number of changes from {changes}')
            return
        self.cloneTable(startVersion, changes)
        self.applyChangeLog(startVersion, changes)

    def cloneTable(self, startVersion, changes):
        """
        Makes a partitioned copy of the table and a clone of the table.
        """
        print(
            f"Testing {self.tablename}. Replaying changes starting with version {startVersion}")

        print(
            f"Making a partitioned clone of {self.tablename} to {self.path}.")
        self.makePartitionedClone(self.path, startVersion)
        print(f"Making a clone of {self.tablename} to {self.clonepath}.")
        self.makeDeepClone(self.clonepath, startVersion)

    def applyChangeLog(self, startVersion, changes=20):
        # Apply changes to partitioned table
        df = spark.sql(f'describe history {self.tablename}').filter(
            f'operation="MERGE" and version > {startVersion}').limit(changes)
        df = df.orderBy('version').select(
            'version', 'readVersion', 'operationMetrics')
        list = df.collect()
        if (len(list) <= 0):
            print('No change history found. exiting.')
            return

        for change in list:
            version = change['version']
            print(
                f"  Applying change in version {change['version']} to partitioned table {self.targetTable} ")
            self.partitionBasedMerge(self.targetTable, version)

        # Apply changes to cloned table
        for change in list:
            version = change['version']
            print(
                f"  Applying change in version {change['version']} to cloned table {self.targetClone} ")
            self.nonPartitionBasedMerge(self.targetClone, version)

        # Display Merge performance
        print('Merge performance')
        if self.dryRun == False:
            print('Original performance')
            display(df)
            print(f'New performance with partitioned {self.targetTable}')
            df_new = spark.sql(f'describe history {self.targetTable}').filter(
                'operation="MERGE"').limit(changes)
            df_new = df_new.orderBy('version').select(
                'version', 'operationMetrics')
            display(df_new)
            print(f'New performance with clone {self.targetClone}')
            df_clone = spark.sql(f'describe history {self.targetClone}').filter(
                'operation="MERGE"').limit(changes)
            df_clone = df_clone.orderBy('version').selectExpr(
                'version+1 as version', 'operationMetrics')  # Versions are a bit out of step
            display(df_clone)
#             df_joined = df_new.alias("part").join(
#                 df_clone.alias("clone"), ['version'], 'left')
#             display(df_joined)
            df_summary_orig = self.summarizeMergePerformance(df, 'original')
            df_summary_new = self.summarizeMergePerformance(
                df_new, 'partitioned')
            df_summary_clone = self.summarizeMergePerformance(
                df_clone, 'clone')
            df_summary = df_summary_orig.union(
                df_summary_new).union(df_summary_clone)
            print('Summarized performance')
            display(df_summary)
