"""Module containing the logic for connector adaptor"""

import re

from dgspoc.exceptions import AdaptorAuthenticationError

from dgspoc.constant import ECODE

from dgspoc.utils import MiscOutput


class Adaptor:
    def __init__(self, adaptor, *args, **kwargs):
        self.adaptor = adaptor.strip()
        if self.is_unreal_device_adaptor:
            addr = args[0]
            self.device = UnrealDeviceAdaptor(addr)
        else:
            fmt = '*** Need to implement "{}" adaptor'
            NotImplementedError(fmt.format(adaptor))

    @property
    def is_unreal_device_adaptor(self):
        result = re.match('(?i)unreal-?device$', self.adaptor)
        return bool(result)

    def connect(self):
        result = self.device.connect()
        if self.is_unreal_device_adaptor:
            if self.device.result.startswith('UnrealDeviceConnectionError:'):
                raise AdaptorAuthenticationError(self.device.result)
        return result

    def execute(self, *args, **kwargs):
        result = self.device.execute(*args, **kwargs)
        return result

    def configure(self, *args, **kwargs):
        result = self.device.configure(*args, **kwargs)
        return result

    def disconnect(self, *args, **kwargs):
        result = self.device.disconnect(*args, **kwargs)
        return result

    def reload(self, *args, **kwargs):
        result = self.device.reload(*args, **kwargs)
        return result

    def release(self, *args, **kwargs):
        result = self.device.release(*args, **kwargs)
        return result


class UnrealDeviceAdaptor:
    def __init__(self, address):
        self.address = str(address).strip()
        self.name = self.address
        self.result = ''
        self.exit_code = ECODE.SUCCESS

    @property
    def status(self):
        return True if self.exit_code == ECODE.SUCCESS else False

    def process(self, statement):
        result = MiscOutput.execute_shell_command(statement.strip())
        self.exit_code, self.result = result.exit_code, result.output
        print(self.result)
        return self.status

    def connect(self):
        fmt = 'unreal-device connect --host={}'
        unreal_statement = fmt.format(self.address)
        self.process(unreal_statement)
        return self.status

    def execute(self, *args, **kwargs):
        addr = kwargs.get('name', self.address)
        cmdline = args[0]
        fmt = 'unreal-device execute {} --host={}'
        unreal_statement = fmt.format(cmdline, addr)
        self.process(unreal_statement)
        return self.result

    def configure(self, *args, **kwargs):
        addr = kwargs.get('name', self.address)
        cfg_reference = args[0]
        fmt = 'unreal-device configure {} --host={}'
        unreal_statement = fmt.format(cfg_reference, addr)
        self.process(unreal_statement)
        return self.result

    def disconnect(self, *args, **kwargs):      # noqa
        addr = kwargs.get('name', self.address)
        fmt = 'unreal-device disconnect --host={}'
        unreal_statement = fmt.format(addr)
        self.process(unreal_statement)
        return self.status

    def reload(self, *args, **kwargs):      # noqa
        addr = kwargs.get('name', self.address)
        fmt = 'unreal-device reload --host={}'
        unreal_statement = fmt.format(addr)
        self.process(unreal_statement)
        return self.status

    def release(self, *args, **kwargs):     # noqa
        addr = kwargs.get('name', self.address)
        fmt = 'unreal-device release --host={}'
        unreal_statement = fmt.format(addr)
        self.process(unreal_statement)
        return self.status
