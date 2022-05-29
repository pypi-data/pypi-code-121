"""Browser utils."""

import logging
import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from utils import browserx_firefox_profile, sysx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('selenium-wrapper')
MAX_T_WAIT = 60


class Browser:
    """Browser."""

    def __init__(self, url):
        """Construct."""
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(
            options=options,
            firefox_profile=browserx_firefox_profile._get(),
        )
        log.info('Opened "%s" in Selenium Firefox Browser', url)
        self.browser.get(url)

    def find_elements_by_id_retry(self, elem_id):
        """Find elements by id."""

        def _find():
            elems = self.browser.find_elements_by_id(elem_id)
            if len(elems) > 0:
                return elems
            return None

        return sysx.retry(
            'Find elems with id="%s"' % elem_id,
            _find,
        )

    def find_element_by_id_retry(self, elem_id):
        """Find single element by id."""
        elems = self.find_elements_by_id_retry(elem_id)
        if elems:
            return elems[0]
        return None

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        SCRIPT_SCROLL = 'window.scrollTo(0, document.body.scrollHeight);'
        self.browser.execute_script(SCRIPT_SCROLL)

    def scroll_to_element(self, elem):
        """Scroll to element."""
        self.browser.execute_script("arguments[0].scrollIntoView();", elem)

    def find_scroll_and_click(self, elem_id):
        """Find element, scroll to it and click."""
        elem = self.find_element_by_id_retry(elem_id)
        self.scroll_to_element(elem)
        elem.click()
        log.info('Clicked on "%s"', elem_id)
        return elem

    def get_source(self):
        """Get page source."""
        return self.browser.page_source

    def quit(self):
        """Quit."""
        self.browser.quit()

    def close(self):
        """Close."""
        self.browser.close()

    def wait_and_quit(self, file_name):
        """Wait and quit."""

        def _wait():
            if os.path.exists(file_name):
                return file_name
            return None

        sysx.retry(
            'wait for "%s"' % (file_name),
            _wait,
        )

        self.quit()
        return file_name
