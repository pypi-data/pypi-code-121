import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterator, NoReturn

import yaml
from dateutil.parser import parse
from slugify import slugify
from statute_utils import StatuteID, get_member
from treeish import set_node_ids

from .statute_formatter import format_units
from .statute_formatter import get_first_short_title_from_units as get_short
from .statute_unformatted import (
    fix_absent_signer_problem,
    fix_multiple_sections_in_first,
)


@dataclass
class StatuteItem:
    """
    Utilizes `StatuteID` to get data from `*.yaml` files through the `category` and `idx` parameters. This will process data to generate a `StatuteItem` with titles that map to `TitleConvetions`."""

    path_to_statute_dir: Path

    def __post_init__(self):
        if not self.path_to_statute_dir.exists():
            raise Exception("Missing directory; cannot make StatuteItem.")

        details_path = self.path_to_statute_dir / "details.yaml"
        if not details_path.exists():
            raise Exception(f"Could not find {details_path=}")
        # Load metadata from details.yaml
        text = details_path.read_text()
        self.raw_data = yaml.load(text, Loader=yaml.SafeLoader)
        if "numeral" not in self.raw_data:
            raise Exception(f"Missing numeral in {self.raw_data=}")
        if "category" not in self.raw_data:
            raise Exception(f"Missing category in {self.raw_data=}")
        if "date" not in self.raw_data:
            raise Exception(f"Missing date in {self.raw_data=}")
        self.category = self.raw_data["category"]
        self.idx = self.raw_data["numeral"]
        self.member: StatuteID = get_member(self.category)
        self.category_label: str = self.get_category_label()
        self.specified_date: date = parse(self.raw_data["date"]).date()
        self.emails: list[str] = self.raw_data.get("emails", None)

        # Populate units
        self.set_units()
        self.raw_data = fix_absent_signer_problem(self.raw_data)
        self.raw_data = fix_multiple_sections_in_first(self.raw_data)
        format_units(self.raw_data["units"])  # adds a short title, if possible
        set_node_ids(self.raw_data["units"])  # adds id to each node
        self.units: list[dict] = self.raw_data["units"]

        # Get titles
        self.short_title = get_short({"units": self.units})
        self.serial_title = self.member.make_title(self.idx.upper())
        self.titles: dict = {
            "short": self.short_title,
            "official": self.official_title,
            "serial": self.serial_title,
            "aliases": self.raw_data.get("aliases", []),
        }

    def get_category_label(self):
        text = self.member.value[0]
        if the_word_number := self.member.value[1]:
            text = f"{text} {the_word_number}"  # e.g. No./Blg. if present
        return text

    def set_units(self) -> NoReturn | dict:
        units_path = None
        prefer = self.path_to_statute_dir / f"{self.category}{self.idx}.yaml"
        default = self.path_to_statute_dir / "units.yaml"
        if prefer.exists():
            units_path = prefer
        elif default.exists():
            units_path = default
        if not units_path:
            raise Exception(f"No unit path found {self.path_to_statute_dir=}")
        self.raw_data["units"] = yaml.load(
            units_path.read_text(), Loader=yaml.SafeLoader
        )
        if "units" not in self.raw_data:
            raise Exception(f"Units not added in {self.units_path=}")
        if not isinstance(self.raw_data["units"], list):
            raise Exception(f"Units not formatted in {self.units_path=}")

    @property
    def official_title(self) -> str | None:
        return self.raw_data.get("law_title", None) or self.raw_data.get(
            "item", None
        )

    @property
    def slug(self) -> str:
        return slugify(f"{self.category}-{self.idx}-{self.raw_data['date']}")

    @property
    def extracted_titles(self) -> Iterator[dict]:
        """Populates the Statute Titles table."""
        base = {"statute_id": self.slug, "basis": None}
        for k, v in self.titles.items():
            if k == "aliases":
                for alias_title in v:
                    if alias_title and alias_title != "":
                        yield base | {"category": "alias", "text": alias_title}
            else:
                if v and v != "":
                    if (
                        v
                        == "Short title indicators but no quoted pattern found."
                    ):
                        yield base | {"category": k, "text": None, "basis": v}
                    else:
                        yield base | {"category": k, "text": v}

    @property
    def extracted_fields(self) -> dict:
        """Populates the Statutes table."""
        return {
            "pk": self.slug,
            "cat": self.category,
            "idx": self.idx,
            "date": self.specified_date,
            "units": json.dumps({"id": "1.", "units": self.units}),
            "titles_detected": list(self.extracted_titles),
        }


def extract_statutes(statute_folder: Path) -> Iterator[dict] | NoReturn:
    for path in statute_folder.glob("**/details.yaml"):
        try:
            item = StatuteItem(path.parent)
            yield item.extracted_fields
        except Exception as e:
            print(f"{path.parent=} issue: {e=}")
