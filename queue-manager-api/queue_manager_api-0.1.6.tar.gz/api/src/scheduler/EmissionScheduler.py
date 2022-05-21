from python_framework import SchedulerType
from python_framework import Scheduler, SchedulerMethod, WeekDay, WeekDayConstant


@Scheduler(muteLogs=True)
class EmissionScheduler:


    @SchedulerMethod(SchedulerType.INTERVAL, seconds=1, instancesUpTo=5)
    def updateAllModifiedFromMemory(self) :
        self.service.emission.updateAllModifiedFromMemory()


    @SchedulerMethod(SchedulerType.INTERVAL, seconds=0.1, instancesUpTo=100)
    def sendAllAcceptedFromOneQueue(self) :
        self.service.emission.sendAllAcceptedFromOneQueue()
