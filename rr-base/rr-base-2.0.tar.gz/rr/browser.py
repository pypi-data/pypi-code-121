from seleniumwire import webdriver as webdriver_wire
from selenium import webdriver as selenium_driver
from browsermobproxy import Server
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeleniumConfig:
    """Default parameters for initiate driver"""

    def __init__(self, chrome_driver_location=None, url='chrome://settings/cookies',
                 headless: bool = False, network: bool = False,
                 page_load_timeout: int = 30, implicitly_wait: int = 30,
                 wait_for_element: int = 3, proxy: bool = False,
                 bob_proxy_path=None, using_wire_package: bool = True,
                 disable_css: bool = False, logs: bool = True):
        self.__url = url
        self.__headless = headless
        self.__network = network
        self.__page_load_timeout = page_load_timeout
        self.__implicitly_wait = implicitly_wait
        self.__proxy = proxy
        self.__bob_proxy_path = bob_proxy_path
        self.__using_wire_package = using_wire_package
        self.__disable_css = disable_css
        self.__driver = self.__initiate_driver(chrome_driver_location=chrome_driver_location)
        self.__actions = SeleniumActions(driver=self.__driver, logs=logs, wait_for_element=wait_for_element)

    @property
    def __get_driver_type(self):
        if self.__using_wire_package:
            return webdriver_wire
        else:
            return selenium_driver

    @property
    def driver(self):
        return self.__driver

    @property
    def actions(self):
        return self.__actions

    @property
    def proxy(self):
        return self.__proxy

    @property
    def session_requests(self):
        if self.__using_wire_package:
            return self.__driver.requests

    @property
    def __proxy_server(self):
        server = Server(self.__bob_proxy_path)
        server.start()
        return server.create_proxy()

    @property
    def __without_css_prefs(self):
        return {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 2,
                                                           'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                           'notifications': 2, 'auto_select_certificate': 2,
                                                           'fullscreen': 2, 'mouselock': 2, 'mixed_script': 2,
                                                           'media_stream': 2, 'protocol_handlers': 2,
                                                           'media_stream_mic': 2, 'media_stream_camera': 2,
                                                           'ppapi_broker': 2, 'automatic_downloads': 2,
                                                           'midi_sysex': 2, 'metro_switch_to_desktop': 2,
                                                           'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                           'protected_media_identifier': 2, 'app_banner': 2,
                                                           'site_engagement': 2, 'durable_storage': 2}}

    def __initiate_driver(self, chrome_driver_location=None):
        """Creates a new instance of the chrome driver.
           Starts the service and then creates new instance of chrome driver.
        :Args
        - url - set end point
        - headless - gives the option to run the tests in the background
        - proxy - gives the option to record the traffic
        :Returns:
             - the driver object"""
        chrome_options = Options()
        capabilities = DesiredCapabilities.CHROME.copy()
        webdriver = self.__get_driver_type

        if self.__proxy:
            self.__proxy = self.__proxy_server
            chrome_options.add_argument("--proxy-server={0}".format(self.__proxy.proxy))
            chrome_options.add_argument('--ignore-ssl-errors=yes')
            chrome_options.add_argument('--ignore-certificate-errors')

        if self.__headless:
            chrome_options.add_argument("--headless")

        if self.__network:
            capabilities = webdriver.DesiredCapabilities.CHROME
            capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

        if self.__disable_css:
            chrome_options.add_experimental_option('prefs', self.__without_css_prefs)
            chrome_options.add_argument('window-size=1200,1100')
            chrome_options.add_argument("disable-infobars")
            chrome_options.add_argument("--disable-extensions")

        if chrome_driver_location is None:
            driver = webdriver.Chrome(executable_path=ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                                      chrome_options=chrome_options,
                                      desired_capabilities=capabilities)
        else:
            driver = webdriver.Chrome(executable_path=chrome_driver_location,
                                      chrome_options=chrome_options,
                                      desired_capabilities=capabilities)

        driver.set_page_load_timeout(self.__page_load_timeout)
        driver.get(self.__url)
        driver.implicitly_wait(self.__implicitly_wait)
        if not self.__headless:
            driver.maximize_window()

        print(f"Started a new session: {driver.session_id}")
        return driver

    @property
    def get_network_performance(self):
        """return the log entry"""
        return self.__driver.get_log('performance')

    def get_url(self, url):
        """Loads a web page in the current browser session.
        :Args:
       - url - needs end point url for start session"""
        try:
            self.__driver.get(url)
        except Exception as e:
            print(f'Failed to get url : {url}, reason : {e}')

    def get_data_from_url(self, url):
        """this function return the html body from specific url."""
        self.get_url(url)
        return self.__get_body()

    def __get_body(self):
        """this function return the html body."""
        try:
            return self.__driver.find_element_by_tag_name("body").text
        except Exception as e:
            print(f"get body method exception:\n{e}")
            return

    def tear_down(self):
        """close the driver session."""
        self.__driver.close()
        print("driver close")


class SeleniumActions:
    """
    This module wrapping basic web actions
    """

    def __init__(self, driver, logs: bool = True, wait_for_element: int = 3):
        self.__driver = driver
        self.__logs = logs
        self.__web_element_type = "webelement"
        self.__temp_element = None
        self.wait_for_element = wait_for_element

    def wait_for_text(self, location=None, text=None):
        try:
            if location:
                WebDriverWait(self.__driver, 10).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, location), text))
                if self.__logs:
                    print(f"Succes to find text: {text} in element: {location}")
            else:
                text = self.find_element_by_xpath(f"//*[text()='{text}']").text
                print(f"Succes to find text: {text}")
            return True
        except Exception:
            if self.__logs:
                assert False, print(f"Failed to find text: {text}")

    def get_list_of_elements_by_type(self, element_type, element):
        """
        - args -
              element_type: 1 = id, 2 - xpath, 3 - name, 4 - css, 5 - link text"""
        try:
            if element_type == 1:
                return self.__driver.find_elements(By.ID, element)
            elif element_type == 2:
                return self.__driver.find_elements(By.XPATH, element)
            elif element_type == 3:
                return self.__driver.find_elements(By.NAME, element)
            elif element_type == 4:
                return self.__driver.find_elements(By.CSS_SELECTOR, element)
            elif element_type == 5:
                return self.__driver.find_elements(By.LINK_TEXT, element)

        except Exception as e:
            if self.__logs:
                print(f"Failed to find list of elements: {e}")
        return

    def click(self, element, wait=0):
        sleep(wait)
        self.__temp_element = self.check_all_options(element)
        try:
            if self.__temp_element is not None:
                self.__temp_element.click()
                if self.__logs:
                    print(f"success to click on element: {element}")
                return True
        except Exception as e:
            if self.__logs:
                assert False, print(f"Failed to click on element: {e}")

    def hover(self, element, wait=0):
        sleep(wait)
        self.__temp_element = self.check_all_options(element)
        try:
            if self.__temp_element is not None:
                hover = ActionChains(self.__driver).move_to_element(self.__temp_element)
                hover.perform()
                if self.__logs:
                    print(f"success to hover on: {element}")
                return True
        except Exception as e:
            if self.__logs:
                assert False, print(f"Failed to hover on element ,reason: {e}")

    def send_keys(self, element=None, text=None, wait=0):
        text = str(text)
        sleep(wait)
        if not element:
            ActionChains(self.__driver).send_keys(text).perform()
            if self.__logs:
                print(f"Succeed to send text to screen")
            return True
        self.__temp_element = self.check_all_options(element)
        try:
            if self.__temp_element is not None:
                self.__temp_element.send_keys(text)
                if self.__logs:
                    print(f"Succeed to send text to element: {element}")
                return True
        except Exception as e:
            if self.__logs:
                assert False, print(f"Failed to send text to element: {e}")

    def get_text(self, element, wait=0, fail=True):
        sleep(wait)
        self.__temp_element = element
        if self.__web_element_type not in str(type(self.__temp_element)):
            self.__temp_element = self.check_all_options(element)
        try:
            if self.__temp_element is not None:
                return self.__temp_element.text
        except Exception as e:
            if self.__logs:
                print(f"Failed to get text to element: {element}\nException:\n{e}")
            if fail:
                assert False

    def check_all_options(self, element):
        # check id option
        self.__temp_element = self.find_element_by_id(element)
        if self.__temp_element is not None:
            return self.__temp_element

        self.__temp_element = self.find_element_by_xpath(element)
        if self.__temp_element is not None:
            return self.__temp_element

        # check name option
        self.__temp_element = self.find_element_by_css(element)
        if self.__temp_element is not None:
            return self.__temp_element

        # check name option
        self.__temp_element = self.find_element_by_link_text(element)
        if self.__temp_element is not None:
            return self.__temp_element

        # check name option
        self.__temp_element = self.find_element_by_name(element)
        if self.__temp_element is not None:
            return self.__temp_element

        return

    def find_element_by_id(self, element):
        try:
            self.__temp_element = self.__driver.find_element_by_id(element)
            if self.__logs:
                print(f"Found element: {element}")
            return self.__temp_element
        except Exception:
            if self.__logs:
                print(f"Failed to find element: {element}")
        return None

    def find_element_by_class_name(self, element):
        try:
            self.__temp_element = self.__driver.find_element_by_class_name(element)
            if self.__logs:
                print(f"Found element: {element}")
            return self.__temp_element
        except Exception:
            if self.__logs:
                print(f"Failed to find element: {element}")
        return None

    def find_element_by_xpath(self, element):
        try:
            self.__temp_element = self.__driver.find_element_by_xpath(element)
            if self.__logs:
                print(f"Found element: {element}")
            return self.__temp_element
        except Exception:
            if self.__logs:
                print(f"Failed to find element: {element}")
        return None

    def find_element_by_name(self, element):
        try:
            self.__temp_element = self.__driver.find_element_by_name(element)
            if self.__logs:
                print(f"Found element: {element}")
            return self.__temp_element
        except Exception:
            if self.__logs:
                print(f"Failed to find element: {element}")
        return None

    def find_element_by_css(self, element):
        try:
            self.__temp_element = self.__driver.find_element_by_css(element)
            if self.__logs:
                print(f"Found element: {element}")
            return self.__temp_element
        except Exception:
            if self.__logs:
                print(f"Failed to find element: {element}")
        return None

    def find_element_by_link_text(self, element):
        try:
            self.__temp_element = self.__driver.find_element_by_link_text(element)
            if self.__logs:
                print(f"Found element: {element}")
            return self.__temp_element
        except Exception:
            if self.__logs:
                print(f"Failed to find element: {element}")
        return None

    def get_page_source(self):
        try:
            source = self.__driver.page_source
            return source
        except Exception:
            return False

    def get_body(self):
        try:
            return self.__driver.find_element_by_tag_name("body").text
        except Exception:
            return False

    def get_href(self, element):
        try:
            if element is not None:
                self.__temp_element = element.get_attribute("href")
                return self.__temp_element

        except Exception:
            if self.__logs:
                print(f"Failed to find element: {element}")
        return False
