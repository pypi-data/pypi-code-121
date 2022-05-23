import logging

from mpi4py import MPI

from typing import Any, List, Optional, Tuple


from JuMonC.tasks import taskPool
from JuMonC.tasks.taskSwitcher import task_switcher
from JuMonC.models import dataStore



logger = logging.getLogger(__name__)



__comm = MPI.COMM_WORLD
__keep_running = True



def waitForCommands() -> None:
    taskPool.setupTaskPool()
    while __keep_running:
        task_switcher.executeNextTask()


def sendCommand(data: List[int]) -> None:
    __comm.bcast(data, root=0)


def gatherResult(dataID: int, command: List[int]) -> None:
    __comm.bcast(dataID, root=0)
    (rec_res_avai, result) = testResultAvaiable(dataID)
    
    if  rec_res_avai == 1:
        resultCom = __comm.reduce(result, op = MPI.SUM, root = 0)
        dataStore.removeResult(dataID)
        dataStore.addResult(dataID, resultCom)
    else: 
        logging.info("Gathering resheduled, command: %s", str(command))
        #taskSwitcher.tasks.add(command)

        
def testResultAvaiable(dataID: int) -> Tuple[int, Optional[Any]]:
    result_avaiable: int = 0
    result: Optional[Any] = None
    try:
        result = dataStore.getResult(dataID)
        result_avaiable = 1
    except KeyError:
        result_avaiable = 0

    rec_res_avai: int = 0
    __comm.Allreduce(result_avaiable, rec_res_avai, op=MPI.PROD)
    return (rec_res_avai, result)