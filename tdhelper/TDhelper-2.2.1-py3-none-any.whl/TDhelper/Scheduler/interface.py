from TDhelper.Scheduler.base import *

import abc
import six
import asyncio

@six.add_metaclass(abc.ABCMeta)
class InterfaceScheduler(Scheduler):
    @abc.abstractmethod
    def __init__(self,name,plugin,taskType="interval",startTime=None,sleep=0):
        """Init

            Params:
                name:taskName
                plugin:call task module
                taskType:task type
                    realtime:run at now
                    interval:loop run and sleep N millisecond,default value
                    timing:run at one datetime
                startTime:first run time
                sleep:sleep millisecond
        """
        super(InterfaceScheduler,self).__init__(name,plugin,taskType,startTime,sleep)

    @abc.abstractmethod
    async def run(self,*args,**kw):
        """Run process
        """