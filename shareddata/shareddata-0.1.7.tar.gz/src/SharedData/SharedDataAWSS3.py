import os,sys
import logging
import subprocess
import boto3
import awscli
from pathlib import Path
import pandas as pd
from datetime import datetime,timedelta
import time
import pytz

from SharedData.Logger import Logger

def S3SyncDownloadDataFrame(path,shm_name):
    Logger.log.debug('AWS S3 Sync DataFrame %s...' % (shm_name))    

    awsfolder = os.environ['S3_BUCKET']+'/'
    awsfolder = awsfolder+str(Path(shm_name).parents[0])
    awsfolder = awsfolder.replace('\\','/')+'/'   
    dbfolder = str(path)
    dbfolder = dbfolder.replace('\\','/')+'/'
    env = os.environ.copy()
    env['PATH'] = sys.exec_prefix+r'\Scripts'

    process = subprocess.Popen(['aws','s3','sync',awsfolder,dbfolder,\
        '--profile',Logger.user,\
        '--exclude','*',\
        '--exact-timestamps',\
        '--include',shm_name.split('/')[-1]+'.json',\
        '--include',shm_name.split('/')[-1]+'.npy'],\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,\
        universal_newlines=True, shell=True, env=env)        
    
    while True:
        output = process.stdout.readline()
        if ((output == '') | (output == b''))\
                & (process.poll() is not None):
            break        
        if (output) and not (output.startswith('Completed')):
            Logger.log.debug('AWSCLI:'+output.strip())  

    rc = process.poll()
    success= rc==0
    if success:
        Logger.log.debug('AWS S3 Sync DataFrame %s,%s DONE!' % (Logger.user,shm_name))
    else:
        Logger.log.error('AWS S3 Sync DataFrame %s,%s ERROR!' % (Logger.user,shm_name))
        Logger.log.error('AWS S3 Sync DataFrame \"%s\"' % (''.join(process.stderr.readlines())))
    return success

def S3SyncDownloadTimeSeries(path,shm_name):    
    Logger.log.debug('AWS S3 sync download timeseries %s...' % (shm_name))
    awsfolder = os.environ['S3_BUCKET']+'/'+shm_name+'/' 
    env = os.environ.copy()
    env['PATH'] = sys.exec_prefix+r'\Scripts'
    process = subprocess.Popen(['aws','s3','sync',awsfolder,path,\
        '--profile',Logger.user,\
        '--exact-timestamps',\
        #'--delete',\
        '--exclude=shm_info.json'],\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,\
        universal_newlines=True, shell=True,env=env)
    
    while True:
        output = process.stdout.readline()
        if ((output == '') | (output == b''))\
                & (process.poll() is not None):
            break    
        if (output) and not (output.startswith('Completed')):
            Logger.log.debug('AWSCLI:'+output.strip())        

    rc = process.poll()
    success= rc==0
    if success:
        Logger.log.debug('AWS S3 Sync timeseries %s,%s DONE!' % (Logger.user,shm_name))
    else:
        Logger.log.error('AWS S3 Sync timeseries %s,%s ERROR!' % (Logger.user,shm_name))
        Logger.log.error('AWS S3 Sync timeseries \"%s\"' % (''.join(process.stderr.readlines())))
    return success

def S3SyncDownloadMetadata(pathpkl,name):
    
    Logger.log.debug('AWS S3 Sync download metadata %s...' % (name))
    folder=str(pathpkl.parents[0]).replace(\
        os.environ['DATABASE_FOLDER'],'')
    
    folder = folder.replace('\\','/')+'/'
    dbfolder = str(pathpkl.parents[0])
    dbfolder = dbfolder.replace('\\','/')+'/'
    awsfolder = os.environ['S3_BUCKET'] + folder    
    env = os.environ.copy()
    env['PATH'] = sys.exec_prefix+r'\Scripts'

    process = subprocess.Popen(['aws','s3','sync',awsfolder,dbfolder,\
        '--profile',Logger.user,\
        '--exclude','*',\
        '--exact-timestamps',\
        '--include',name.split('/')[-1]+'.pkl',\
        '--include',name.split('/')[-1]+'_SYMBOLS.pkl',\
        '--include',name.split('/')[-1]+'_SERIES.pkl',\
        '--include',name.split('/')[-1]+'.xlsx'],\
        #'--delete'],\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,\
        universal_newlines=True, shell=True,env=env)        
    
    while True:
        output = process.stdout.readline()
        if ((output == '') | (output == b''))\
                & (process.poll() is not None):
            break        
        if (output) and not (output.startswith('Completed')):
            Logger.log.debug('AWSCLI:'+output.strip())  
            
    rc = process.poll()
    success= rc==0
    if success:
        Logger.log.debug('AWS S3 Sync download metadata %s,%s DONE!' % (Logger.user,name))
    else:
        Logger.log.error('AWS S3 Sync download metadata %s,%s ERROR!' % (Logger.user,name))
        Logger.log.error('AWS S3 Sync download metadata \"%s\"' % (''.join(process.stderr.readlines())))
    return success

def S3Upload(localfilepath):
    remotefilepath = str(localfilepath).replace(\
            os.environ['DATABASE_FOLDER'],os.environ['S3_BUCKET'])   
    remotefilepath = remotefilepath.replace('\\','/')        
    localfilepath = str(localfilepath).replace('\\','/')              
      
    Logger.log.debug(Logger.user+' Uploading to S3 '+str(localfilepath)+' ...')
    try:                
        session = boto3.Session(profile_name=Logger.user)   
        s3 = session.resource('s3')
        bucket = s3.Bucket(os.environ['S3_BUCKET'].replace('s3://',''))
        bucket.upload_file(localfilepath,remotefilepath.replace(os.environ['S3_BUCKET'],'')[1:])
        Logger.log.debug(Logger.user+' Uploading to S3 '+str(localfilepath)+' DONE!')
    except Exception as e:
        Logger.log.error(Logger.user+' Uploading to S3 '+localfilepath+' ERROR! %s' % str(e))