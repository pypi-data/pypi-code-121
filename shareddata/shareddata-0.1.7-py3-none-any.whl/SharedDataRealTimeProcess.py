import os,time,sys
import pandas as pd
import numpy as np
from pathlib import Path

from SharedData.Logger import Logger
logger = Logger(__file__)
from SharedData.SharedData import SharedData
from SharedData.SharedDataAWSKinesis import KinesisStreamConsumer


try:
    if len(sys.argv)>=2:
        DATABASE = str(sys.argv[1])
    else:
        DATABASE = 'MarketData'

    if len(sys.argv)>=3:
        SLEEP_TIME = int(sys.argv[2])
    else:
        SLEEP_TIME = 5

    if len(sys.argv)>=4:
        PLOT_MESSAGES = bool(sys.argv[3])
    else:
        PLOT_MESSAGES = False


    streamname = os.environ['BASE_STREAM_NAME']+'-'+DATABASE.lower()
    profilename = Logger.user
    user = os.environ['USER_COMPUTER']

    Logger.log.info('Starting SharedData real time'+\
        ' subscription database:%s' % (DATABASE))

    consumer = KinesisStreamConsumer(streamname,profilename)
    shdata = SharedData(DATABASE,sync_frequency_days=0)

    Logger.log.info('SharedData real time'+\
        ' subscription database:%s STARTED!' % (DATABASE))

    today = pd.Timestamp(pd.Timestamp.now().date())
    lastdate = today
    while True:
        today = pd.Timestamp(pd.Timestamp.now().date())
        wd = shdata['WATCHDOG']['D1']
        dfwatchdog = wd[today]
        if dfwatchdog.empty:
            df = pd.DataFrame(
                time.time(),
                index = [shdata.database],
                columns = ['watchdog']
            )
            wd[today] = df        
        
        dfwatchdog.loc[DATABASE,'watchdog'] = time.time()

        consumer.consume()
        for msg in consumer.stream_buffer:
            if PLOT_MESSAGES:
               print(str(msg))
               
            if msg['sender'] != user:
                if msg['msgtype']=='df':
                    tag = pd.Timestamp(msg['tag'])
                    data = np.array(msg['data'])
                    df = shdata[msg['feeder']][msg['period']][tag]
                    df.loc[msg['idx'],msg['col']] = data
                elif msg['msgtype']=='ts':
                    data = np.array(msg['data'])
                    idx = pd.to_datetime(msg['idx'])
                    df = shdata[msg['feeder']][msg['period']][msg['tag']]
                    df.loc[idx,msg['col']] = data

        consumer.stream_buffer = []        
        time.sleep(SLEEP_TIME + SLEEP_TIME*np.random.rand() - SLEEP_TIME/2)
except Exception as e:        
    Logger.log.error('SharedData real time'+\
        ' subscription database:%s ERROR: %s!' % (DATABASE,str(e)))