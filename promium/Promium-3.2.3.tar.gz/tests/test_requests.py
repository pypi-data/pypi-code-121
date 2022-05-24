import pytest
from bs4 import BeautifulSoup

from promium.test_case import RequestTestCase


@pytest.mark.request
class TestMainPage(RequestTestCase):
    test_case_url = 'some url with test case'

    def test_google_search_block(self):
        page_text = self.get_response('https://google.com.ua').text
        soup = BeautifulSoup(page_text, "html.parser")

        search_input = soup.find(attrs={'name': 'q'})
        self.soft_assert_true(
            search_input,
            'Не найдена строка поиска'
        )

        search_btn = soup.find(attrs={'name': 'btnG'})
        self.soft_assert_equals(
            search_btn.get('value'),
            'Пошук Google',
            'Не правильное название кнопки поиска'
        )
