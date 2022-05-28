import abc

import pandas as pd

from podcast_scraper.atom import Atom


class ApiScraper:

    extracted_content = []
    page_count = 0

    @abc.abstractmethod
    def get_content(self):
        ...

    def write_csv(self, path):
        df = pd.concat([pd.DataFrame(url) for url in self.extracted_content])
        df.to_csv(path, index=None)
        return self

    def print_csv(self):
        df = pd.concat([pd.DataFrame(url) for url in self.extracted_content])
        print(df.to_csv(index=None))
        return self

    def print_rss(self):
        df = pd.concat([pd.DataFrame(url) for url in self.extracted_content])
        atom = Atom()
        for row in df.itertuples():
            atom.add_items(row)

        return atom.to_string()

    def write_rss(self, path):
        with open(path, "w") as file:
            file.write(self.print_rss())

    def print_content(self, page_number=-1):
        while result := self.get_content():
            print("Scrap page ", self.page_count)
            self.extracted_content.append(result)
            self.page_count += 1
            if page_number != -1 and page_number == self.page_count:
                break

        return self
