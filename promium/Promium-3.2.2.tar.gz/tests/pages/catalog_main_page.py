from selenium.webdriver.common.by import By

from promium import Page, Block, Link, InputField

from tests.urls import collect_url


class HeaderRegistration(Block):
    pass


class TopSearchesBlock(Block):
    pass


class EmptyOrderPopup(Block):
    pass


class SearchBlock(Block):
    search_input = InputField(
        By.CSS_SELECTOR,
        '[data-qaid="search_input"]'
    )


class HeaderBlock(Block):

    search_block = SearchBlock(
        By.CSS_SELECTOR,
        '[data-qaid="search_input_block"]'
    )
    logo_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="header_logo_link"]'
    )
    favourite_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="favorite"]'
    )
    shopping_cart_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="shopping_cart"]'
    )
    authorization_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="auth_element"][href*="sign-in"]'
    )


class HeaderToolbarBlock(Block):

    add_classified_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="add_classified"]'
    )
    mobile_app_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="mobile_app_link"]'
    )
    authorization_link = Link(
        By.CSS_SELECTOR,
        '[data-qaid="auth_element"]'
    )
    registration_link = Link(
        By.CSS_SELECTOR,
        "[data-qaid='reg_element']"
    )
    header_reg_popup = HeaderRegistration(
        By.CSS_SELECTOR,
        '[data-qaid="header_registration_popup"]'
    )


class CatalogMainPage(Page):

    url = collect_url('')

    top_searches_block = TopSearchesBlock(
        By.CSS_SELECTOR,
        '[data-qaid="top-searches"]'
    )
    header_block = HeaderBlock(
        By.CSS_SELECTOR,
        '[data-qaid="header"]'
    )
    header_toolbar_block = HeaderToolbarBlock(
        By.CSS_SELECTOR,
        '[data-qaid="header-toolbar"]'
    )
    empty_order_popup = EmptyOrderPopup(
        By.CSS_SELECTOR,
        '[data-qaid="overlay"]'
    )
    header_reg_popup = Block(
        By.CSS_SELECTOR,
        '[data-qaid="header_registration_popup"]'
    )
