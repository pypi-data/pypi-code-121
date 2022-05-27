class Selection():
    def __init__(self, soup, selectors):
        self.data = [soup]
        self.selectors = selectors

    def get(self):
        """
            Get the first specified part/tag of a web page.
        """

        for selector in self.selectors:
            if selector["attr"]:
                if selector["text"]:
                    self.data = self.data[0].find(selector["tag"], attrs = {selector["attr"], selector["value"]}).text
                elif selector["attrt"]:
                    self.data = self.data[0].find(selector["tag"], attrs = {selector["attr"], selector["value"]})[selector["attrt"]]
                else:
                    self.data = self.data[0].find(selector["tag"], attrs = {selector["attr"], selector["value"]})
            else:
                if selector["text"]:
                    self.data = self.data[0].find(selector["tag"]).text
                elif selector["attrt"]:
                    self.data = self.data[0].find(selector["tag"])[selector["attrt"]]
                else:
                    self.data = self.data[0].find(selector["tag"])

        return self.data

    def getall(self):
        """
            Get all the specified parts/tags of a web page.
        """

        for selector in self.selectors:
            if selector != self.selectors[-1]:
                if selector["attr"]:
                    if selector["text"]:
                        raise Exception("Text is not allowed to be taken in any of the tag selectors except for the last one.")
                    elif selector["attrt"]:
                        raise Exception("Attribute is not allowed to be taken in any of the tag selectors except for the last one.")
                    else:
                        self.data = self.data[0].find_all(selector["tag"], attrs = {selector["attr"], selector["value"]})
                else:
                    if selector["text"]:
                        raise Exception("Text is not allowed to be taken in any of the tag selectors except for the last one.")
                    elif selector["attrt"]:
                        raise Exception("Attribute is not allowed to be taken in any of the tag selectors except for the last one.")
                    else:
                        self.data = self.data[0].find_all(selector["tag"])
            else:
                if selector["attr"]:
                    if selector["text"]:
                        self.data[0] = [tag.text for tag in self.data[0].find_all(selector["tag"])]
                    elif selector["attrt"]:
                        self.data[0] = [tag[selector["attrt"]] for tag in self.data[0].find_all(selector["tag"])]
                    else:
                        self.data[0] = [tag for tag in self.data[0].find_all(selector["tag"])]
                else:
                    if selector["text"]:
                        self.data[0] = [tag.text for tag in self.data[0].find_all(selector["tag"])]
                    elif selector["attrt"]:
                        self.data[0] = [tag[selector["attrt"]] for tag in self.data[0].find_all(selector["tag"])]
                    else:
                        self.data[0] = [tag for tag in self.data[0].find_all(selector["tag"])]

        return self.data[0]