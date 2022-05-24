import logging
from time import sleep
from scrapper_boilerplate.setup import setSelenium
from scrapper_boilerplate.parser_handler import init_parser


def scrolldown(driver):
    """
    Scroll down the page
    args:
        - driver: Selenium Webdriver
    return: void
    """

    SCROLL_PAUSE_TIME = 20

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page and increments one more second
        SCROLL_PAUSE_TIME += 1
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def smooth_scroll(driver):
    """
    Smooth scroll the page
    args:
        - driver: Selenium Webdriver
    returns:
        - void
    """
    scroll = .1
    while scroll < 9.9:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scroll)
        scroll += .01


def load_dynamic_page(url, headless=True):
    """
    Load a dynamic page
    args:
        - url: str, the url of the page you want to load
        - headless: bool, True if you want to run the browser in headless mode
    returns:
        - driver: Selenium Webdriver
    """

    with setSelenium(headless=headless) as driver:
        driver.get(url)
        driver.implicitly_wait(220)
        html = driver.find_element_by_tag_name('html')
        return init_parser(html.get_attribute('outerHTML'))


def load_code(driver):
    """
    Load code from a page

    args:
        - driver: Selenium Webdriver
    
    returns:
        - code: Beautifulsoap Obj, the code from the page
    """

    code = driver.page_source
    return init_parser(code)


def check_tag(tag):
    """
    Check if the tag is valid
    args:
        - tag: str, the tag you want to check
    returns:
        - bool: True if the tag is valid, 'Não localizado...':str otherwise
    """
    try:
        handler = tag
        return handler

    except Exception as error:
        print('Error')
        logging.error(error)
        return 'Não localizado...'
