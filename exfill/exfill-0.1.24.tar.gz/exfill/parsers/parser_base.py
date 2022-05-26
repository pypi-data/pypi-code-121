from abc import abstractmethod


class Parser:
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def parse_postings(self):
        "Parse job postings"
