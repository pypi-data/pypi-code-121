import json
import os


class SettingsManager:
    def get_path(self):
        if os.name == 'nt':
            return os.path.join(os.getenv('APPDATA'), 'smartinput_ng')
        elif os.name == 'posix':
            return os.path.join(os.getenv('HOME'), '.config', 'smartinput_ng')
        else:
            raise NotImplementedError('OS not supported')

    def get_file_path(self):
        return os.path.join(self.get_path(), 'settings.json')

    def get_config_file_path(self):
        return os.path.join(self.get_path(), 'config.yml')

    def get_settings(self):
        if os.path.exists(self.get_file_path()):
            with open(self.get_file_path(), 'r') as f:
                return json.loads(f.read())
        else:
            return {}
    
    def save_settings(self, settings: dict):
        os.makedirs(self.get_path(), exist_ok=True)
        with open(self.get_file_path(), 'w') as f:
            json.dump(settings, f)

settings_manager = SettingsManager()