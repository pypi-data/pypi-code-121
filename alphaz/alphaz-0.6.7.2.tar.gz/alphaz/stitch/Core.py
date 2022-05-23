from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from glob import glob
import os, sys

class Core:
    INIT            = False

    INIT_FILE       = "init.json"
    WEBSITES_PATH   = 'websites'
    DRIVER_DIR      = 'web-drivers'
    DRIVER_PATH     = ''

    CAPABILITIES    = { 'chromeOptions':  { 'useAutomationExtension': False}}

    DRIVER          = None
    ROOT_PATH       = ""

    @staticmethod
    def set_driver(name='chrome'):
        name = name.lower()
        
        driver = None
        if name == 'firefox':
            Core.set_driver_name('geckodriver')
            driver_path     = Core.DRIVER_ROOT + os.sep + 'geckodriver'
            monExecutable   = FirefoxBinary(driver_path)
            driver = webdriver.Firefox(firefox_binary= monExecutable)

            sys.path.append(Core.DRIVER_ROOT)
            #driver = webdriver.Firefox() # Core.get_driver_path(), desired_capabilities = Core.CAPABILITIES
        elif name == 'chrome':
            Core.set_driver_name('chromedriver.exe')
            driver = webdriver.Chrome(Core.DRIVER_PATH, desired_capabilities = Core.CAPABILITIES)
        Core.DRIVER = driver

    @staticmethod
    def set_driver_name(driver_name):
        Core.DRIVER_PATH    = Core.DRIVER_ROOT + os.sep + driver_name

    @staticmethod
    def init():    
        print('Core initialization')
        Core.ROOT_PATH      = os.path.dirname(__file__)
        Core.DRIVER_ROOT    = Core.ROOT_PATH + os.sep + Core.DRIVER_DIR

    @staticmethod
    def getWebsites():
        results     = glob(Core.WEBSITES_PATH + os.sep + "*")
        websites    = [os.path.basename(x) for x in results if os.path.isdir(x)]
        return websites

if not Core.INIT:
    Core.init()