from .selection import Selection

class Soup():
    def __init__(self, soup):
        self.soup = soup
    
    def css(self, selector):
        """
            (Scrapy-style)
            Get CSS selector to get the specified part/tag of the web page.

            Required Parameters
            -------------------
            `selector`: CSS selector to get the specified part/tag of the web
            page.
        """

        selectors = []

        split = selector.split(" ")
        for i in split:
            i = i.replace("[", " ")
            i = i.replace("]", "")
            i_split = i.split(" ")
            if len(i_split) == 2:
                further = i_split[1].split("::")
                attr_value = further[0].split("*=")
                if len(further) == 2:
                    if further[1] == "text":
                        selectors.append({
                            "tag": i_split[0],
                            "attr": attr_value[0],
                            "value": attr_value[1],
                            "text": True,
                            "attrt": None
                        })
                    else:
                        attr = further[1].replace("attr(", "")
                        attr = attr.replace(")", "")
                        selectors.append({
                            "tag": i_split[0],
                            "attr": attr_value[0],
                            "value": attr_value[1],
                            "text": False,
                            "attrt": attr
                        })
                else:
                    selectors.append({
                        "tag": i_split[0],
                        "attr": attr_value[0],
                        "value": attr_value[1],
                        "text": False,
                        "attrt": None
                    })
            else:
                further = i.split("::")
                if len(further) == 2:
                    if further[1] == "text":
                        selectors.append({
                            "tag": further[0],
                            "attr": None,
                            "value": None,
                            "text": True,
                            "attrt": None
                        })
                    else:
                        attr = further[1].replace("attr(", "")
                        attr = attr.replace(")", "")
                        selectors.append({
                            "tag": further[0],
                            "attr": None,
                            "value": None,
                            "text": False,
                            "attrt": attr
                        })
                else:
                    selectors.append({
                        "tag": further[0],
                        "attr": None,
                        "value": None,
                        "text": False,
                        "attrt": None
                    })

        selection = Selection(self.soup, selectors)
        return selection

    def find(self, tag: str, attrs = None):
        """
            (BeautifulSoup-style)
            Getting the first specified part/tag of a web page.

            Required Parameters
            -------------------
            `tag`: Tag for getting the first specified part/tag of a web page.

            Optional Parameters
            -------------------
            `attrs`: Attribute and value used as a criteria.
        """

        data = self.soup.find(tag, attrs = attrs)
        data_soup = Soup(data)

        return data

    def find_all(self, tag: str, attrs = None):
        """
            (BeautifulSoup-style)
            Getting all the specified parts/tags of a web page.

            Required Parameters
            -------------------
            `tag`: Tag for getting all the specified parts/tags of a web page.

            Optional Parameters
            -------------------
            `attrs`: Attribute and value used as a criteria.
        """

        data = self.soup.find_all(tag, attrs = attrs)
        data_soup = Soup(data)

        return data