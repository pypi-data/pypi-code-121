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