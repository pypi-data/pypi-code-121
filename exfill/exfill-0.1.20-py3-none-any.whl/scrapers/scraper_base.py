from abc import abstractmethod


class Scraper:
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def scrape_postings(self):
        "Scrape job postings"

    @abstractmethod
    def export(self):
        "Export postings to file"
