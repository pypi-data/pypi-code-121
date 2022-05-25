from TDhelper.robot.control.device import absDevice

class joint:
    '''
        关节基础类, 活动关节控制.
    '''
    def __init__(self, name, powerSystem:dict= None):
        '''
            关节初始化
            - params:
            -   name: <str>, 关节名称.
            -   powerSystem: <dict>, 动力控制模块。{"updown": device,"leftright": device}
        '''
        # self.id= id
        self.name= name
        self.powerSystem= {
            "updown":[None, 0.0], # key:方向指令，arrary[0]:动力设备, arrary[1]:当前值
            "leftright":[None, 0.0]
        }
        if powerSystem:
            if "updown" in powerSystem:
                if isinstance(powerSystem['updown'], absDevice):
                    self.powerSystem['updown'][0]= powerSystem['updown']
                else:
                    raise Exception("%s->updown不是设备." % self.name)
            if "leftright" in powerSystem:
                if isinstance(powerSystem['updown'], absDevice):
                    self.powerSystem["leftright"][0]= powerSystem["leftright"]
                else:
                    raise Exception("%s->leftright不是设备." % self.name)
        else:
            raise Exception("动力控制模块不能为空,至少需要绑定一个动力模块.")
    
    def action(self, actionStruct:dict):
        '''
            控制动作
            - params:
            -   actionStruct: <dict>, 动作指令. 格式：{ "updown": 28, "leftrigth": 40}
        '''
        if actionStruct:
            for action, v in actionStruct.items():
                if self.powerSystem[action.lower()][0]:
                    status =self.powerSystem[action.lower()][0].ctrl(v)
                    if status:
                        self.powerSystem[action.lower][1]= v
                else:
                    raise Exception("%s 动力设备不支持 %s 指令." % (self.name, action.lower()))
        else:
            raise Exception('参数不能为空.')

    def reset(self):
        for k,v in self.powerSystem.items():
            if v[0]:
                v[0].reset()

