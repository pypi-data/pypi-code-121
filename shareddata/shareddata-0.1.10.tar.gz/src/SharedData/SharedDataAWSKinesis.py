import os
import logging
import subprocess
import boto3
import awscli
from pathlib import Path
import pandas as pd
from datetime import datetime,timedelta
import time
import pytz
import json

# LOGS
class KinesisLogStreamHandler(logging.StreamHandler):
    #reference: https://docs.python.org/3/library/logging.html#logging.LogRecord
    def __init__(self,user='guest'):
        # By default, logging.StreamHandler uses sys.stderr if stream parameter is not specified
        logging.StreamHandler.__init__(self)
        
        self.user = user
        self.datastream = None
        self.stream_buffer = []


        try:
            session = boto3.Session(profile_name=self.user)
            self.datastream = session.client('kinesis')
        except Exception:
            print('Kinesis client initialization failed.')

        self.stream_name = os.environ['LOG_STREAMNAME']
        
    def emit(self, record):
        try:
            #msg = self.format(record)
            user = os.environ['USERNAME']+'@'+os.environ['COMPUTERNAME']
            timezone = pytz.timezone("UTC")
            dt = datetime.utcfromtimestamp(record.created)
            dt= timezone.localize(dt)
            asctime = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
            msg = {
                    'user_name': user,
                    'asctime': asctime,
                    'logger_name': record.name,
                    'level': record.levelname,
                    'message': str(record.msg).replace('\'','\"'),
                    #'function_name': record.funcName,
                    #'file_name': record.filename,                
                }   
            msg = json.dumps(msg)
            if self.datastream:
                self.stream_buffer.append({
                    'Data': str(msg).encode(encoding="UTF-8", errors="strict"),
                    'PartitionKey' : user,
                })
            else:
                stream = self.stream
                stream.write(msg)
                stream.write(self.terminator)

            self.flush()
        except Exception:
            self.handleError(record)

    def flush(self):
        self.acquire()
        try:
            if self.datastream and self.stream_buffer:
                self.datastream.put_records(
                    StreamName=self.stream_name,
                    Records=self.stream_buffer                   
                )

                self.stream_buffer.clear()
        except Exception as e:
            print("An error occurred during flush operation.")
            print(f"Exception: {e}")
            print(f"Stream buffer: {self.stream_buffer}")
        finally:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
            self.release()

class KinesisLogStreamConsumer():
    def __init__(self,user='guest'):
        self.user = user
        self.logfilepath = Path(os.environ['DATABASE_FOLDER']+'\\Logs\\')
        self.logfilepath = self.logfilepath / (datetime.utcnow().strftime('%Y%m%d')+'.log')
        self.lastlogfilepath = Path(os.environ['DATABASE_FOLDER']+'\\Logs\\')
        self.lastlogfilepath = self.lastlogfilepath / ((datetime.utcnow()+timedelta(days=-1)).strftime('%Y%m%d')+'.log')

    def readLogs(self):
        self.logfilepath = Path(os.environ['DATABASE_FOLDER']+'\\Logs\\')
        self.logfilepath = self.logfilepath / (datetime.utcnow().strftime('%Y%m%d')+'.log')
        self.lastlogfilepath = Path(os.environ['DATABASE_FOLDER']+'\\Logs\\')
        self.lastlogfilepath = self.lastlogfilepath / ((datetime.utcnow()+timedelta(days=-1)).strftime('%Y%m%d')+'.log')

        self.dflogs = pd.DataFrame([])
        if self.logfilepath.is_file():
            self.dflogs = pd.read_csv(self.logfilepath,header=None,sep=';',\
                engine='python',error_bad_lines=False,warn_bad_lines=False)
            self.dflogs.columns = ['shardid','sequence_number','user_name','asctime','logger_name','level','message']
        
        if self.lastlogfilepath.is_file():
            _dflogs = pd.read_csv(self.lastlogfilepath,header=None,sep=';',\
                engine='python',error_bad_lines=False,warn_bad_lines=False)
            _dflogs.columns = ['shardid','sequence_number','user_name','asctime','logger_name','level','message']
            self.dflogs = pd.concat([_dflogs,self.dflogs],axis=0)

        return self.dflogs
    
    def connect(self):                
        session = boto3.Session(profile_name=self.user)
        self.client = session.client('kinesis')
        self.stream = self.client.describe_stream(StreamName=os.environ['LOG_STREAMNAME'])
        if self.stream and 'StreamDescription' in self.stream:
            self.stream = self.stream['StreamDescription']
            i=0    
            for i in range(len(self.stream['Shards'])):        
                shardid = self.stream['Shards'][i]['ShardId']
                if not self.dflogs.empty and (shardid in self.dflogs['shardid'].values):            
                    seqnum = self.dflogs[self.dflogs['shardid']==shardid].iloc[-1]['sequence_number']
                    shard_iterator = self.client.get_shard_iterator(
                        StreamName=self.stream['StreamName'],
                        ShardId=self.stream['Shards'][i]['ShardId'],
                        ShardIteratorType='AFTER_SEQUENCE_NUMBER',
                        StartingSequenceNumber=seqnum
                        )
                else:
                    shard_iterator = self.client.get_shard_iterator(
                        StreamName=self.stream['StreamName'],
                        ShardId=self.stream['Shards'][i]['ShardId'],                
                        ShardIteratorType='TRIM_HORIZON'                
                        )
                self.stream['Shards'][i]['ShardIterator'] = shard_iterator['ShardIterator']
        if self.stream['StreamStatus'] != 'ACTIVE':
            raise Exception('Stream status %s' % (self.stream['StreamStatus']))
        
        return self.stream

    def loop(self):
        while True:        
            for i in range(len(self.stream['Shards'])):
                response = self.client.get_records(\
                    ShardIterator = self.stream['Shards'][i]['ShardIterator'],\
                    Limit = 100)
                self.stream['Shards'][i]['ShardIterator'] = response['NextShardIterator']
                if len(response['Records'])> 0:
                    for r in response['Records']:
                        try:
                            rec = r['Data'].decode(encoding="UTF-8", errors="strict")                        
                            rec = json.loads(rec.replace("\'", "\"").replace(';',','))
                            line = '%s;%s;%s;%s;%s' % (rec['user_name'],rec['asctime'],\
                                rec['logger_name'],rec['level'],rec['message']) 
                            print(line)
                            line = '%s;%s;%s;%s;%s;%s;%s' % (self.stream['Shards'][i]['ShardId'],\
                                r['SequenceNumber'],rec['user_name'],rec['asctime'],\
                                rec['logger_name'],rec['level'],rec['message'])                     
                            dt = datetime.strptime(rec['asctime'][:-5], '%Y-%m-%dT%H:%M:%S')
                            logfilepath = Path(os.environ['DATABASE_FOLDER']+'\\Logs\\')
                            logfilepath =logfilepath / (dt.strftime('%Y%m%d')+'.log')
                            if not logfilepath.parents[0].is_dir():
                                os.makedirs(logfilepath.parents[0])
                            with open(logfilepath,'a+',encoding = 'utf-8') as f:
                                f.write(line.replace('\n',' ').replace('\r',' ')+'\n')  
                        except Exception as e:
                            print('Invalid record:'+str(rec))
                            print('Invalid record error:'+str(e))
            time.sleep(1)
        
# REAL TIME
class KinesisStreamProducer():
    def __init__(self,stream_name, profile_name):
        self.stream_name = stream_name
        self.profile_name = profile_name
        self.datastream = None
        self.stream_buffer = []
        try:
            session = boto3.Session(profile_name=self.profile_name)
            self.datastream = session.client('kinesis')
        except Exception:
            print('Kinesis client initialization failed.')

    def produce(self, record, partitionkey):    
        _rec = json.dumps(record)            
        self.stream_buffer.append({
            'Data': str(_rec).encode(encoding="UTF-8", errors="strict"),
            'PartitionKey' : partitionkey,
        })
        self.datastream.put_records(
                    StreamName=self.stream_name,
                    Records=self.stream_buffer                   
                )
        self.stream_buffer = []

class KinesisStreamConsumer():
    def __init__(self,stream_name, profile_name):
        self.stream_name = stream_name
        self.profile_name = profile_name    
        self.stream_buffer = []
        self.get_stream()

    def get_stream(self):
        print('Initializing stream...')
        session = boto3.Session(profile_name=self.profile_name)
        self.client = session.client('kinesis')
        self.stream = self.client.describe_stream(StreamName=self.stream_name)
        if self.stream and 'StreamDescription' in self.stream:
            self.stream = self.stream['StreamDescription']
            i=0    
            for i in range(len(self.stream['Shards'])):        
                shardid = self.stream['Shards'][i]['ShardId']
                shard_iterator = self.client.get_shard_iterator(
                    StreamName=self.stream['StreamName'],
                    ShardId=self.stream['Shards'][i]['ShardId'],                
                    ShardIteratorType='LATEST'                
                    )
                self.stream['Shards'][i]['ShardIterator'] = shard_iterator['ShardIterator']
        if self.stream['StreamStatus'] != 'ACTIVE':
            raise Exception('Stream status %s' % (self.stream['StreamStatus']))
        print('Initializing stream DONE!')
                
    def consume(self):
        success=False

        for i in range(len(self.stream['Shards'])):
            try:
                response = self.client.get_records(\
                    ShardIterator = self.stream['Shards'][i]['ShardIterator'],\
                    Limit = 100)
                success = True
                self.stream['Shards'][i]['ShardIterator'] = response['NextShardIterator']
                if len(response['Records'])> 0:
                    for r in response['Records']:
                        try:
                            rec = json.loads(r['Data'])
                            self.stream_buffer.append(rec)
                        except Exception as e:
                            print('Invalid record:'+str(r['Data']))
                            print('Invalid record:'+str(e))                
                
            except Exception as e:
                print('Kinesis consume exception:%s' % (e))
                break

        return success
            
     