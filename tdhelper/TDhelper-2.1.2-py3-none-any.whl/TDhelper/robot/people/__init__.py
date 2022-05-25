from enum import Enum
from threading import Thread


class actionMode(Enum):
    slow = 0
    middle = 1
    quick = 2


class action:
    def __init__(self):
        self.actions = {}

    def loadActionScript(self, scriptConfig: dict):
        '''
            装载动作脚本
            - params:
            -   scriptConfig: <dict>, 脚本字典. 格式: {"KEY值":脚本对象}
        '''
        if scriptConfig:
            for k, v in scriptConfig.items():
                self.actions[k] = v
        else:
            raise Exception("动作脚本不能为空.")

    def do(self, scriptKey, mode: actionMode):
        '''
            执行动作脚本
            - params:
            -   scriptKey: <str>, 脚本KEY值
            -   mode: <actionMode>, 模式
        '''
        self.actions[scriptKey].do(mode)

    def stop(self, scriptKey):
        '''
            停止执行脚本
            - params:
            -   scriptKey: <str>, 脚本Key值
        '''
        self.actions[scriptKey].stop()

    def stopActionListen(self, scriptKey):
        self.actions[scriptKey].stopListen()
