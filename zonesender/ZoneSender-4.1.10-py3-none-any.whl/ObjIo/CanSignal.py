import typing
import copy
from .ZoneSenderObject import ZoneSenderObject


class CanSignal(ZoneSenderObject):
    ''' CanSignal 对象，用来描述一个 CAN Signal
    '''
    def __init__(
        self,
        name: 'str',
        channel: 'int',
        data: 'float' = 0.0,
        mean: 'str' = '',
        unit: 'str' = '',
        context: 'dict' = dict(),
        ) -> None:
        ...
        # #####################################
        super().__init__()
        self.name = name
        self.data = data
        self.channel = channel
        self.mean = mean
        self.unit = unit
        self.context = copy.deepcopy(context)

    def __str__(self) -> str:
        # return super().__str__()
        return 'name: {0} channel: {1} value: {2} mean: {3}'.format(self.name, self.channel, self.data, self.mean)