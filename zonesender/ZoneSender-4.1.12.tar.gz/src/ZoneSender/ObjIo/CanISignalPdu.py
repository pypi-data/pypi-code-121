from copy import copy
import typing
import copy
from .ZoneSenderObject import ZoneSenderObject


class CanISignalIPdu(ZoneSenderObject):
    ''' CanISignalIPdu 对象，用来描述一个 CanISignalIPdu
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
        self.data = []

    def __str__(self) -> str:
        # return super().__str__()
        return 'name: {0} data: {1}'.format(self.name, self.data)
    
    