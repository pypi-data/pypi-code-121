from abc import ABC, abstractmethod
import enum

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..actions import ZBSAction
    pass


class ISpecialInstructions(ABC):
    pass


class IActionHF(ABC):
    class Status(enum.Enum):
        NEW = 1
        PENDING = 2
        RUNNING = 3
        CANCELED = 4
        READY = 5
        HOLDING = 6
        REVERT = 7
        PAUSE = 8 # should stop
        STOPPED = 9 # action stopped

    @abstractmethod
    def get_action_id(self) -> str:
        raise NotImplementedError(
            "ActionHF 'get_action_id' is abstract, please implement")

    @abstractmethod
    def get_action_type(self) -> str:
        raise NotImplementedError(
            "ActionHF 'get_action_type' is abstract, please implement")

    @abstractmethod
    def get_status(self) -> Status:
        raise NotImplementedError(
            "ActionHF 'get_status' is abstract, please implement")

    @abstractmethod
    def set_status(self, status: Status):
        raise NotImplementedError(
            "ActionHF 'set_status' is abstract, please implement")

    @abstractmethod
    def get_special_instructions(self) -> ISpecialInstructions:
        raise NotImplementedError(
            "ActionHF 'get_special_instructions' is abstract, please implement")

    @abstractmethod
    def set_special_instructions(self, special_instructions: ISpecialInstructions):
        raise NotImplementedError(
            "ActionHF 'set_special_instructions' is abstract, please implement")


class IDeviceHF(ABC):

    @abstractmethod
    def get_dev_id(self) -> str:
        raise NotImplementedError(
            "DeviceHF 'get_dev_id' is abstract, please implement")

    @abstractmethod
    def get_size(self) -> int:
        raise NotImplementedError(
            "DeviceHF 'get_size' is abstract, please implement")

    @abstractmethod
    def get_usage(self) -> int:
        raise NotImplementedError(
            "DeviceHF 'get_usage' is abstract, please implement")

    @abstractmethod
    def get_unlock_ts(self) -> int:
        raise NotImplementedError(
            "DeviceHF 'get_unlock_ts' is abstract, please implement")

class IFileSystemHF(ABC):

    @abstractmethod
    def get_fs_id(self) -> str:
        raise NotImplementedError(
            "IFileSystemHF 'get_fs_id' is abstract, please implement")

    @abstractmethod
    def get_devices(self) -> Dict[str, IDeviceHF]:
        raise NotImplementedError(
            "IFileSystemHF 'get_devices' is abstract, please implement")

    @abstractmethod
    def get_existing_actions(self) -> Dict[str, IActionHF]:
        raise NotImplementedError(
            "IFileSystemHF 'get_existing_actions' is abstract, please implement")
