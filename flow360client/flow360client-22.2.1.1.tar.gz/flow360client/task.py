import time

from flow360client.httputils import flow360ApiGet, flow360ApiPut, flow360ApiPost, flow360ApiDelete

def UpdateTask(item):
    return flow360ApiPut(f'solver/task/{item.itemId}', item)

def NewTask(item):
    return flow360ApiPost(f'solver/task', item)

def GetTask(itemId):
    return flow360ApiGet(f'solver/task/{itemId}')

def DeleteTask(itemId):
    return flow360ApiDelete(f'solver/task/{itemId}')

def ListTask(type):
    return flow360ApiGet(f'solver/{type}/tasks')

def WaitOnTask(taskId, timeout=86400, sleepSeconds=10):
    startTime = time.time()
    while time.time() - startTime < timeout:
        try:
            info = GetTask(taskId)
            if info['status'] in ['error', 'success']:
                return info['status']
        except Exception as e:
            print('Warning : {0}'.format(str(e)))

        time.sleep(sleepSeconds)




