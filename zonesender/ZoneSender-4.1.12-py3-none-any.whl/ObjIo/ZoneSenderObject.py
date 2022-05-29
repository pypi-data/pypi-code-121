import typing
import uuid
import copy

class ZoneSenderObject(object):
    ''' ZoneSender 中的基础数据对象
    '''
    def __init__(self) -> None:
        # self._triggerFuntion = None
        self.name = uuid.uuid4().hex
        self.context = dict()
    
    @staticmethod
    def From(obj):
        ''' [static] 从 obj 中构造 对象
        :param obj: 需要重写实现具体的功能
        '''
        return None

    def ToDict(self) -> 'dict':
        ''' 转成 dict 数据结构
        :return: dict 该数据结构的 dict 表达
        '''
        return dict()