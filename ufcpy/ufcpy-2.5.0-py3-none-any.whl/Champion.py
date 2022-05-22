import urllib3
from bs4 import BeautifulSoup as bs

from .Fighter import Fighter


class Champion:
    BASE_URL = "https://ufc.com/athletes"

    def __init__(self):
        """
        Reprents all of the current champions
        """
        req = urllib3.PoolManager()
        res = req.request("GET", self.BASE_URL)
        self._parsed_url = bs(res.data, "html.parser")
        self._div = self._parsed_url.find(
            class_="views-element-container block block-views block-views-blockathletes-titleholders-block-1"
        )
        self._athlete_blocks = self._div.find_all(
            class_="node node--type-athlete node--view-mode-listing-detail clearfix athlete-listing-detail-wrp"
        )

    def all_names(self) -> list:
        """:class:`List[str]`: All of the current champions names"""
        athletes = []
        for athlete in self._athlete_blocks:
            name = athlete.find_all(
                class_="field field--name-title field--type-string field--label-hidden"
            )
            name_string = "".join(str(e) for e in name)
            name = name_string.split(">")[1].split("<")[0]
            athletes.append(name)
        return athletes

    def all_objects(self) -> list:
        """:class:`List[Fighter]`: All of the current champions in `Fighter` objects"""
        athletes = []
        for athlete in self.all_names():
            athletes.append(Fighter(athlete))
        return athletes

    @property
    def womens_strawweight(self) -> Fighter:
        """:class:`Fighter`: The current Women's Strawweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Strawweight" and athlete.gender == "Woman":
                return athlete or None

    @property
    def womens_flyweight(self) -> Fighter:
        """:class:`Fighter`: The current Women's Flyweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Flyweight" and athlete.gender == "Woman":
                return athlete or None

    @property
    def womens_bantamweight(self) -> Fighter:
        """:class:`Fighter`: The current Women's Bantamweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Bantamweight" and athlete.gender == "Woman":
                return athlete or None

    @property
    def womens_featherweight(self) -> Fighter:
        """:class:`Fighter`: The current Women's Featherweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Featherweight" and athlete.gender == "Woman":
                return athlete or None

    @property
    def flyweight(self) -> Fighter:
        """:class:`Fighter`: The current Flyweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Flyweight" and athlete.gender == "Man":
                return athlete or None

    @property
    def bantamweight(self) -> Fighter:
        """:class:`Fighter`: The current Bantamweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Bantamweight" and athlete.gender == "Man":
                return athlete or None

    @property
    def featherweight(self) -> Fighter:
        """:class:`Fighter`: The current Featherweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Featherweight" and athlete.gender == "Man":
                return athlete or None

    @property
    def lightweight(self) -> Fighter:
        """:class:`Fighter`: The current Lightweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Lightweight":
                return athlete or None

    @property
    def welterweight(self) -> Fighter:
        """:class:`Fighter`: The current Welterweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Welterweight":
                return athlete or None
    
    @property
    def middleweight(self) -> Fighter:
        """:class:`Fighter`: The current Middleweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Middleweight":
                return athlete or None

    @property
    def lightheavyweight(self) -> Fighter:
        """:class:`Fighter`: The current Light Heavyweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Light Heavyweight":
                return athlete or None
    
    @property
    def heavyweight(self) -> Fighter:
        """:class:`Fighter`: The current Heavyweight champion"""
        for athlete in self.all_objects():
            if athlete.get_weight_class() == "Heavyweight":
                return athlete or None