import abc

import pandas as pd


class ApiScraper:

    extracted_content = []
    page_count = 0

    @abc.abstractmethod
    def get_content(self, content):
        ...

    @abc.abstractmethod
    def get_next(self):
        ...

    def write_csv(self, path):
        df = pd.concat([pd.DataFrame(url) for url in self.extracted_content])
        df.to_csv(path, index=None)

    def print_content(self, page_number=-1):
        while result := self.get_content():
            print("Scrap page ", self.page_count)
            self.extracted_content.append(result)
            self.page_count += 1
            if page_number != -1 and page_number == self.page_count:
                break

        return self
