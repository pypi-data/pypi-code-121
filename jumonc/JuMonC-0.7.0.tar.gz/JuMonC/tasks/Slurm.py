from JuMonC.tasks import Plugin

class SlurmPlugin(Plugin.Plugin):
    
    def _isWorking(self) -> bool:
        return False