# PROPRIETARY LIBS
import os,sys,time
from decentralizedroutines.RoutineScheduler import RoutineScheduler
from datetime import datetime

from SharedData.Logger import Logger
logger = Logger(__file__,'master')
from SharedData.SharedDataAWSKinesis import KinesisStreamConsumer,KinesisStreamProducer

Logger.log.info('Routine schedule starting...')

stream_name='deepportfolio-workerpool'
profile_name='master'
producer = KinesisStreamProducer(stream_name, profile_name)
GIT_TOKEN=os.environ['GIT_TOKEN']
GIT_ACRONYM=os.environ['GIT_ACRONYM']
GIT_SERVER=os.environ['GIT_SERVER']
data = {
    "sender" : "MASTER",
    "target" : "ALL",
    "job" : "gitpwd",    
    "GIT_TOKEN" : GIT_TOKEN,
    "GIT_ACRONYM" : GIT_ACRONYM,
    "GIT_SERVER" : GIT_SERVER
}
producer.produce(data,'command')

Logger.log.info('Sent git credentials')

sched = RoutineScheduler()
sched.LoadSchedule()
sched.RefreshLogs()
sched.getPendingRoutines()

Logger.log.info('Routine schedule STARTED!')
time.sleep(15)
while(True):
    print('',end='\r')
    print('Running Schedule %s' % (str(datetime.now())),end='')
    if sched.schedule['Run Times'][0].date()<datetime.now().date():
        print('')
        print('Reloading Schedule %s' % (str(datetime.now())))
        print('')
        sched.LoadSchedule()
        sched.RefreshLogs()
        sched.getPendingRoutines()

    sched.RefreshLogs()
    sched.getPendingRoutines()
    sched.RunPendingRoutines()    
    time.sleep(15) 