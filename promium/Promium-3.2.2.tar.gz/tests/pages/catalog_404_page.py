from selenium.webdriver.common.by import By

from promium import Page, Element, InputField
from tests.urls import collect_url


class Catalog404Page(Page):

    url = collect_url('xxx')

    search_input = InputField(
        By.CSS_SELECTOR,
        '[data-qaid="search_form"] input'
    )
    search_button = Element(
        By.CSS_SELECTOR,
        '[data-qaid="search_form"] button[type="submit"]'
    )
    main_404_title = Element(
        By.CSS_SELECTOR,
        '[data-qaid="page_not_found_title"]'
    )
    suggest_404_title = Element(
        By.CSS_SELECTOR,
        '[data-qaid="page_not_found_descr"]'
    )
