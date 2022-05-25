"""Parser module will process and aggregate job posting files.
"""
import logging
import os
import re
from configparser import NoOptionError, NoSectionError
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from pandas import DataFrame
from parsers.parser_base import Parser


class NoImportFiles(Exception):
    pass


class InvalidConfigArg(Exception):
    pass


class InvalidFileName(Exception):
    pass


class EmptySoup(Exception):
    "That is some bad soup"
    pass


@dataclass
class Posting:
    # config props
    input_file_name: str
    input_file: str = ""
    soup: BeautifulSoup = field(default=BeautifulSoup(), repr=False)

    # export props
    jobid: str = ""
    url: str = ""
    title: str = ""
    workplace_type: str = ""
    company_name: str = ""
    company_url: str = ""
    company_size: str = ""
    company_industry: str = ""
    hours: str = ""
    level: str = ""

    # used to replace asdict() as that has limited options
    def to_dict(self) -> dict:
        return {
            "jobid": self.jobid,
            "url": self.url,
            "title": self.title,
            "company_name": self.company_name,
            "workplace_type": self.workplace_type,
            "company_url": self.company_url,
            "company_size": self.company_size,
            "company_industry": self.company_industry,
            "hours": self.hours,
            "level": self.level,
        }


class LinkedinParser(Parser):
    def __init__(self, config):
        self.config = config

        # lists to hold each posting
        self.postings: list[dict] = []
        self.postings_err: list[dict] = []

        try:
            self.output_file = config.get("Parser", "output_file")
            self.output_file_errors = config.get("Parser", "output_file_err")
            self.input_dir = config.get("Parser", "input_dir")
        except NoSectionError as e:
            raise InvalidConfigArg(e.message) from None
        except NoOptionError as e:
            raise InvalidConfigArg(e.message) from None

    # parser
    def parse_export(self) -> None:
        """Export all postings to CSV file"""
        logging.info(f"Exporting to {self.output_file}")
        DataFrame(self.postings).to_csv(self.output_file, index=False)

    # parser
    def parse_postings(self) -> None:

        if len(os.listdir(self.input_dir)) == 0:
            raise NoImportFiles("There are no files to import")

        for input_file_name in os.listdir(self.input_dir):

            post = Posting(input_file_name)

            # posting - set config props
            post.input_file = self.set_posting_input_file(
                self.input_dir, input_file_name
            )
            post.soup = self.set_posting_soup(post.input_file)

            # posting - set export props
            post.jobid = self.set_posting_jobid(input_file_name)
            post.url = self.set_posting_url(post.jobid)
            post.title = self.set_posting_title(post.soup)
            post.workplace_type = self.set_posting_workplace_type(post.soup)
            post.company_name = self.set_posting_company_name(post.soup)
            post.company_url = self.set_posting_company_url(post.soup)
            (
                post.company_size,
                post.company_industry,
                post.hours,
                post.level,
            ) = self.set_posting_company_details(post.soup)

            self.postings.append(post.to_dict())

        self.parse_export()

    # input_file - config prop
    def set_posting_input_file(
        self, input_dir: str, input_file_name: str
    ) -> str:
        return os.path.join(input_dir, input_file_name)

    # soup - config prop
    def set_posting_soup(self, input_file: str) -> BeautifulSoup:

        try:
            with open(input_file, mode="r", encoding="UTF-8") as f:
                soup = BeautifulSoup(f, "html.parser")
        except FileNotFoundError as e:
            raise InvalidFileName(e) from None
        except OSError as e:
            raise InvalidFileName(e) from None
        else:
            return soup

    # jobid - export prop
    def set_posting_jobid(self, input_file_name: str) -> str:
        try:
            jobid = input_file_name.split("_")[1]
        except IndexError as e:
            raise InvalidFileName(e) from None
        else:
            logging.info(f"{jobid} - Parsing job ")
            return jobid

    # url - export prop
    def set_posting_url(self, jobid: str) -> str:
        return "https://www.linkedin.com/jobs/view/" + jobid

    # title - export prop
    def set_posting_title(self, soup: BeautifulSoup) -> str:

        try:
            assert type(soup) is BeautifulSoup
            title = soup.find(class_="t-24")

            if title is None:
                raise EmptySoup("workplace_type is missing")

        except EmptySoup as e:
            logging.error(f"Err msg - {e}")
            return "missing"
        except AssertionError:
            logging.error(f"Soup should be BeautifulSoup, not {type(soup)}")
            return "error"
        else:
            return title.text.strip()

    # workplace_type - export prop
    def set_posting_workplace_type(self, soup: BeautifulSoup) -> str:

        try:
            assert type(soup) is BeautifulSoup

            # workplace_type. looking for remote (f_WT=2 in url)
            workplace_type = soup.find(
                class_="jobs-unified-top-card__workplace-type"
            )

            if workplace_type is None:
                raise EmptySoup("workplace_type is missing")

        except EmptySoup as e:
            logging.error(f"Err msg - {e}")
            return "missing"
        except AssertionError:
            logging.error(f"Soup should be BeautifulSoup, not {type(soup)}")
            return "error"
        else:
            return workplace_type.text.strip()

    # company_name - export prop
    def set_posting_company_name(self, soup: BeautifulSoup) -> str:

        try:
            assert type(soup) is BeautifulSoup
            company_name = soup.find(
                "span", class_="jobs-unified-top-card__company-name"
            ).find("a")

        # AttributeError can occur on second find()
        except AttributeError as e:
            logging.error(f"Err msg - {e}")
            return "missing"
        except AssertionError:
            logging.error(f"Soup should be BeautifulSoup, not {type(soup)}")
            return "error"
        else:
            return company_name.text.strip()

    # company_url - export prop
    def set_posting_company_url(self, soup: BeautifulSoup) -> str:

        try:
            assert type(soup) is BeautifulSoup
            company_url = soup.find(
                "span", class_="jobs-unified-top-card__company-name"
            ).find("a")["href"]

        # AttributeError can occur on second find()
        except AttributeError as e:
            logging.error(f"Err msg - {e}")
            return "missing"
        except AssertionError:
            logging.error(f"Soup should be BeautifulSoup, not {type(soup)}")
            return "error"
        else:
            return company_url.strip()

    # company_details - export props
    def set_posting_company_details(self, soup: BeautifulSoup) -> tuple:

        try:
            assert type(soup) is BeautifulSoup
            company_details = soup.find_all(string=re.compile(r" · "))
        except AssertionError:
            logging.error(f"Soup should be BeautifulSoup, not {type(soup)}")
            return "error", "error", "error", "error"

        company_size: str = "missing"
        company_industry: str = "missing"
        hours: str = "missing"
        level: str = "missing"

        for section in company_details:

            section = section.strip()

            # remove leading dots if they exist
            if section[0] == "·":
                section = section[1:].strip()

            if "employees" in section and section.count(" · ") == 1:
                company_size, company_industry = section.split(" · ")
            elif "Full-time" in section and section.count(" · ") == 1:
                hours, level = section.split(" · ")

        return company_size, company_industry, hours, level
