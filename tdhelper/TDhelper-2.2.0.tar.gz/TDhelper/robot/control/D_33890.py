from TDhelper.robot.control.device import absDevice


class device_D_33890(absDevice):
    def __init__(self, deviceName: str, revolveScope=(0, 180), reset=0.0):
        '''
            设备初始化
            - params:
            - deviceName: <str>, 设备名称.
            - revolveScope: <tuple>, 设备角度范围.
            - reset: <float>, 设备复位值.
        '''
        super(device_D_33890, self).__init__(deviceName, revolveScope, reset)


    def notify(self):
        print(self.name + ': 角度调整(' + str(self.currentValue)+"), 设备控制信号输出.")
        # todo 通知设备接口.

    def ctrl(self, v):
        if self.deviceStatus:
            if self.revolveScope[0] <= v <= self.revolveScope[1]:
                if v!= self.currentValue:
                    self.currentValue = v
                    self.ctrStatus= True
            else:
                raise Exception("%s 控制角度为：(%d,%d),您的控制信号(%d)超出范围." % (
                    self.name, self.revolveScope[0], self.revolveScope[1], v))
        else:
            print('%s 动力设备还没有就绪.' % self.name)
