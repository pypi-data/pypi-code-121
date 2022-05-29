import typing
import copy
from .ZoneSenderObject import ZoneSenderObject


class CanMessage(ZoneSenderObject):
    ''' CanMessage 对象，用来描述一个 CanMessage
    '''
    def __init__(
        self,
        arbitration_id: 'int',
        channel: 'int',
        dlc: 'int' = 0,
        data: typing.List['int'] = [],
        is_fd: 'bool' = False,
        is_extended_id: 'bool' = False,
        is_remote_frame: 'bool' = False,
        context: 'dict' = dict(),
        ) -> None:
        ...
        # #####################################
        super().__init__()
        self.arbitration_id = arbitration_id
        self.is_extended_id = is_extended_id
        self.is_remote_frame = is_remote_frame
        self.channel = channel
        self.dlc = dlc
        self.data = data
        self.is_fd = is_fd
        self.context = copy.deepcopy(context)

    def __str__(self) -> str:
        # return super().__str__()
        return 'arbitration_id: {0} data: {1}'.format(hex(self.arbitration_id).upper(), self.data)
