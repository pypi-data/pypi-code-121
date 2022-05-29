import functools
import platform
from enum import Enum


class OSType(str, Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MAC = "Mac"

    @property
    def name(self) -> str:
        if self.value == "Windows":
            return "Windows"
        elif self.value == "Linux":
            return "Linux"
        elif self.value == "Mac":
            return "Darwin"
        else:
            raise NotImplementedError(f"Unknown OS type: {self.value}")


def run_in(os_type: OSType):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if platform.system() != os_type.name:
                print(f"Skipping test {func.__name__} on non-{os_type.value} platform")
                return
            return func(*args, **kwargs)

        return wrapper

    return decorator
