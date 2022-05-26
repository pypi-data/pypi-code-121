from argparse import ArgumentParser, Namespace

from clime_bus_factor.version import version

name: str = "PRiMe"
versionName: str = "PRiMe Bus Factor Module"
authors: list = [
    "Nicholas M. Synovic",
    "Matthew Hyatt",
    "George K. Thiruvathukal",
]

from argparse import HelpFormatter
from operator import attrgetter


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter("option_strings"))
        super(SortingHelpFormatter, self).add_arguments(actions)


def busFactorArgs() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog=f"{name} Bus Factor Calculator",
        description="A tool to calculate the bus factor of a Git repository",
        epilog=f"Author(s): {', '.join(authors)}",
        formatter_class=SortingHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Commits JSON file. DEFAULT: ./commits_loc.json",
        default="commits_loc.json",
    )
    parser.add_argument(
        "-b",
        "--bin",
        help="Bin containing the number of days between computed bus factor values. DEFAULT: 1",
        type=int,
        default=1,
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Display version of the tool",
        action="version",
        version=f"{versionName}: {version()} ",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON file. DEFAULT: ./bus_factor.json",
        type=str,
        default="bus_factor.json",
    )
    parser.add_argument(
        "-a",
        "--alpha",
        help="The percent change of the code base a developer needs to contribute in a time interval . DEFAULT: 0.8",
        type=float,
        default=0.8,
    )
    return parser.parse_args()


def graphArgs() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog=f"{name} Bus Factor Grapher",
        description="A tool to graph the bus factor of a repository",
        epilog=f"Author(s): {', '.join(authors)}",
        formatter_class=SortingHelpFormatter,
    )
    parser.add_argument(
        "-y",
        "--y-data",
        help="The key to use for graphing the y axis data. DEFAULT: busFactor",
        type=str,
        default="busFactor",
    )
    parser.add_argument(
        "-i",
        "--input",
        help=f"JSON export from clime-git-bus-factor-compute. DEFAULT: ./bus_factor.json",
        type=str,
        required=False,
        default="bus_factor.json",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Filename of the graph. DEFAULT: ./bus_factor.pdf",
        type=str,
        required=False,
        default="bus_factor.pdf",
    )
    parser.add_argument(
        "--type",
        help="Type of figure to plot. DEFAULT: bar",
        type=str,
        required=False,
        default="bar",
    )
    parser.add_argument(
        "--title",
        help='Title of the figure. DEFAULT: ""',
        type=str,
        required=False,
        default="",
    )
    parser.add_argument(
        "--x-label",
        help='X axis label of the figure. DEFAULT: ""',
        type=str,
        required=False,
        default="",
    )
    parser.add_argument(
        "--y-label",
        help='Y axis label of the figure. DEFAULT: ""',
        type=str,
        required=False,
        default="",
    )
    parser.add_argument(
        "--stylesheet",
        help='Filepath of matplotlib stylesheet to use. DEFAULT: ""',
        type=str,
        required=False,
        default="",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Display version of the tool",
        action="version",
        version=f"{versionName}: {version()} ",
    )

    return parser.parse_args()
