"""Spark Utils
Doc::

    pip install utilmy
    OR git clone ...    && cd myutil && pip install -e .   ### Dev mode

    ####  CLI Access
    sspark h
    sspark spark_config_check


    #### In Python Code
    from utilmy.sspark.src.util_spark import   spark_config_check

    ### Require
       pyspark
       conda  install libhdfs3 pyarrow
       https://stackoverflow.com/questions/53087752/unable-to-load-libhdfs-when-using-pyarrow



    utilmy/sspark/src/util_spark.py
    -------------------------functions----------------------
    analyze_parquet(dirin, dirout, tag = '', nfiles = 1, nrows = 10, minimal = True, random_sample = True, verbose = 1, cols = None)
    config_parser_yaml(config)
    date_get_month_days(dt)
    date_get_timekey(unix_ts)
    date_get_unix_day_from_datetime(dt_with_timezone)
    date_get_unix_from_datetime(dt_with_timezone)
    date_now(datenow:Union[str, int, datetime.datetime] = "", fmt = "%Y%m%d", add_days = 0, add_hours = 0, timezone = 'Asia/Tokyo', fmt_input = "%Y-%m-%d", force_dayofmonth = -1, ###  01 first of monthforce_dayofweek = -1, force_hourofday = -1, returnval = 'str,int,datetime/unix')
    hdfs_dir_stats(dirin, recursive = True)
    hive_check_table(tables:Union[list, str], add_jar_cmd = "")
    hive_db_dumpall()
    hive_get_dblist()
    hive_get_tablechema(tablename)
    hive_get_tabledetails(table)
    hive_get_tablelist(dbname)
    hive_run_sql(query_or_sqlfile = "", nohup:int = 1, test = 0, end0 = None)
    json_compress(raw_obj)
    json_decompress(data)
    show_parquet(path, nfiles = 1, nrows = 10, verbose = 1, cols = None)
    spark_add_jar(sparksession, hive_jar_cmd = None)
    spark_config_check()
    spark_config_create(mode = '', dirout = "./conf_spark/")
    spark_config_print(sparksession)
    spark_df_check(df:sp_dataframe, tag = "check", conf:dict = None, dirout:str =  "", nsample:int = 10, save = True, verbose = True, returnval = False)
    spark_df_filter_mostrecent(df:sp_dataframe, colid = 'userid', col_orderby = 'date', decreasing = 1, rank = 1)
    spark_df_over_sample(df:sp_dataframe, coltarget:str, major_label, minor_label, ratio, )
    spark_df_sample(df, fractions = 0.1, col_stratify = None, with_replace = True)
    spark_df_stats_all(df:sp_dataframe, cols:Union[list, str], sample_fraction = -1, metric_list = ['null', 'n5', 'n95' ], doprint = True)
    spark_df_stats_null(df:sp_dataframe, cols:Union[list, str], sample_fraction = -1, doprint = True)
    spark_df_timeseries_split(df_m:sp_dataframe, splitRatio:float, sparksession:object)
    spark_df_under_sample(df:sp_dataframe, coltarget, major_label, minor_label, ratio, )
    spark_df_write(df:sp_dataframe, dirout:str =  "", show:int = 0, numPartitions:int = None, saveMode:str =  "append", format:str =  "parquet")
    spark_get_session(config:dict, config_key_name = 'spark_config', verbose = 0)
    spark_metrics_classifier_summary(df_labels_preds)
    spark_metrics_roc_summary(labels_and_predictions_df)
    spark_read(sparksession = None, dirin="hdfs = "hdfs://", **kw)
    spark_run_sqlfile(sparksession = None, spark_config:dict = None, sql_path:str = "", map_sql_variables:dict = None)

    os_file_replace(dirin = ["myfolder/**/*.sh", "myfolder/**/*.conf", ], textold = '/mypath2/', textnew = '/mypath2/', test = 1)
    os_subprocess(args_list, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    os_system(cmd, doprint = False)
    run_cli_sspark()


    ### More docs:
       https://github.com/arita37/myutil/issues/502

    ### Docker available:
      https://hub.docker.com/r/artia37/spark243-hdp27

"""
import os, sys, yaml, calendar, datetime, json, pytz, subprocess, time,zlib
import pandas  as pd
import numpy as np
from box import Box
from typing import Union


import pyspark
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

sp_dataframe= pyspark.sql.DataFrame
##################################################################################
def log(*s):
    print(*s, flush=True)




##################################################################################
from utilmy.sspark.src.util_hadoop import *
from utilmy.sspark.src.util_hadoop import (
   hdfs_copy_tolocal,
   hdfs_copy_fromlocal,
   hdfs_dir_exists,
   hdfs_file_exists,
   hdfs_mkdir,
   hdfs_rm_dir,
   hdfs_download,
   hdfs_ls,
   hdfs_list_dir,
   hdfs_size_dir,

### parquet
hdfs_pd_read_parquet,
hdfs_pd_write_parquet,
pd_read_parquet_hdfs,
pd_write_file_hdfs,


### hive
#hive_csv_tohive,
#hive_check_table,
#hive_run_sql

)

########################################################################################
###### TESTS  ##########################################################################
def test_all():
    test1()
    test2()


def test1():
    ss="""
    spark.master                       : 'local[1]'   # 'spark://virtual:7077'
    spark.app.name                     : 'logprocess'
    spark.driver.maxResultSize         : '10g'
    spark.driver.memory                : '10g'
    spark.driver.port                  : '45975'
    #spark.eventLog.enabled             : 'true'
    #spark.executor.cores               : 5
    #spark.executor.id                  : 'driver'
    #spark.executor.instances           : 2
    spark.executor.memory              : '10g'
    #spark.kryoserializer.buffer.max    : '2000mb'
    spark.rdd.compress                 : 'True'
    spark.serializer                   : 'org.apache.spark.serializer.KryoSerializer'
    #spark.serializer.objectStreamReset : 100
    spark.sql.shuffle.partitions       : 8
    spark.sql.session.timeZone         : "UTC"    
    # spark.sql.catalogImplementation  : 'hive'
    #spark.sql.warehouse.dir           : '/user/myuser/warehouse'
    #spark.sql.warehouse.dir           : '/tmp'    
    spark.submit.deployMode            : 'client'
    """
    cfg = config_parser_yaml(ss)
    log(cfg)
    sparksession = spark_get_session_local()

    spark_config_print(sparksession)


    spark_config_check()


def test2():
    sparksession = spark_get_session_local()
    df = pd.DataFrame(np.random.random((27,  5)), columns=[ 'c'+str(i) for i in range(0,5) ])
    df = sparksession.createDataFrame(df)




def run_cli_sspark():
    import fire
    fire.Fire()





################################################################################################
###### TODO : list of function to be completed later ###########################################


def hdfs_dir_stats(dirin,recursive=True):
    """  nfile, total size in bytes, last modified
         format of files,

    """
    if hdfs_dir_exists(dirin):
        hdfs_list_dir(dirin,recursive)
        hdfs_size_dir(dirin)
    else:
        print("{} does not exist!".format(dirin))
    



def hive_get_tablelist(dbname):

    cmd = f'show tables from {dbname}'



def hive_get_dblist():

    cmd = f'show databases '



def hive_get_tablechema(tablename):
    cmd = f'show schema '



def hive_get_tabledetails(table):
    cmd = f'described formatted {table}'




def hive_db_dumpall():
    cmd = 'dump all db, table schema on disk'



def spark_read(sparksession=None, dirin="hdfs://", **kw):
    """ Universal HDFS file reader
    Doc::

    """

    try:
        df = sparksession.read_parquet(dirin, **kw)
    except:     
        df = sparksession.read_csv(dirin, **kw)

    return df

















########################################################################################
###### HDFS PARQUET ####################################################################
def show_parquet(path, nfiles=1, nrows=10, verbose=1, cols=None):
    """ Us pyarrow
    Doc::

       conda  install libhdfs3 pyarrow
       https://stackoverflow.com/questions/53087752/unable-to-load-libhdfs-when-using-pyarrow


    """
    import pandas as pd
    import pyarrow as pa, gc
    import pyarrow.parquet as pq
    hdfs = pa.hdfs.connect()

    n_rows = 999999999 if nrows < 0  else nrows

    flist = hdfs.ls( path )
    flist = [ fi for fi in flist if  'hive' not in fi.split("/")[-1]  ]
    flist = flist[:nfiles]

    dfall = None
    for pfile in flist:
        if verbose > 0 :print( pfile )

        try :
            arr_table = pq.read_table(pfile, columns=cols)
            df        = arr_table.to_pandas()
            print(df.head(nrows), df.shape, df.columns)
            del arr_table; gc.collect()
        except : pass


def analyze_parquet(dirin, dirout, tag='', nfiles=1, nrows=10, minimal=True, random_sample=True, verbose=1, cols=None):
    """ Make report in HTML from HDFS parquer files
    Doc::

       pip install pandas-profiling

    """
    import pandas as pd, numpy as np
    import pyarrow as pa, gc
    from utilmy.sspark.src.util_hadoop import pd_read_parquet_hdfs

    hdfs = pa.hdfs.connect()
    flist = hdfs.ls( dirin )
    flist = [ fi for fi in flist if  'hive' not in fi.split("/")[-1]  ]
    if random_sample: flist = flist[np.random.randint(0, len(flist))][:nfiles]   #### random sample

    df = pd_read_parquet_hdfs(flist, n_rows= nrows, cols=cols)

    from pandas_profiling import ProfileReport

    profile = ProfileReport(df, minimal=minimal)
    os.makedirs(dirout, exist_ok=True)
    profile.to_file( dirout + f"/data_profile_{tag}.html")






#######################################################################################
###### SPARK CONFIG ###################################################################
def spark_get_session_local(config:str="/default.yaml", keyfield='sparkconfig'):
    """  Start Local session for debugging
    Docs::

            sparksession = spark_get_session_local()  

            sparksession = spark_get_session_local('mypath/conffig.yaml)  

    """
    from utilmy.utilmy import direpo
    # from utilmy.configs.util_config import config_load

    if config == "/default.yaml":
        dir1 = direpo() + "/sspark/config/config_local.yaml"
    else :
        dir1  = config

    log(dir1)
    configd = config_load(dir1)
    configd = configd[keyfield]
    log(configd)

    sparksession = spark_get_session(configd)

    cols =  [ 'c1', 'c2']
    df = sparksession.createDataFrame([[0,1 ],[2,4]]).toDF(*cols)
    print(df.show())

    return sparksession




def spark_config_print(sparksession):
    log('\n####### Spark Conf')
    conft = sparksession.sparkContext.getConf().getAll()
    for x in conft:
        print(x)

    log('\n####### Env Variables')
    for key,val in os.environ.items():
        print(key,val)

    log('\n####### Spark Conf files:  spark-env.sh ')
    os.system(  f'cat  $SPARK_HOME/conf/spark-env.sh ')

    log('\n####### Spark Conf:  spark-defaults.conf')
    os.system(  f'cat  $SPARK_HOME/conf/spark-defaults.conf ')


def spark_config_check():
    """ Check if files are misisng !!! Very useful for new spark install.
    Doc::

         pip install -e .    // pip install utilmy
         sspark spark_config_check


    """
    env_vars_required = ['SPARK_HOME', 'HADOOP_HOME']
    file_required = [ '$SPARK_HOME/conf/spark-env.sh',  '$SPARK_HOME/conf/spark-defaults.conf' ]

    for env_path in env_vars_required:
        path = os.environ.get(env_path)
        log("exists: " + env_path + " = " + path) if path else log("not exists: " + env_path)

    for file in file_required:
        file_path = os.path.expandvars(file)
        if os.path.exists(file_path):
            log("exist: " + file_path)
        elif os.path.exists(file_path + '.template'):
            log("exist: " + file_path + '.template') # windows
        else:
            log("not exists: " + file_path)


def spark_config_create(mode='', dirout="./conf_spark/"):
    """ Dump template Spark config into a folder.


    """
    pass

    file_required = [ '$SPARK_HOME/conf/spark-env.sh' ]

    if mode=='yarn-cluster':
        pass

    if mode=='yarn-client':
        pass

    if mode=='local':
        pass



def spark_get_session(config:dict, config_key_name='spark_config', verbose=0):
    """  Generic Spark session creation
    Doc::

         config:  path on disk OR dictionnary

         config_key_name='spark_config'  for sub-folder


    """
    from pyspark import SparkConf
    from pyspark.sql import SparkSession
    if isinstance(config, str):
        from utilmy.configs.util_config import config_load
        config_path = config
        config = config_load(config_path)  ### Universal config loader
    assert isinstance(config, dict),  'spark configuration is not a dictionary {}'.format(config)

    if config_key_name in config:
        config = config[config_key_name]
    assert 'spark.master' in config , f"config seems incorrect: {config}"


    conf = SparkConf()
    conf.setAll(config.items())
    spark = SparkSession.builder.config(conf=conf)

    if config.get('hive_support', False):
       spark = spark.enableHiveSupport().getOrCreate()
    else:
       spark = spark.getOrCreate()

    if 'pyfiles' in config:
        spark.sparkContext.addPyFile(  config.get('pyfiles') )

    if verbose>0:
        print(spark)

    return spark



def spark_add_jar(sparksession, hive_jar_cmd=None):
    try :
      ss  = "create temporary function tmp_f1 as 'com.jsonserde.udf.Empty2Null'  using jar 'hdfs:///user/myjar/json-serde.jar' ; "
      if hive_jar_cmd is not None:
          ss= hive_jar_cmd

      sparksession.sql(ss)
      log('JAR added')

    except Exception as e :
        log(e)







#########################################################################################
###### Dataframe ########################################################################
#from pyspark.sql.functions import col, explode, array, lit
def spark_df_check(df:sp_dataframe, tag="check", conf:dict=None, dirout:str= "", nsample:int=10,
                   save=True, verbose=True, returnval=False):
    """ Check dataframe for debugging
    Doc::

        Args:
            conf:  Configuration in dict
            df:
            dirout:
            nsample:
            save:
            verbose:
            returnval:
        Returns:
    """
    if conf is not None :
        confc = conf.get('Check', {})
        dirout = confc.get('path_check', dirout)
        save = confc.get('save', save)
        returnval = confc.get('returnval', returnval)
        verbose = confc.get('verbose', verbose)

    if save or returnval or verbose:
        df1 =   df.limit(nsample).toPandas()

    if save :
        ##### Need HDFS version
        os.makedirs(dirout, exist_ok=True)
        df1.to_csv(dirout + f'/table_{tag}.csv', sep='\t', index=False)

    if verbose :
        log(df1.head(2).T)
        log( df.printSchema() )

    if returnval :
        return df1



def spark_df_write(df:sp_dataframe, dirout:str= "", show:int=0, numPartitions:int=None, saveMode:str= "append", format:str= "parquet"):
    """
    Doc::
        saveMode: append, overwrite, ignore, error
        format: parquet, csv, json ...
    """
    if numPartitions:
        df.coalesce(numPartitions).write.mode(saveMode).save(dirout, format)
    else:
        df.write.mode(saveMode).save(dirout, format)

    if show:
        df.show(3)



def spark_df_over_sample(df:sp_dataframe, coltarget:str, major_label, minor_label, ratio, ):
    print("Count of df before over sampling is  "+ str(df.count()))
    major_df = df.filter(F.col(coltarget) == major_label)
    minor_df = df.filter(F.col(coltarget) == minor_label)
    a = range(ratio)
    # duplicate the minority rows
    oversampled_df = minor_df.withColumn("dummy", F.explode(F.array([F.lit(x) for x in a]))).drop('dummy')
    # combine both oversampled minority rows and previous majority rows
    combined_df = major_df.unionAll(oversampled_df)
    print("Count of combined df after over sampling is  "+ str(combined_df.count()))
    return combined_df


def spark_df_under_sample(df:sp_dataframe, coltarget, major_label, minor_label, ratio,):
    print("Count of df before under sampling is  "+ str(df.count()))
    major_df = df.filter(F.col(coltarget) == major_label)
    minor_df = df.filter(F.col(coltarget) == minor_label)
    sampled_majority_df = major_df.sample(False, ratio,seed=33)
    combined_df = sampled_majority_df.unionAll(minor_df)
    print("Count of combined df after under sampling is  " + str(combined_df.count()))
    return combined_df


def spark_df_timeseries_split(df_m:sp_dataframe, splitRatio:float, sparksession:object):
    """.
    Doc::

            # Splitting data into train and test
            # we maintain the time-order while splitting
            # if split ratio = 0.7 then first 70% of data is train data
            Args:
                df_m:
                splitRatio:
                sparksession:

            Returns: df_train, df_test

    """
    from pyspark.sql import types as T
    newSchema  = T.StructType(df_m.schema.fields + \
                [T.StructField("Row Number", T.LongType(), False)])
    new_rdd        = df_m.rdd.zipWithIndex().map(lambda x: list(x[0]) + [x[1]])
    df_m2          = SparkSession.createDataFrame(new_rdd, newSchema)
    total_rows     = df_m2.count()
    splitFraction  =int(total_rows*splitRatio)
    df_train       = df_m2.where(df_m2["Row Number"] >= 0)\
                          .where(df_m2["Row Number"] <= splitFraction)
    df_test        = df_m2.where(df_m2["Row Number"] > splitFraction)
    return df_train, df_test


def spark_df_filter_mostrecent(df:sp_dataframe, colid='userid', col_orderby='date', decreasing=1, rank=1):
    """ get most recent (ie date desc, rank=1) record of userid
    """
    partition_by = colid
    dedupe_df = df.withColumn('rnk__',F.row_number().over(Window.partitionBy(partition_by).orderBy(F.desc(col_orderby))))\
    .where(F.col('rnk__')==rank)\
    .drop('rnk__')
    return dedupe_df


def spark_df_stats_null(df:sp_dataframe,cols:Union[list,str], sample_fraction=-1, doprint=True):
    """ get the percentage of value absent in the column
    """
    if isinstance(cols, str): cols= [ cols]

    if sample_fraction>0 :
         df = spark_df_sample(df,  fractions= sample_fraction, col_stratify=None, with_replace=True)
    
    n = df.count()
    dfres = []
    for coli in cols :
        try :
           n_null    = df.where( f"{coli} is null").count()
           npct_null = np.round( n_null / n , 5)
           dfres.append([ coli, n,  n_null, npct_null  ])
        except :
            log( 'error: ' + coli)

    dfres = pd.DataFrame(dfres, columns=['col', 'ntot',  'n_null', 'npct_null'])
    if doprint :print(dfres)
    return dfres




def spark_df_stats_all(df:sp_dataframe,cols:Union[list,str], sample_fraction=-1,
                       metric_list=['null', 'n5', 'n95' ], doprint=True):
    """ TODO: get stats 5%, 95% for each column
    """
    if isinstance(cols, str): cols= [ cols]

    if sample_fraction>0 :
         df = spark_df_sample(df,  fractions= sample_fraction, col_stratify=None, with_replace=True)
    

    n = df.count()
    dfres = []
    for coli in cols :
        try :
           n_null  = df.where( f"{coli} is null").count()     if 'null' in metric_list else -1
           n5      = df.approxQuantile(coli, [0.05], 0.1)[0]  if 'n5'   in metric_list else -1
           n95     = df.approxQuantile(coli, [0.95], 0.1)[0]  if 'n95'  in metric_list else -1
           nunique = df.agg(F.approx_count_distinct(F.col(coli))).head()[0]

           dfres.append([ coli, n, n_null, n5 , n95, nunique  ])
        except :
            log( 'error: ' + coli)

    dfres = pd.DataFrame(dfres, columns=['col', 'ntotal', 'n_null',  'n5', 'n95', 'nunique' ])
    if doprint :print(dfres)
    return dfres


def spark_df_sample(df,  fractions=0.1, col_stratify=None, with_replace=True):
    """


    """
    if col_stratify:
        df1 = df.sampleBy(col= col_stratify, fractions=fractions, seed=None)
        return df1

    df1 = df.sample(with_replace, fractions=fractions, seed=None)
    return df1





#########################################################################################
###### SQL  #############################################################################
def spark_run_sqlfile(sparksession=None, spark_config:dict=None,sql_path:str="", map_sql_variables:dict=None)->pyspark.sql.DataFrame:
    """ Execute SQL
    Doc::

          map_sql_variables = {'start_dt':  '2020-01-01',  }

    """
    sp_session = spark_get_session(spark_config) if sparksession is None else sparksession
    with open(sql_path, mode='r') as fr:
        query = fr.read()
        query = query.format(**map_sql_variables)  if map_sql_variables is not None else query
        df_results = sp_session.sql(query)
        return df_results


def hive_check_table(tables:Union[list,str], add_jar_cmd=""):
  """ Check Hive table using Hive
  Doc::

       tables = [  'mydb.mytable'   ]
       OR
          myalias : mydb.mytable



  """
  if isinstance(tables, str):
      ### Parse YAML file
      ss = tables.split("\n")
      ss = [t for t in ss if len(t) > 5  ]
      ss = [  t.split(":") for t in ss]
      ss = [ (t[0].strip(), t[1].strip().replace("'", "") ) for t in ss ]
      print(ss)

  elif isinstance(tables, list):
      ss = [ [ ti, ti] for ti in tables  ]

  for x in ss :
    cmd = """hive -e   " """ + add_jar_cmd  +  f"""   describe formatted  {x[1]}  ; "  """
    log(x[0], cmd)
    log( os.system( cmd ) )



def hive_run_sql(query_or_sqlfile="", nohup:int=1, test=0, end0=None):
        """

        """
        if ".sql" in query_or_sqlfile or ".txt" in query_or_sqlfile  :
            with open(query_or_sqlfile, mode='r') as fp:
                query = query_or_sqlfile.readlines()
                query = "".join(query)
        else :
            query = query_or_sqlfile

        hiveql = "./zhiveql_tmp.sql"
        print(query)
        print(hiveql, flush=True)

        with open(hiveql, mode='w') as f:
            f.write(query)

        with open("nohup.out", mode='a') as f:
            f.write("\n\n\n\n###################################################################")
            f.write(query + "\n########################" )

        if test == 1 :
            return

        if nohup > 0:
           os.system( f" nohup 2>&1   hive -f {hiveql}    & " )
        else :
           os.system( f" hive -f {hiveql}      " )
        print('finish')




#########################################################################################
###### In/Out  ##########################################################################
def spark_read_subfolder(sparksession,  dir_parent:str, nfile_past=24, exclude_pattern="", **kw):
    """ subfolder
    doc::

          dir_parent/2021-02-03/file1.csv
          dir_parent/2021-02-04/file1.csv
          dir_parent/2021-02-05/file1.csv



    """
    # from util_hadoop import hdfs_ls
    flist = hdfs_ls(dir_parent )
    flist = sorted(flist)  ### ordered by dates increasing
    flist = flist[-nfile_past:] if nfile_past > 0 else flist
    log('Reading Npaths', len(flist))

    path =  ",".join(flist)
    df = sparksession.read.csv(path, header=True, **kw)
    return df







#########################################################################################
###### metrics  #########################################################################
def spark_metrics_classifier_summary(df_labels_preds):
    from pyspark.mllib.evaluation import MulticlassMetrics
    from pyspark.mllib.evaluation import BinaryClassificationMetrics

    labels_and_predictions_rdd =df_labels_preds.rdd.map(list)
    metrics = MulticlassMetrics(labels_and_predictions_rdd)
    # Overall statistics
    precision = metrics.precision()
    recall = metrics.recall()
    f1Score = metrics.fMeasure()
    confusion_metric = metrics.confusionMatrix
    print("Summary Stats")
    print("Precision = %s" % precision)
    print("Recall = %s" % recall)
    print("F1 Score = %s" % f1Score)
    print("Confusion Metrics = %s " %confusion_metric)
    # Weighted stats
    print("Weighted recall = %s" % metrics.weightedRecall)
    print("Weighted precision = %s" % metrics.weightedPrecision)
    print("Weighted F(1) Score = %s" % metrics.weightedFMeasure())
    print("Weighted F(0.5) Score = %s" % metrics.weightedFMeasure(beta=0.5))
    print("Weighted false positive rate = %s" % metrics.weightedFalsePositiveRate)


def spark_metrics_roc_summary(labels_and_predictions_df):
    from pyspark.mllib.evaluation import BinaryClassificationMetrics

    labels_and_predictions_rdd =labels_and_predictions_df.rdd.map(list)
    metrics = BinaryClassificationMetrics(labels_and_predictions_rdd)
    # Area under precision-recall curve
    print("Area under PR = %s" % metrics.areaUnderPR)
    # Area under ROC curve
    print("Area under ROC = %s" % metrics.areaUnderROC)






##########################################################################################
###### Dates  ############################################################################
def date_now(datenow:Union[str,int,datetime.datetime]="", fmt="%Y%m%d", add_days=0, add_hours=0, 
             timezone='Asia/Tokyo', fmt_input="%Y-%m-%d",
             force_dayofmonth=-1,   ###  01 first of month
             force_dayofweek=-1,
             force_hourofday=-1,
             returnval='str,int,datetime/unix'):
    """ One liner for date Formatter
    Doc::

        datenow: 2012-02-12  or ""  emptry string for today's date.
        fmt:     output format # "%Y-%m-%d %H:%M:%S %Z%z"

        date_now(timezone='Asia/Tokyo')    -->  "20200519"   ## Today date in YYYMMDD
        date_now(timezone='Asia/Tokyo', fmt='%Y-%m-%d')    -->  "2020-05-19"
        date_now('2021-10-05',fmt='%Y%m%d', add_days=-5, returnval='int')    -->  20211001
        date_now(20211005, fmt='%Y-%m-%d', fmt_input='%Y%m%d', returnval='str')    -->  '2021-10-05'


    """
    from pytz import timezone as tzone
    import datetime, time

    if isinstance(datenow, datetime.datetime):
        now_utc = datenow

    elif len(str(datenow)) >7 :  ## Not None
        now_utc = datetime.datetime.strptime(str(datenow), fmt_input)
    else:
        now_utc = datetime.datetime.now(tzone('UTC'))  # Current time in UTC

    #### Force dates
    if force_dayofmonth >0 :
        now_utc = now_utc.replace(day=force_dayofmonth)

    if force_dayofweek >0 :
        pass

    if force_hourofday >0 :
        now_utc = now_utc.replace(hour=force_hourofday)


    now_new = now_utc.astimezone(tzone(timezone))  if timezone != 'utc' else  now_utc.astimezone(tzone('UTC'))
    now_new = now_new + datetime.timedelta(days=add_days, hours=add_hours)

    if   returnval == 'datetime': return now_new ### datetime
    elif returnval == 'int':      return int(now_new.strftime(fmt))
    elif returnval == 'unix':     return time.mktime(now_new.timetuple())
    else:                         return now_new.strftime(fmt)


def date_get_month_days(dt):
    _, days = calendar.monthrange(dt.year, dt.month)
    return days

def date_get_timekey(unix_ts):
    return int(unix_ts+9*3600)/86400

def date_get_unix_from_datetime(dt_with_timezone):
    return time.mktime(dt_with_timezone.astimezone(pytz.utc).timetuple())

def date_get_unix_day_from_datetime(dt_with_timezone):
    return int(date_get_unix_from_datetime(dt_with_timezone)) / 86400







#########################################################################################
def config_load(config_path:str):
    """  Load Config filt yaml into a dict
    """
    from box import Box
    import yaml
    #Load the yaml config file
    with open(config_path, "r") as yamlfile:
        config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)

    dd = {}
    for x in config_data :
        for key,val in x.items():
           dd[key] = val

    dd = Box(dd)
    return dd


def config_parser_yaml(config):
    """ Parse string YAML
    Doc::

            spark.master                       : 'local[1]'   # 'spark://virtual:7077'
            spark.app.name                     : 'logprocess'
            spark.driver.maxResultSize         : '10g'

    """
    ss = config
    cfg = Box({})
    for line in ss.split("\n"):
        if not line:
            continue
        l1 = line.split(":")
        if len(l1) < 2:
            continue
        key = l1[0].strip()
        val = l1[1].split("#")[0].strip().strip("'")
        if key[0] == "#":
            continue
        cfg[key] = val
    return cfg


def json_compress(raw_obj):
    return zlib.compress(str.encode(json.dumps(raw_obj)))


def json_decompress(data):
    return json.loads(bytes.decode(zlib.decompress(data)))


def os_subprocess(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    import subprocess
    proc = subprocess.Popen(args_list, stdout=stdout, stderr=stderr)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


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


def os_file_replace(dirin=["myfolder/**/*.sh",  "myfolder/**/*.conf",   ],
                    textold='/mypath2/', textnew='/mypath2/', test=1):
    """ Replace string in config files.
    Doc::

         sspark os_file_replace --dirin spark/conf  --textold 'mydir1/' --textnew 'mydir2/'  --test 1

    """
    import glob

    txt1= textold ##  "/usr/local/old/"
    txt2= textnew  ## "/new/"


    flist = []
    for diri in dirin:
       flist = glob.glob( diri , recursive= True )

    flist = [ fi for fi in flist if 'backup' not in fi]
    log(flist)

    for fi in flist :
      flag = False
      with open(fi,'r') as fp:
        lines = fp.readlines()

      ss = []
      for li in lines :
        if txt1 in li :
          flag = True
          li = li.replace(txt1, txt2)
        ss.append(li)

      if flag  :
        log('update', fi)
        # log(ss)
        # break
        if test == 0 :
          with open(fi, mode='w') as fp :
             fp.writelines("".join(ss))
        # break





###############################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()



