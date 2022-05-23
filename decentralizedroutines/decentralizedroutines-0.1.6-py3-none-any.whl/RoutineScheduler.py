import os,glob,subprocess,pytz
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from tzlocal import get_localzone 
local_tz = pytz.timezone(str(get_localzone()))

from SharedData.Logger import Logger
from SharedData.SharedDataAWSKinesis import KinesisLogStreamConsumer,KinesisStreamProducer

class RoutineScheduler:

    def __init__(self,stream_name='deepportfolio-workerpool',profile_name='master'):
        self.consumer = KinesisLogStreamConsumer()
        self.producer = KinesisStreamProducer(stream_name, profile_name)

    def LoadSchedule(self):
        self.schedule=[]
        if not 'SCHEDULE_PATH' in os.environ:
            raise Exception('SCHEDULE_PATH not found in environ!')
        else:
            schedpath = Path(os.environ['SCHEDULE_PATH'])

        today = datetime.now().date()
        year = today.timetuple()[0]
        month = today.timetuple()[1]
        day = today.timetuple()[2]        

        _sched = pd.read_excel(schedpath)
        sched = pd.DataFrame()
        for i,s in _sched.iterrows():
            runtimes = s['Run Times'].split(',')
            for t in runtimes:
                hour = int(t.split(':')[0])
                minute = int(t.split(':')[1])
                dttm = local_tz.localize(datetime(year,month,day,hour,minute))
                s['Run Times'] = dttm
                sched = sched.append(s)       

        sched = sched.sort_values(by=['Run Times','Name']).reset_index(drop=True)
        sched['Status'] = np.nan
        sched['Last Message'] = np.nan
        self.schedule = sched
        return sched

    def RefreshLogs(self):
        sched = self.schedule                
        local_tz = pytz.timezone(str(get_localzone()))
        # RefreshLogs
        dflogs = self.consumer.readLogs()
        if not dflogs.empty:
            dflogs = dflogs[dflogs['asctime'].notnull()].copy()
            dflogs['asctime'] = pd.to_datetime(dflogs['asctime'])
            dflogs['asctime'] = [dt.astimezone(tz=local_tz) for dt in dflogs['asctime']]

            i=0
            for i in sched.index:
                r = sched.loc[i]
                idx = dflogs['logger_name']==r['Script']
                idx = (idx) & (dflogs['user_name']==r['Computer'])
                idx = (idx) & (dflogs['asctime']>=r['Run Times'])    
                if np.any(idx):    
                    sched.loc[i,'Last Message'] = dflogs[idx].iloc[-1]['message']   

                                
            dferr = dflogs[dflogs['message']=='ROUTINE ERROR!']
            dferr = dferr.reset_index(drop=True).sort_values(by='asctime')
            i=0
            for i in dferr.index:
                r = dferr.iloc[i]
                idx = sched['Script']==r['logger_name']
                idx = (idx) & (sched['Computer']==r['user_name'])
                idx = (idx) & (r['asctime']>=sched['Run Times'])
                if idx.any():
                    ids = idx[::-1].idxmax()
                    sched.loc[ids,'Status'] = 'ERROR'
                    idx = sched.loc[idx,'Status'].isnull()
                    idx = idx.index[idx]
                    sched.loc[idx,'Status'] = 'EXPIRED'

            compl = dflogs[dflogs['message']=='ROUTINE COMPLETED!'].reset_index(drop=True).sort_values(by='asctime')
            i=0
            for i in compl.index:
                r = compl.iloc[i]
                idx = sched['Script']==r['logger_name']
                idx = (idx) & (sched['Computer']==r['user_name'])
                idx = (idx) & (r['asctime']>=sched['Run Times'])
                if idx.any():
                    ids = idx[::-1].idxmax()
                    sched.loc[ids,'Status'] = 'COMPLETED'
                    idx = sched.loc[idx,'Status'].isnull()
                    idx = idx.index[idx]
                    sched.loc[idx,'Status'] = 'EXPIRED'

        self.schedule = sched
        return sched

    def getPendingRoutines(self):
        sched = self.schedule
        local_tz = pytz.timezone(str(get_localzone()))
        
        idx = sched['Status'].isnull()
        idx = (idx) & (sched['Run Times']<=datetime.now().astimezone(tz=local_tz))
        dfpending = sched[idx]        
        for i in dfpending.index:
            r = dfpending.loc[i]    
            if not str(r['Dependencies'])=='nan':
                run=True
                dependencies = r['Dependencies'].replace('\n','').split(',')
                dep=dependencies[0]
                for dep in dependencies:
                    computer = dep.split(':')[0]
                    script = dep.split(':')[1]
                    idx = sched['Computer']==computer
                    idx = (idx) & (sched['Script']==script)
                    idx = (idx) & (sched['Run Times']<=datetime.now().astimezone(tz=local_tz))
                    ids = sched.index[idx]
                    if len(ids)==0:
                        Logger.log.error('Dependency not scheduled for '+r['Computer']+':'+r['Script'])
                    else:
                        if not str(sched.loc[ids[-1],'Status']) == 'COMPLETED':
                            run=False
                if run:
                    sched.loc[i,'Status'] = 'PENDING'
            else:
                sched.loc[i,'Status'] = 'PENDING'
        
        self.schedule=sched
        return sched

    def RunPendingRoutines(self):   
        sched = self.schedule
        
        # Run pending routines
        dfpending = sched[sched['Status']=='PENDING']
        for i in dfpending.index:
            r = dfpending.loc[i]
            if str(r['Last Message'])=='nan':
                target = r['Computer']    
                repo = r['Script'].split('\\')[0]
                routine = r['Script'].replace(repo,'')[1:]+'.py'
                data = {
                    "sender" : "MASTER",
                    "job" : "routine",
                    "target" : target,        
                    "repo" : repo,
                    "routine" : routine
                }
                self.producer.produce(data,'command')
                sched.loc[r.name,'Status'] = 'RUNNING'
                Logger.log.info('Command to run %s:%s sent!' % (target,r['Script']))
        
        self.schedule = sched
        return sched



