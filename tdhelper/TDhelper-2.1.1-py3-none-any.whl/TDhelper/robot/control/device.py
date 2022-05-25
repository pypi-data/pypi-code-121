from abc import ABCMeta, abstractmethod
import threading
import time


class absDevice(threading.Thread):
    def __init__(self, deviceName: str, revolveScope=(0, 180), reset=0.0):
        threading.Thread.__init__(self)
        #  self.id= id
        self.name = deviceName  # 设备名称.
        self.revolveScope = revolveScope  # 可转动范围限制.
        self.currentValue = -1  # 当前设备状态值.
        self.resetValue = reset  # 复位参数.
        self.ctrStatus = False  # 控制状态
        self.deviceStatus = False  # 设备状态
        self.start()

    def run(self):
        count = 0
        while True:
            if count == 0:
                count += 1
                self.deviceStatus= True
                print("%s 动力设备准备就绪." % self.name)
            if self.ctrStatus:
                self.notify()
            self.ctrStatus = False
            time.sleep(0.1)

    def reset(self):
        self.ctrl(self.resetValue)

    @abstractmethod
    def notify(self):
        '''
            通知硬件设备控制.
        '''
        pass

    @abstractmethod
    def ctrl(self, scope: float = 0.0):
        '''
        控制接口
        - params
        -   scope: <float>, 控制舵机旋转到多少度.
        '''
        pass
