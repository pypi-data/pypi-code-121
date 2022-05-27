"""Docstring."""

import argparse
import csv
import fileinput
import re
import time
from pathlib import Path


class Netflix:
    """Docstring."""

    DEFAULT_DATA_FILE = Path.home().joinpath("Downloads/NetflixViewingHistory.csv")
    RE_SEASON = re.compile(
        r"^((Season|Volume|Part|Collection|Chapter|Series) ([\dIVX]+)|^Limited Series)$"
    )
    RE_EPISODE = re.compile(r"^Episode (\d+)$")
    IFS = ": "
    OFS = ", "
    INDENT = " " * 4

    def __init__(self, options: argparse.ArgumentParser) -> None:
        """Docstring."""

        self.options = options
        # self.histogram = {x: 0 for x in range(1, 6)}

    def print_report(self):
        """Read netfile history `file` and print report to `stdout`."""

        titles = self.read_history_file()
        self.report(titles)

    def read_history_file(self):
        """Docstring."""

        titles = {}  # return this
        for title, date in csv.reader(fileinput.input(self.options.file)):

            if title == "Title" and date == "Date":
                continue

            title, season, episode = self._parse_title(title)

            if (title2 := titles.get(title)) is None:
                titles[title] = {}
                title2 = titles[title]

            if (season2 := title2.get(season)) is None:
                title2[season] = {}
                season2 = title2[season]

            season2[episode] = time.strftime("%Y-%m-%d", time.strptime(date, "%m/%d/%y"))

        return titles

    def _parse_title(self, title):

        parts = title.split(self.IFS)
        assert 1 <= len(parts) <= 5
        # self.histogram[len(parts)] += 1

        title_parts = []
        subtitle_parts = []
        season = ""
        episode = ""

        for part in parts:
            if self.RE_SEASON.search(part):
                if not season:
                    season = part
                else:
                    subtitle_parts.append(part)
            elif self.RE_EPISODE.search(part):
                assert not episode
                episode = part
            elif season or episode:
                subtitle_parts.append(part)
            else:
                title_parts.append(part)

        title = self.IFS.join(title_parts)
        if not episode:
            episode = self.IFS.join(subtitle_parts)
        else:
            assert len(subtitle_parts) == 0

        return title, season, episode

    # -------------------------------------------------------------------------------

    def report(self, titles):
        """Print netflix history report."""

        filtered = (
            self.options.movies_only or self.options.series1_only or self.options.series2_only
        )

        # pylint: disable=too-many-nested-blocks

        for title, seasons in titles.items():
            if episodes := seasons.get(""):
                if date := episodes.get(""):
                    # movie
                    if not filtered or self.options.movies_only:
                        print(date + self.INDENT + title)
                else:
                    # series, (no seasons), episodes
                    if not filtered or self.options.series1_only:
                        date = max(list(episodes.values()))
                        print(
                            date
                            + self.INDENT
                            + self.OFS.join([title, self._pluralize(len(episodes), "episode")])
                        )
                        if self.options.episodes:
                            for episode, date in episodes.items():
                                print(date + self.INDENT + self.INDENT + episode)

            # series, seasons, episodes
            elif not filtered or self.options.series2_only:
                n_episodes = sum([len(episodes) for episodes in seasons.values()])
                date = max(list(list(seasons.values())[0].values()))
                print(
                    date
                    + self.INDENT
                    + self.OFS.join(
                        [
                            title,
                            self._pluralize(len(seasons), "season"),
                            self._pluralize(n_episodes, "episode"),
                        ]
                    )
                )

                if not self.options.seasons and not self.options.episodes:
                    continue

                for season, episodes in seasons.items():
                    date = max(list(episodes.values()))
                    print(
                        date
                        + self.INDENT
                        + self.INDENT
                        + self.OFS.join(
                            [
                                season,
                                self._pluralize(len(episodes), "episode"),
                            ]
                        )
                    )

                    if self.options.episodes:
                        for episode, date in episodes.items():
                            print(date + self.INDENT + self.INDENT + self.INDENT + episode)
        #
        # print("count nparts ntitles", self.histogram)

    # -------------------------------------------------------------------------------

    @staticmethod
    def _pluralize(number, thing):
        """Return string that describes some number of things."""
        return str(number) + " " + thing + ("s" if number != 1 else "")
