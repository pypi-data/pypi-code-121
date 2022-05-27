
from robertcommonio.basic.cls.utils import SingleInstance

class TestClass(SingleInstance):

    def __init__(self, **kwargs):
        super(TestClass, self).__init__(**kwargs)
        self.cache = {}

    def set(self, key, value):
        self.cache[key] = value

    def get(self, key):
        return self.cache.get(key)


def get_interface(driver_type):
    """Returns an instance of the interface"""
    module_name = "system.io." + driver_type
    module = __import__(module_name)
    ios = module.io
    sub_module = getattr(ios, driver_type)
    klass = getattr(sub_module, "INIAccessor")
    config = getattr(sub_module, "INIConfig")
    accessor = klass(config(PATH='test.ini', PARAMS={'HTTP_SERVER': {'HTTP_HOST': '0.0.0.0', 'HTTP_PORT': 5002}}))
    assert accessor.get('HTTP_HOST', str) != '0.0.0.0'
    accessor.set('HTTP_HOST', '127.0.0.1')
    assert accessor.get('HTTP_HOST', str) == '127.0.0.1'
    print()
    return accessor

def get_interface1(driver_type):
    """Returns an instance of the interface"""
    module_name = "basic.dt.utils"
    module = __import__(module_name, fromlist=('utils'))
    print(dir(module))
    print(module.get_date())

#get_interface1('ini')

TestClass.getInstance().set('aa', 123)
print(TestClass.getInstance().get('aa'))