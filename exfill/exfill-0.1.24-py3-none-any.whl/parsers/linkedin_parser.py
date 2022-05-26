"""Parser module will process and aggregate job posting files.
"""
import csv
import logging
import re
from configparser import NoOptionError, NoSectionError
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup

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
    input_file: Path = Path()
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
            self.input_dir = Path(
                Path.cwd() / config.get("Parser", "input_dir")
            )
        except NoSectionError as e:
            raise InvalidConfigArg(e.message) from None
        except NoOptionError as e:
            raise InvalidConfigArg(e.message) from None

    # parser
    def parse_export(self) -> None:
        """Export all postings to CSV file"""
        logging.info(f"Exporting to {self.output_file}")
        with open(self.output_file, "w") as f:
            writer = csv.writer(f, delimiter="|")

            writer.writerow(self.postings[0].keys())  # headers
            for posting in self.postings:
                writer.writerow(posting.values())

    # parser
    def parse_postings(self) -> None:

        if not any(self.input_dir.iterdir()):
            raise NoImportFiles("There are no files to import")

        for input_file_name in self.input_dir.iterdir():

            post = Posting(input_file_name)

            # posting - load config props
            post.input_file = self.load_posting_input_file(
                self.input_dir, input_file_name
            )
            post.soup = self.load_posting_soup(post.input_file)

            # posting - load export props
            post.jobid = self.load_posting_jobid(input_file_name)
            post.url = self.load_posting_url(post.jobid)
            post.title = self.load_posting_title(post.soup)
            post.workplace_type = self.load_posting_workplace_type(post.soup)
            post.company_name = self.load_posting_company_name(post.soup)
            post.company_url = self.load_posting_company_url(post.soup)
            (
                post.company_size,
                post.company_industry,
                post.hours,
                post.level,
            ) = self.load_posting_company_details(post.soup)

            self.postings.append(post.to_dict())

        self.parse_export()

    # input_file - config prop
    def load_posting_input_file(
        self, input_dir: Path, input_file_name: Path
    ) -> Path:
        return Path(input_dir / input_file_name)

    # soup - config prop
    def load_posting_soup(self, input_file: Path) -> BeautifulSoup:
        try:
            with open(input_file, mode="r", encoding="UTF-8") as f:
                soup = BeautifulSoup(f, "html.parser")
        except FileNotFoundError as e:
            logging.error(f"Err msg - {e}")
            raise e
        else:
            return soup

    # jobid - export prop
    def load_posting_jobid(self, input_file_name: str) -> str:
        try:
            jobid = str(input_file_name).split("_")[1]
        except IndexError as e:
            raise InvalidFileName(e) from None
        else:
            logging.info(f"{jobid} - Parsing job ")
            return jobid

    # url - export prop
    def load_posting_url(self, jobid: str) -> str:
        return "https://www.linkedin.com/jobs/view/" + jobid

    # title - export prop
    def load_posting_title(self, soup: BeautifulSoup) -> str:

        try:
            title = soup.find(class_="t-24").text.strip()

        except Exception as e:
            logging.error(f"Err msg - {e}")

            if isinstance(e, AttributeError):
                return "missing"
            return "error"
        else:
            return title

    # workplace_type - export prop
    def load_posting_workplace_type(self, soup: BeautifulSoup) -> str:

        try:
            # looking for remote (f_WT=2 in url)
            workplace_type = soup.find(
                class_="jobs-unified-top-card__workplace-type"
            ).text.strip()

        except Exception as e:
            logging.error(f"Err msg - {e}")

            if isinstance(e, AttributeError):
                return "missing"
            return "error"
        else:
            return workplace_type

    # company_name - export prop
    def load_posting_company_name(self, soup: BeautifulSoup) -> str:

        try:
            company_name = (
                soup.find("span", class_="jobs-unified-top-card__company-name")
                .find("a")
                .text.strip()
            )

        except Exception as e:
            logging.error(f"Err msg - {e}")

            # AttributeError can occur on second find()
            if isinstance(e, AttributeError):
                return "missing"
            return "error"
        else:
            return company_name

    # company_url - export prop
    def load_posting_company_url(self, soup: BeautifulSoup) -> str:

        try:
            company_url = soup.find(
                "span", class_="jobs-unified-top-card__company-name"
            ).find("a")["href"]

        except Exception as e:
            logging.error(f"Err msg - {e}")
            if isinstance(e, (AttributeError, KeyError)):
                return "missing"
            return "error"
        else:
            return company_url

    # company_details - export props
    def load_posting_company_details(self, soup: BeautifulSoup) -> tuple:

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
