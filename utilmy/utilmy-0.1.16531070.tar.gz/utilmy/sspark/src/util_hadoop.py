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


def log(*s):
  print(*s, flush=True)




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

def hdfs_isok(path):
    import os
    print( os.system( f'hdfs dfs -ls {path}' ) )
     
def hdfs_mkdir(hdfs_path):
    res = os_system( f"hdfs dfs -mkdir -p  '{hdfs_path}' ", doprint=True)

def hdfs_copy_local_to_hdfs(local_path, hdfs_path, overwrite=False):
    if overwrite: hdfs_rm_dir(hdfs_path)
    res = os_system( f"hdfs dfs -copyFromLocal '{local_path}'  '{hdfs_path}' ", doprint=True)

def hdfs_copy_hdfs_to_local(hdfs_path, local_path):
    res = os_system( f"hdfs dfs -copyToLocal '{hdfs_path}'  '{local_path}' ", doprint=True)

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


def hdfs_pd_write_parquet(df, hdfs_path=  'hdfs:///user/pppp/clean_v01.parquet/', 
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
        hdfs.rm(hdfs_path.replace("hdfs://", ""), recursive=True)
    hdfs.mkdir(hdfs_path.replace("hdfs://", ""))
    pq.write_to_dataset(table, root_path=hdfs_path,
                        partition_cols=partition_cols, filesystem=hdfs)
    
    flist = hdfs.ls( hdfs_path )  
    print(flist)


pd_write_file_hdfs   =  hdfs_pd_write_parquet
pd_read_parquet_hdfs =  hdfs_pd_read_parquet




def hdfs_download_parallel(from_dir="", to_dir="",  verbose=False, n_pool=1,   **kw):
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
  flist = [ t for t in hdfs.ls(from_dir) ]

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

         xi    = (filei,  to_dir + "/" + filei.split("/")[-1] )

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



def hive_sql_todf(sql, header_hive_sql:str='', verbose=1, save_path=None, **kwargs):
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

        if save_path is not None :
           fname = f'ztmp/hive_result/{sid}/'
           os.makedirs(os.path.dirname(fname), exist_ok=True)
           df.to_parquet( fname + '/table.parquet' )
           open(fname +'/sql.txt', mode='w').write(sql2)
           print('saved',  fname)

        print('hive table', df.columns, df.shape)
        return df

    except Exception as e:
        print(e)



def hdfs_dir_exists(path):
    return {0: True, 1: False}[subprocess.call(["hdfs", "dfs", "-test", "-e", path])]


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
    def convert_pyarrow():   
        dirin  = dir_ca + "/hdfs/a/*"
        dirout = dir_ca + "/hdfs/a_hive/"

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


def date_now(datenow:str="", fmt="%Y%m%d", add_days=0, add_hours=0, timezone='Asia/Tokyo', fmt_input="%Y-%m-%d", 
                returnval='str,int,datetime'):
    """ One liner for date Formatter
    Doc::

        datenow: 2012-02-12  or ""  emptry string for today's date.
        fmt:     output format # "%Y-%m-%d %H:%M:%S %Z%z"

        date_now('today',)    -->  "20200519" 
        date_now('now',timezone='Asia/Tokyo', fmt='%Y-%m-%d')    -->  "2020-05-19" 
        date_now('2022-10-05', timezone='Asia/Tokyo', fmt='%Y%m%d', add_days=-1, returnval='int')    -->  20220204 


    """
    from pytz import timezone as tzone
    import datetime

    if len(str(datenow )) >7 :  ## Not None
        now_utc = datetime.datetime.strptime( str(datenow), fmt_input)       
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

