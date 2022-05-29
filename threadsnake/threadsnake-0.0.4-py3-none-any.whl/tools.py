from asyncio.subprocess import PIPE
import subprocess

class PhpServer:
    def __init__(self, path:str, port:int = 80, address:str= 'localhost', phpBinPath:str='php') -> None:
        self.path:str = path
        self.port:int = port
        self.address:str = address
        self.process:subprocess.Popen = None
        self.pid:int = None
        self.phpBinPath = phpBinPath
        
    def start(self):   
        arguments = [
            f'{self.phpBinPath}',
            f'--server',
            f'{self.address}:{self.port}'
        ]
        path = self.path
        self.process = subprocess.Popen(arguments, stdout=PIPE, stderr=PIPE, cwd=path)
        self.pid = self.process.pid
        return self
    
    def stop(self):
        self.process.kill()