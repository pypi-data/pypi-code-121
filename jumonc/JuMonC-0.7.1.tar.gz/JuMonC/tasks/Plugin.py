class Plugin:
    works = None
    
    def __init__(self) -> None:
        """Base class for all plugins to use."""
    
    def isWorking(self) -> bool:
        if self.works is None:
            self.works = self._isWorking()
            return self.works
        return self.works
    
    def _isWorking(self) -> bool:
        raise NotImplementedError("Please Implement this method")