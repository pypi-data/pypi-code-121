import time
from typing import Final, List, Tuple, Dict
from bs4 import ResultSet
import pandas as pd
from selenium.webdriver.chrome.webdriver import WebDriver
from house_info.base import BaseSelRequest
from house_info.utils import DataFrame, LIST_IN_TUPLE, PageList


# TODO: typing needed
class StationAreaRequest(BaseSelRequest):
    """
    역세권 청년주택 정보 수집
    민간, 공공 포함
    :ChromeDriver 필요
    """

    URL: Final = "https://soco.seoul.go.kr/youth/bbs/BMSR00015/list.do?menuNo=400008"

    def __init__(self, chrome_driver_path: str, page: int = 1) -> None:
        super(StationAreaRequest, self).__init__(chrome_driver_path, page)

    def get_post_list(self, soup) -> List:
        post_list = soup.find("tbody", attrs={"id": "boardList"}).find_all("tr")
        if not post_list:
            return None
        return post_list

    def move_next_page(self, browser: WebDriver, page: int):
        browser.execute_script(f"cohomeList({page})")
        return browser

    def create_post_list_sources(self) -> PageList[ResultSet]:
        browser = self.browser_open_headless()
        page_source = self.get_page_source(browser)
        parsed_html = self.parse_html(page_source)
        post_list = self.get_post_list(parsed_html)
        post_list_sources = PageList([post_list])

        for page in range(2, self.page + 1):
            self.move_next_page(browser, page)
            time.sleep(0.1)
            # TODO: neeed to extract func
            page_source = self.get_page_source(browser)
            parsed_html = self.parse_html(page_source)
            post_list = self.get_post_list(parsed_html)

            if not post_list:
                break
            post_list_sources.append(post_list)
        return post_list_sources

    def __call__(self):
        return self.create_post_list_sources()


class StationAreaTable:
    def __init__(self, page_sources: LIST_IN_TUPLE) -> None:
        self.page_sources = page_sources

    def get_data(self) -> Tuple[List]:
        index, _type, title, link, registration_date, subscription_date, manager = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )

        for page_source in self.page_sources:
            for post in page_source:
                items = post.find_all("td")
                index.append(items.pop(0).get_text().strip())
                _type.append(items.pop(0).get_text().strip())

                title_tag = items.pop(0)
                url = (
                    "https://soco.seoul.go.kr/youth/bbs/BMSR00015/"
                    + title_tag.find("a").attrs["href"]
                )
                link.append(url)

                title.append(title_tag.get_text().strip())
                registration_date.append(items.pop(0).get_text().strip())
                subscription_date.append(items.pop(0).get_text().strip())
                manager.append(items.pop(0).get_text().strip())
        return index, _type, title, registration_date, subscription_date, manager, link

    def get_data_dict(self) -> Dict[str, List[str]]:
        data = self.get_data()
        data_dict = {
            "인덱스": data[0],
            "유형": data[1],
            "제목": data[2],
            "게시일": data[3],
            "청약신청일": data[4],
            "담당자": data[5],
            "링크": data[6],
        }
        return data_dict

    def create_data_frame(self) -> DataFrame:
        data_dict = self.get_data_dict()
        data_frame = pd.DataFrame(data=data_dict)
        return data_frame


class StationAreaDataManager:
    def __init__(self, chrome_driver_path: str, page: int = 1) -> None:
        self.request = StationAreaRequest(chrome_driver_path, page)

    def create_page_sources(self) -> ResultSet:
        page_sources = self.request()
        return page_sources

    def get_data_frame(self, page_sources) -> DataFrame:
        data_table = StationAreaTable(page_sources)
        data_table = data_table.create_data_frame()
        return data_table

    def export_csv(self, path: str) -> None:
        page_sources = self.create_page_sources()
        data_table = self.get_data_frame(page_sources)

        data_table.to_csv(path, index=False)
