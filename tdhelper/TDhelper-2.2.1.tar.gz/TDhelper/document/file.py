import os

class stream:
    '''
    未完成
    '''
    def __init__(self, streamPath):
        self._handle= None
        if self._exsiteFolder(streamPath):
            self._handle= os.open(streamPath)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._handle.close()

    def _exsiteFolder(self,streamPath):
        if not os.path.exists(streamPath.rsplit(r'\\',1)[0]):
            try:
                os.mkdir(streamPath)
                return True
            except Exception as e:
                return False
        else:
            return True