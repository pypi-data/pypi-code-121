import os
import json
import time
import html
import base64

from chromdroid.webdriver.common import utils
from chromdroid.webdriver.common.by import By
from chromdroid.webdriver.remote.command import Command
from chromdroid.webdriver.remote.web_element import WebElement
from chromdroid.webdriver.common.exception import NoSuchElementException, NoSuchPageSourceException, ApplicationClosed
from chromdroid.webdriver.remote.remote_connection import RemoteConnection


class WebDriver(RemoteConnection):

    def __init__(self, gui=True, accept_time_out=60, recv_time_out=60*60):
        super(WebDriver, self).__init__(accept_time_out=accept_time_out)
        self.encode_req = lambda data, encode=True: (
            "%s\n" % utils.DictMap(data)).encode() if encode else "%s\n" % data
        self.gui = gui
        self.shut_up = False
        data = self.encode_req({
            "command": Command.INIT,
            "host": self.host,
            "port": self.port
        }, False)
        if self.gui:
            os.system(self.command(
                "start", "com.luanon.chromium/.MainActivity", data))
        else:
            os.system(self.command("startservice",
                      "com.luanon.chromium/.MainService", data))
        try:
            self.client_accept = self.accept()[0]
            self.client_accept.settimeout(recv_time_out)
        except TimeoutError:
            utils.exception(TimeoutError, "Could not connect chrome webdriver")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #----------utils----------#

    def command(self, action, name, data=""):
        return "am %s -n %s -d '%s' > /dev/null" % (action, name, data)

    def check_result(self, commnad, recv):
        #print("\033[1;32m%s\033[1;0m" %recv)
        data = utils.DictMap(json.loads(recv), "no_encode_again")
        #print("\033[1;33m%s\033[1;0m" %data)
        if commnad == data.command:
            return data

    def execute(self, command, **kwargs):
        data = self.encode_req({
            "command": command,
            **kwargs
        })
        self.client_accept.send(data)
        recv = self.recv_all()
        return self.check_result(command, recv)

    def recv_all(self):
        """
                byte or string faster?
                byte faster 0.2 - 1 second
        """
        result = b""
        length = b""
        while True:
            try:
                data = self.client_accept.recv(1)
            except Exception:
                utils.exception(TimeoutError, "Time out to receive data")
            if not data.decode().isdigit():
                result += data
                break
            length += data
        try:
            length = int(length.decode())
        except Exception:
            utils.exception(ApplicationClosed,
                            "Please close me by driver.close() conmand")
        while len(result) < length:
            result += self.client_accept.recv(self.max_recv)
        return utils.decode_data(result)

    #----------function----------#

    def close(self):
        return self.execute(Command.CLOSE).result

    @property
    def current_url(self):
        return self.execute(Command.CURRENT_URL).result

    def clear_cookie(self, name, url=""):
        return self.execute(Command.CLEAR_COOKIE, request=url, keys=name).result

    def clear_cookies(self):
        return self.execute(Command.CLEAR_COOKIES).result

    def execute_script(self, script):
        return self.execute(Command.EXECUTE_SCRIPT, script=script).result

    def find_element_by_id(self, id_):
        return self.find_element(by=By.ID, value=id_)

    def find_element_by_xpath(self, xpath):
        return self.find_element(by=By.XPATH, value=xpath)

    def find_element_by_link_text(self, link_text):
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_element_by_partial_link_text(self, partial_link_text):
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=partial_link_text)

    def find_element_by_name(self, name):
        return self.find_element(by=By.NAME, value=name)

    def find_element_by_tag_name(self, tag_name):
        return self.find_element(by=By.TAG_NAME, value=tag_name)

    def find_element_by_class_name(self, class_name):
        return self.find_element(by=By.CLASS_NAME, value=class_name)

    def find_element_by_css_selector(self, css_selector):
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_id(self, id_):
        return self.find_elements(by=By.ID, value=id_)

    def find_elements_by_xpath(self, xpath):
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_elements_by_link_text(self, link_text):
        return self.find_elements(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, partial_link_text):
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=partial_link_text)

    def find_elements_by_name(self, name):
        return self.find_elements(by=By.NAME, value=name)

    def find_elements_by_tag_name(self, tag_name):
        return self.find_elements(by=By.TAG_NAME, value=tag_name)

    def find_elements_by_class_name(self, class_name):
        return self.find_elements(by=By.CLASS_NAME, value=class_name)

    def find_elements_by_css_selector(self, css_selector):
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def find_element(self, by, value, command=""):
        if command:
            element = self.execute(Command.FIND_ELEMENT,
                                   request=command, by=by, value=value)
        else:
            element = self.execute(Command.FIND_ELEMENT, by=by, value=value)
        if not element.result:
            return None
        return WebElement(self.execute, element)

    def find_elements(self, by, value):
        elements = self.execute(Command.FIND_ELEMENTS, by=by, value=value)
        result = []
        for element in elements.result:
            data = utils.DictMap(elements)  # copy
            data.command = Command.FIND_ELEMENT
            data.element_path = "%s[%s]" % (elements.element_path, element[0])
            data.result = element[1]
            result.append(WebElement(self.execute, data))
        return result

    def get(self, url):
        return self.execute(Command.GET, url=url).result

    def get_cookie(self, name, url=""):
        return self.execute(Command.GET_COOKIE, request=url, keys=name).result

    def get_cookies(self, url=""):
        return self.execute(Command.GET_COOKIES, request=url).result

    def implicitly_wait(self, delay):
        time.sleep(delay)

    @property
    def page_source(self):
        page_source = self.execute(Command.PAGE_SOURCE).result
        if not page_source:
            utils.exception(NoSuchPageSourceException,
                            "If you get this error please report me on github", self.shut_up)
        return page_source

    def swipe_down(self):
        return self.execute(Command.SWIPE_DOWN).result

    def swipe_up(self):
        return self.execute(Command.SWIPE_UP).result

    def set_cookie(self, name, value, url=""):
        return self.execute(Command.SET_COOKIE, request=url, keys=name, value=value).result

    def set_user_agent(self, user_agent):
        return self.execute(Command.SET_USER_AGENT, keys=user_agent).result

    def set_proxy(self, host, port):
        proxy = host + ":" + str(port)
        return self.execute(Command.SET_PROXY, keys=proxy).result

    @property
    def title(self):
        return self.execute(Command.TITLE).result
