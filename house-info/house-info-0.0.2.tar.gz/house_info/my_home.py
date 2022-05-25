import re
import time
from typing import Final, Dict
import pandas as pd
from bs4 import BeautifulSoup, ResultSet
from selenium.webdriver.chrome.webdriver import WebDriver
from house_info.base import BaseSelRequest
from house_info.utils import PageList, LIST_IN_TUPLE, DataFrame


class MyHomeRequest(BaseSelRequest):
    """
    마이홈 포털 정보 수집
    :ChromeDriver 필요
    """

    URL: Final = "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcView.do"

    def __init__(
        self,
        chrome_driver_path: str,
        page: int = 1,
        types: str = "student",
        region: str = "seoul",
    ) -> None:
        super(MyHomeRequest, self).__init__(chrome_driver_path, page)
        self.types = types
        self.region = region

        assert self.types in ["student", "couple"], "types는 student 또는 couple 이어야함"
        assert self.region in ["seoul", "kkd"], "region는 seoul 또는 kkd 이어야함"

    def get_post_list(self, soup: BeautifulSoup) -> ResultSet:
        post_list = soup.find("tbody", attrs={"id": "schTbody"}).find_all("tr")
        if not post_list:
            return None
        return post_list

    def move_next_page(self, browser: WebDriver, page: int) -> WebDriver:
        browser.execute_script(f"fnSearch({page})")
        return browser

    def click_category(self, browser: WebDriver) -> WebDriver:
        if self.region == "seoul" and self.types == "student":
            browser.execute_script("fnSchKoreaMapClick('11');")  # 서울
            time.sleep(1.5)
            browser.execute_script("setUserTy('FIXES100001');")  # 대학생
        elif self.region == "seoul" and self.types == "couple":
            browser.execute_script("fnSchKoreaMapClick('11');")
            time.sleep(1.5)
            browser.execute_script("setUserTy('FIXES100002');")  # 신혼부부
        elif self.region == "kkd" and self.types == "student":
            browser.execute_script("fnSchKoreaMapClick('41');")  # 경기
            time.sleep(1.5)
            browser.execute_script("setUserTy('FIXES100001');")
        elif self.region == "kkd" and self.types == "couple":
            browser.execute_script("fnSchKoreaMapClick('41');")
            time.sleep(1.5)
            browser.execute_script("setUserTy('FIXES100002');")
        return browser

    def create_post_list_sources(self) -> PageList:
        browser = self.browser_open_headless()
        browser = self.click_category(browser)
        time.sleep(0.5)
        page_source = self.get_page_source(browser)
        parsed_html = self.parse_html(page_source)
        post_list = self.get_post_list(parsed_html)
        post_list_sources = PageList([post_list])

        for page in range(2, self.page + 1):
            self.move_next_page(browser, page)
            time.sleep(1)
            # TODO: neeed to extract func
            page_source = self.get_page_source(browser)
            parsed_html = self.parse_html(page_source)
            post_list = self.get_post_list(parsed_html)

            if not post_list:
                break
            post_list_sources.append(post_list)
        return post_list_sources

    def __call__(self) -> PageList:
        return self.create_post_list_sources()


class MyHomeTable:
    def __init__(self, page_sources: PageList):
        self.page_sources = page_sources

    def get_data(self) -> LIST_IN_TUPLE:
        (
            _type,
            status,
            region,
            title,
            link,
            _,
            registration_date,
            release_date,
            supplier,
        ) = ([], [], [], [], [], [], [], [], [])
        p = re.compile("[0-9]+")

        for page_source in self.page_sources:
            for post in page_source:
                items = post.find_all("td")
                _type.append(items.pop(0).get_text().strip())
                status.append(items.pop(0).get_text().strip())
                region.append(items.pop(0).get_text().strip())

                title_tag = items.pop(0)
                detail_id = p.findall(title_tag.find("a").attrs["href"])[0]
                url = f"https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcDetailView.do?pblancId={detail_id}"
                link.append(url)
                title.append(title_tag.get_text().strip())

                _.append(items.pop(0))

                registration_date.append(items.pop(0).get_text().strip())
                release_date.append(items.pop(0).get_text().strip())
                supplier.append(items.pop(0).get_text().strip())
        return (
            _type,
            status,
            region,
            title,
            registration_date,
            release_date,
            supplier,
            link,
        )

    def get_data_dict(self) -> Dict:
        data = self.get_data()
        data_dict = {
            "공급유형": data[0],
            "진행상태": data[1],
            "지역": data[2],
            "공고명": data[3],
            "모집공고일자": data[4],
            "당첨발표일자": data[5],
            "공급기관": data[6],
            "링크": data[7],
        }
        return data_dict

    def create_data_frame(self) -> DataFrame:
        data_dict = self.get_data_dict()
        data_frame = pd.DataFrame(data=data_dict)
        return data_frame


class MyHomeDataManager:
    def __init__(
        self,
        chrome_driver_path: str,
        page: int = 1,
        types: str = "student",
        region: str = "seoul",
    ) -> None:
        self.request = MyHomeRequest(chrome_driver_path, page, types, region)

    def create_page_sources(self) -> PageList:
        page_sources = self.request()
        return page_sources

    def get_data_frame(self, page_sources: PageList) -> DataFrame:
        data_table = MyHomeTable(page_sources)
        data_table = data_table.create_data_frame()
        return data_table

    def export_csv(self, path: str) -> None:
        page_sources = self.create_page_sources()
        data_table = self.get_data_frame(page_sources)

        data_table.to_csv(path, index=False)
