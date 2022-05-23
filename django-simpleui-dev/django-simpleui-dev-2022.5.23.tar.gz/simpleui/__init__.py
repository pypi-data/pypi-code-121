default_app_config = 'simpleui.apps.SimpleApp'
import datetime

def get_version():
    return datetime.datetime.now().strftime('%Y.%m.%d')
