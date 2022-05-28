from abc import ABC, abstractmethod

class AsyncTask(ABC):
    @abstractmethod
    async def initialize_async(self) -> None:
        pass

    @abstractmethod
    async def run_async(self) -> None:
        pass

    @abstractmethod
    async def stop_async(self) -> None:
        pass