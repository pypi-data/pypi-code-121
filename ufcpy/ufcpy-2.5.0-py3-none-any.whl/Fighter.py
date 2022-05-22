import re
import urllib3
from bs4 import BeautifulSoup as bs

from .exceptions import UFCPyError


class Fighter:
    BASE_URL = "https://ufc.com/athlete"
    """
    Represents a UFC fighter 

    .. container:: operation

        .. describe:: str(x)

            Returns the fighter's name

    Parameters
    ----------
    fighter : :class:`str`
        The fighter to search for
    """

    def __init__(self, fighter: str = None):
        url = str(fighter).lower().replace(" ", "-")
        req = urllib3.PoolManager()
        res = req.request("GET", f"{self.BASE_URL}/{url}")
        self._check_response(res)
        self._parsed_url = bs(res.data, "html.parser")

    @staticmethod
    def _check_response(response):
        if response.status == 200:
            return response
        else:
            raise UFCPyError(f"Error: {response.reason}")

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """:class:`str`: The full name of the fighter"""
        return (
            self._parse_html("div", _class="c-hero--full__headline is-large-text")
            .get_text()
            .strip()
        )

    @property
    def nickname(self) -> str:
        """:class:`str`: The nickname of the fighter"""
        return (
            self._parse_html("div", _class="field field-name-nickname")
            .get_text()
            .strip('/"')
        )

    @property
    def age(self) -> str:
        """:class:`str`: The age of the fighter"""
        return self._parse_html(
            "div",
            _class="field field--name-age field--type-integer field--label-hidden field__item",
        ).get_text()

    @property
    def gender(self) -> str:
        """:class:`str`: The gender of the fighter"""
        rank = self.get_rank()
        if "Women" in rank:
            return "Woman"
        return "Man"

    @property
    def record(self) -> list:
        """:class:`list`: The record of the fighter in a list"""
        return re.findall(
            r"\d+",
            self._parse_html("div", _class="c-hero__headline-suffix tz-change-inner")
            .get_text()
            .split("•")[1],
        )

    @property
    def pretty_record(self) -> str:
        """:class:`str`: A prettified version of the record"""
        return f"{self.record[0]}-{self.record[1]}-{self.record[2]}"

    @property
    def wins(self) -> str:
        """:class:`str`: Amount of wins the fighter have"""
        return self.record[0]

    @property
    def losses(self) -> str:
        """:class:`str`: Amount of losses the fighter have"""
        return self.record[1]

    @property
    def draws(self) -> str:
        """:class:`str`: Amount of draws the fighter have"""
        return self.record[2]

    @property
    def weight(self) -> str:
        """:class:`str`: The weight the fighter likes to compete at"""
        return (
            self._parse_html("div", _class="c-bio__row--3col")
            .get_text()
            .split()[5]
            .replace(".00", "")
        )

    @property
    def hometown(self) -> str:
        """:class:`str`: The hometown of the fighter"""
        return (
            self._parse_html(
                "div", _class="c-bio__field c-bio__field--border-bottom-small-screens"
            )
            .get_text()
            .replace("Hometown", "")
            .strip()
        )

    @property
    def activity(self) -> str:
        """:class:`str`: The activity of the fighter"""
        return self._parse_html("div", _class="c-bio__text").get_text()

    @property
    def image_url(self) -> str:
        """:class:`str`: A image of the fighter"""
        return (
            self._parse_html("div", _class="c-bio__image--mobile")
            .find_next()
            .get("src")
        )

    @property
    def height_in_inch(self) -> str:
        """:class:`str`: The fighter's height in inches"""
        return (
            self._parse_html("div", _class="c-bio__row--3col")
            .get_text()
            .split()[3]
            .replace(".00", "")
        )

    @property
    def striking_accuracy(self) -> str:
        """:class:`str`: The striking accuracy of the fighter"""
        return (
            self._parse_html("div", _class="l-overlap-group__item--odd")
            .get_text()
            .strip()
            .split()[3]
        )

    @property
    def significant_strikes_landed(self) -> str:
        """:class:`str`: The significant strikes landed in the UFC career of the fighter"""
        return (
            self._parse_html("div", _class="l-overlap-group__item--odd")
            .get_text()
            .strip()
            .split()[8]
            .replace("Landed", "")
        )

    @property
    def significant_strikes_attempted(self) -> str:
        """:class:`str`: The significant strikes attemped in the UFC career of the fighter"""
        return (
            self._parse_html("div", _class="l-overlap-group__item--odd")
            .get_text()
            .strip()
            .split()[11]
            .replace("Attempted", "")
        )

    @property
    def grappling_accuracy(self) -> str:
        """:class:`str`: The grappling accuracy in the UFC career of the fighter"""
        return (
            self._parse_html("div", _class="l-overlap-group__item--even")
            .get_text()
            .strip()
            .split()[3]
        )

    @property
    def landed_takedowns(self) -> str:
        """:class:`str`: The takedowns landed in the UFC career of the fighter"""
        return (
            self._parse_html("div", _class="l-overlap-group__item--even")
            .get_text()
            .strip()
            .split()[7]
            .replace("Landed", "")
        )

    @property
    def attempted_takedowns(self) -> str:
        """:class:`str`: The takedowns attempted in the UFC career of the fighter"""
        return (
            self._parse_html("div", _class="l-overlap-group__item--even")
            .get_text()
            .strip()
            .split()[9]
            .replace("Attempted", "")
        )

    @property
    def debut(self) -> str:
        """:class:`str`: The UFC debut of the fighter"""
        stats = self._parse_html("div", _class="c-bio__row--3col", _find_all=True)[
            1
        ].text.split()
        return f"{stats[2]} {stats[3]} {stats[4]}"

    @property
    def reach(self) -> str:
        """:class:`str`: The reach of the fighter"""
        stats = self._parse_html("div", _class="c-bio__row--3col", _find_all=True)[
            1
        ].text.split()
        return stats[6]

    @property
    def leg_reach(self) -> str:
        """:class:`str`: The leg reach of the fighter"""
        stats = self._parse_html("div", _class="c-bio__row--3col", _find_all=True)[
            1
        ].text.split()
        return stats[9]

    def get_weight_class(self) -> str:
        """Returns the weight class the fighter competes in.

        .. note::

            This does *not* specify if the weight class is either mens or women

        Returns
        --------
        :class:`str`
            The weight class
        """
        if self.weight < "116":
            return "Strawweight"
        elif self.weight < "126":
            return "Flyweight"
        elif self.weight < "136":
            return "Bantamweight"
        elif self.weight < "146":
            return "Featherweight"
        elif self.weight == "156":
            return "Lightweight"
        elif self.weight == "171":
            return "Welterweight"
        elif self.weight == "186":
            return "Middleweight"
        elif self.weight == "206":
            return "Light Heavyweight"
        else:
            return "Heavyweight"

    def get_rank(self) -> str:
        """Retrieves the ranking of the fighter

        Returns
        --------
        :class:`str`
            The ranking of the fighter
        """
        rank = (
            self._parse_html("div", _class="c-hero__headline-suffix tz-change-inner")
            .get_text()
            .split("•")[0]
            .split("\n")
        )
        if "Champion" in rank[1]:
            return rank[1].strip()
        elif rank[1].strip().startswith("#"):
            return f"{rank[1].strip()} {rank[2].strip()}"
        else:
            return f"Unranked {rank[1].strip()} {rank[2].strip()}"

    def get_height_in_feet(self) -> str:
        height_feet = round(int(self.height_inches) / 12, 1)
        new_height = str(height_feet).replace(".", " ").split(" ")
        if new_height[1] == "0":
            return f"{new_height[0]} foot"
        else:
            return f"{new_height[0]} foot {new_height[1]} inch"

    def _parse_html(self, _element, _id=None, _class=None, _find_all: bool = False):
        parsed = self._parsed_url.find(_element) or ""
        if _find_all == False:
            if _id is not None:
                parsed = self._parsed_url.body.find(_element, {"id": _id})
            if _class is not None:
                parsed = self._parsed_url.body.find(_element, {"class": _class})
            if _id is not None and _class is not None:
                parsed = self._parsed_url.body.find(
                    _element, {"id": _id, "class": _class}
                )
        else:
            if _id is not None:
                parsed = self._parsed_url.body.find_all(_element, {"id": _id})
            if _class is not None:
                parsed = self._parsed_url.body.find_all(_element, {"class": _class})
            if _id is not None and _class is not None:
                parsed = self._parsed_url.body.find_all(
                    _element, {"id": _id, "class": _class}
                )
        return parsed
