from copy import copy
import typing
import copy
from .ZoneSenderObject import ZoneSenderObject


class CanFrame(ZoneSenderObject):
    ''' CanFrame 对象，用来描述一个 CanFrame
    '''
    def __init__(
        self,
        name: 'str',
        channel: 'int',
        context: 'dict' = dict(),
        ) -> None:
        ...
        # #####################################
        super().__init__()
        self.name = name
        self.channel = channel
        self.context = copy.deepcopy(context)
        self.dlc = 0
        self.id = 0
        self.data = []

    def __str__(self) -> str:
        # return super().__str__()
        return 'name: {0} data: {2}'.format(self.name, self.data)