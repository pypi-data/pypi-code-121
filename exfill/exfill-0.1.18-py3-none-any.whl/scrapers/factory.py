from scrapers.linkedin_scraper import LinkedinScraper


class ScraperFactory:
    @staticmethod
    def create(scraper_type: str, config):
        if scraper_type == "linkedin":
            return LinkedinScraper(config)
