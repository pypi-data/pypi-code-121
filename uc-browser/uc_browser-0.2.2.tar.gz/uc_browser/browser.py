from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
from random import choice

import re
import stem.process
from stem import Signal
from stem.control import Controller


os.environ['WDM_LOG'] = '1'
os.environ['WDM_LOG_LEVEL'] = '1'


class Browser:
    user_agents = []

    @classmethod
    def get_agent(cls):
        if len(Browser.user_agents) > 0:
            return choice(Browser.user_agents)
        exit(1)

    @staticmethod
    def interceptor(request):
        del request.headers['Referer']  # Remember to delete the header first
        request.headers['Referer'] = 'https://google.com.br'  # Spoof the referer

    def __init__(self, use_proxy=False, in_terminal=False, profile_path=None, active_sleep=False, active_tor=False):
        self.__active_sleep = active_sleep
        self.__active_tor = active_tor
        self.__tor_process = None

        # if use_proxy:
        #     from seleniumwire import webdriver
        # else:
        #     from selenium import webdriver
        options = webdriver.ChromeOptions()
        if in_terminal:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--mute-audio")

        if profile_path is not None:
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)
            options.add_argument("--profile-directory=Default")
            options.add_argument('--user-data-dir=' + profile_path)

        Browser.user_agents = list(Utils.get_agent_users())

        options.add_argument("start-maximized")
        options.add_argument("--window-size=1280,800")
        options.add_argument(f'user-agent={Browser.get_agent()}')
        options.add_argument('--disable-dev-sh-usage')
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        serv_driver = Service(ChromeDriverManager().install())
        if use_proxy:
            self.driver = webdriver.Chrome(service=serv_driver, options=options,
                                           seleniumwire_options=self.__use_proxy())
        else:
            self.driver = webdriver.Chrome(service=serv_driver, options=options)

    def set_headers(self):
        raise NotImplementedError("Please implement this method")

    def __use_proxy(self):
        if self.__active_tor:
            SOCKS_PORT = 41293
            CONTROL_PORT = 41294

            print('[INFO] TOR has been activated. Using this option will change your IP address every 60 secs.')
            print(
                '[INFO] Depending on your luck you might still see: Your Computer or Network May Be Sending Automated '
                'Queries.')
            self.__tor_process = TorProxy.create_tor_proxy(SOCKS_PORT, CONTROL_PORT)
            proxies = {
                'proxy': {
                    "http": f"socks5://127.0.0.1:{SOCKS_PORT}",
                    "https": f"socks5://127.0.0.1:{SOCKS_PORT}",
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }
        else:
            API_KEY = '030bc9e214b3a2eae6bc1fe05e50e4b6'
            proxies = {
                'proxy': {
                    'http': f'http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001',
                    'https': f'http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001',
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }
        return proxies

    def test_proxy(self):
        self.driver.get('http://httpbin.org/ip')
        print(self.driver.page_source)

    def delay(self, waiting_time=5):
        self.driver.implicitly_wait(waiting_time)

    def close_driver(self):
        self.driver.close()

    def click(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).click()

    def wait_to_click(self, xpath, time=10):
        return WebDriverWait(self.driver, time).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

    def wait_frame_switch_to(self, xpath, time=10):
        WebDriverWait(self.driver, time).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))

    def switch_to_frame_default(self):
        self.driver.switch_to.default_content()

    def switch_to_frame(self, frame):
        self.driver.switch_to.frame(frame)

    def get_href(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).get_attribute('href')

    def get_src(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).get_attribute('src')

    def navigate(self, url):
        if self.__active_sleep:
            Utils.time_to_sleep()

        self.driver.request_interceptor = Browser.interceptor
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.get_agent()})
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                  const newProto = navigator.__proto__
                  delete newProto.webdriver
                  navigator.__proto__ = newProto
                  """
        })
        self.driver.get(url)

    def input(self, xpath, send):
        self.driver.find_element(By.XPATH, xpath).send_keys(send)

    def get_text(self, xpath):
        return self.driver.find_element(By.XPATH, xpath).text

    def get_elements(self, xpath):
        return self.driver.find_elements(By.XPATH, xpath)


class Utils:
    @staticmethod
    def time_to_sleep(start=2, end=10):
        from time import sleep
        from random import randint
        sleep(randint(start, end))

    @staticmethod
    def get_agent_users():
        agents = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 '
            'Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 '
            'Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 '
            'Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 '
            'Safari/537.36 '
        )
        return agents


class TorProxy:
    @staticmethod
    def create_tor_proxy(socks_port, control_port):
        try:
            tor_process = stem.process.launch_tor_with_config(
                config={
                    'SocksPort': str(socks_port),
                    'ControlPort': str(control_port),
                    'MaxCircuitDirtiness': '300',
                    'DataDir': '/tmp/tor'
                },
                init_msg_handler=lambda line: print(line) if re.search('Bootstrapped', line) else False,
                tor_cmd='/usr/bin/tor'
            )
            print("[INFO] Tor connection created.")
        except:
            tor_process = None
            print("[INFO] Using existing tor connection.")

        return tor_process

    @staticmethod
    def renew_ip(control_port):
        print("[INFO] Renewing TOR ip address.")
        with Controller.from_port(port=control_port) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            controller.close()
        print("[INFO] IP address has been renewed! Better luck next try~")


if __name__ == '__main__':
    bw = Browser()
    print(bw.get_agent())
