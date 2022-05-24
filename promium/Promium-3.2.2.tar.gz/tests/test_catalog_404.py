# -*- coding: utf-8 -*-

import pytest

from promium.test_case import WebDriverTestCase
from promium.waits import wait_url_contains
from tests.urls import collect_url
from tests.pages.catalog_404_page import Catalog404Page


MAIN_404_PAGE_TITLE = (
    'Оо! Страница не найдена'
)
SUGGEST_404_PAGE_TITLE = (
    'Похоже такой страницы больше нет, либо произошла какая-то ошибка, '
    'попробуйте обновить страницу либо поискать что-то еще'
)

SEARCH_TERM = 'search?search_term='


def get_expected_search_term_url(search_target):
    return collect_url('{search_term}{search_target}'.format(
        search_term=SEARCH_TERM,
        search_target=search_target
    ))


@pytest.mark.se
class Test404CatalogPage(WebDriverTestCase):
    test_case_url = 'some url with test case'

    def test_catalog_404_page_check_elements(self):
        catalog_404_page = Catalog404Page(self.driver)
        catalog_404_page.open()
        catalog_404_page.wait_for_page_loaded()
        self.soft_assert_equals(
            catalog_404_page.main_404_title.text,
            MAIN_404_PAGE_TITLE,
            'Не правильно указан основной title на странице 404.'
        )
        self.soft_assert_equals(
            catalog_404_page.suggest_404_title.text,
            SUGGEST_404_PAGE_TITLE,
            'Не правильно указан suggest title на странице 404.'
        )
        fake_search_query = 666
        catalog_404_page.search_input.send_keys(fake_search_query)
        catalog_404_page.search_button.click()
        wait_url_contains(
            self.driver,
            get_expected_search_term_url(fake_search_query)
        )
