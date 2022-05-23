from JuMonC.tasks import Plugin

class PapiPlugin(Plugin.Plugin):
    
    def _isWorking(self) -> bool:
        return False