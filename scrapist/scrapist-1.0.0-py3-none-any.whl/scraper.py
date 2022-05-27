import requests
from bs4 import BeautifulSoup, SoupStrainer
from .soup import Soup

class Scraper():
    """
        Used for making a scraper.
    """

    def __init__(self):
        self.session = requests.Session()

    def strainer(self, selector: str = None, tag: str = None, attrs = None):
        """
            Used for creating a soup strainer.

            Required Parameters
            -------------------
            `selector`: CSS selector for creating a strainer.
            `tag`: Tag for creating a strainer.
            NOTE: `selector` and `tag` both should not be given. Give either
            `selector` or `tag`.

            Optional Parameters
            -------------------
            `attrs`: Attribute of a tag with its value used as a criteria (Use
            only when `tag` parameter is used).
        """

        if selector:
            if tag or attrs:
                raise Exception("CSS selector and tag/attribute given. Please provide either CSS selector or tag (and attribute it's optional).")
            else:
                selector = selector.replace("[", " ")
                selector = selector.replace("]", "")
                split = selector.split(" ")
                if len(split) == 2:
                    attr_value = split[1].split("*=")
                    strainer = SoupStrainer(split[0], attrs = {attr_value[0], attr_value[1]})
                else:
                    strainer = SoupStrainer(split[0])
        else:
            strainer = SoupStrainer(tag, attrs = attrs)

        return strainer

    def scrape(self, url, strainer = None):
        """
            Used for scraping data from a web page.

            Required Parameters
            -------------------
            `url`: URL of the web page.

            Optional Parameters
            -------------------
            `strainer`: Soup strainer for parsing only the required part of the
            web page.
        """

        data = self.session.get(url)
        content = BeautifulSoup(data.content, "lxml", parse_only = strainer)
        soup = Soup(content)
        return soup