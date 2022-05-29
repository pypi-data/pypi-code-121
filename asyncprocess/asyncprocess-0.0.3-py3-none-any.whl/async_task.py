from abc import ABC, abstractmethod

class AsyncTask(ABC):
    async def initialize_async(self) -> None:
        pass

    @abstractmethod
    async def run_async(self) -> None:
        pass

    async def stop_async(self) -> None:
        pass