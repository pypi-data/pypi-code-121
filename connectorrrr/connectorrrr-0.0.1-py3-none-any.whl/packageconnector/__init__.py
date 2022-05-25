import packagesource
import packagedestination

def test_source(name):
    return packagesource.say_hello(name)
def test_destination(name):
    return packagedestination.say_bye(name)