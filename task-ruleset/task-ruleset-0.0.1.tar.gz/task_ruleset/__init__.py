__version__ = "0.0.1"

from multiprocessing import Process, Manager
import os, sys, time

NGuests = 4
Rules = {}
InitTask = None
TasksAssignedToProcess = None

class Task:
    def __init__(self, TaskType, TaskKey, TaskData):
        self.TaskType = TaskType
        self.TaskKey = TaskKey
        self.TaskData = TaskData

def Host(id, sharedDict):
    global TasksAssignedToProcess

    for i in range(1, NGuests + 1):
        while i not in sharedDict.keys():
            pass

    TasksAssignedToProcess = [0] * (NGuests + 1)
    recvIdxs, sendIdxs = [0] * (NGuests + 1), [0] * (NGuests + 1)

    def sendMessageToGuest(guestIdx, msg):
        sharedDict[str(guestIdx) + "_toGuest_" + str(sendIdxs[guestIdx])] = msg
        sendIdxs[guestIdx] += 1
    
    def hasMessageFromGuest(guestIdx):
        if (key := str(guestIdx) + "_toHost_" + str(recvIdxs[guestIdx])) in sharedDict.keys():
            return key
        else:
            return False
    
    def readMessageFromGuest(guestIdx, key):
        MSG = sharedDict[key]
        del sharedDict[key]
        recvIdxs[guestIdx] += 1
        return MSG

    TaskMap = {}
    sendMessageToGuest(1, InitTask)

    while True:
        if len(sharedDict.keys()) == NGuests and len(TaskMap.keys()) == 0:
            for i in range(1, NGuests + 1):
                if sharedDict[i] != "WAITING":
                    break
            else:
                break
        
        for i in range(1, NGuests + 1):
            if key := hasMessageFromGuest(i):
                TASK = readMessageFromGuest(i, key)
                if TASK.TaskKey not in TaskMap.keys():
                    TaskMap[TASK.TaskKey] = (TASK.TaskType, [])
                TaskMap[TASK.TaskKey][1].extend(TASK.TaskData)
        
        if len(TaskMap.keys()) > 0:
            for key in list(TaskMap.keys()):
                if len(TaskMap[key][1]) >= Rules[TaskMap[key][0]][0]:
                    for w, i in sorted(zip(TasksAssignedToProcess[1:], range(1, NGuests + 1))):
                        if sharedDict[i] == "WAITING":
                            sendMessageToGuest(i, Task(TaskMap[key][0], key, TaskMap[key][1])); del TaskMap[key]
                            TasksAssignedToProcess[i] += 1
                            break
                    break

    for i in range(1, NGuests + 1):
        sendMessageToGuest(i, "EXIT")

def Guest(id, sharedDict):    
    sharedDict[id] = "READY"

    recvIdx, sendIdx = [0], [0]

    def hasMessageFromHost():
        if (key := str(id) + "_toGuest_" + str(recvIdx[0])) in sharedDict.keys():
            return key
        else:
            return False
    
    def readMessageFromHost(key):
        sharedDict[id] = "READING"
        MSG = sharedDict[key]
        del sharedDict[key]
        recvIdx[0] += 1
        return MSG
    
    def sendMessageToHost(msg):
        sharedDict[str(id) + "_toHost_" + str(sendIdx[0])] = msg
        sendIdx[0] += 1
    
    sharedDict[id] = "WAITING"
    while True:
        if key := hasMessageFromHost():
            TASK = readMessageFromHost(key)

            sharedDict[id] = "WORKING"
            if TASK == "EXIT":
                sharedDict[id] = "EXITING"
                return
            
            if TASK.TaskType in Rules.keys() or True:
                Rule = Rules[TASK.TaskType]
                NewTasks = Rule[1](TASK.TaskKey, TASK.TaskData)
                if NewTasks is not None and type(NewTasks) == type([]):
                    for newTask in NewTasks:
                        if type(newTask) == Task:
                            sendMessageToHost(newTask)
        
        else:
            sharedDict[id] = "WAITING"


def main():
    assert(NGuests > 0)
    assert(InitTask is not None)
    assert(type(InitTask.TaskData) == type([]))

    sharedDict = Manager().dict()

    processList = []
    for i in range(1, NGuests + 1):
        p = Process(target=Guest, args=(i, sharedDict))
        processList.append(p)
    
    for p in processList:
        p.start()
    Host(0, sharedDict)
    for p in processList:
        p.join()
