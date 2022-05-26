from argparse import Namespace

import matplotlib.pyplot as plt
import pandas
from pandas import DataFrame

from clime_bus_factor.args import graphArgs
from clime_bus_factor.version import version


def plot(
    x: list,
    y: list,
    type: str,
    title: str,
    xLabel: str,
    yLabel: str,
    output: str,
    stylesheet: str,
) -> None:
    "param: type can only be one of the following: line, bar"

    if stylesheet != "":
        plt.style.use(stylesheet)

    if type == "line":
        plt.plot(x, y)
    elif type == "bar":
        plt.bar(x, height=y)
    else:
        print(f"Invalid plot type: {type}. Can only be one of the following: line, bar")

    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)

    plt.savefig(output)


def main() -> None:
    args: Namespace = graphArgs()

    df: DataFrame = pandas.read_json(args.input)

    data: list = []
    data.append(df["days_since_0"].to_dict().keys())
    data.append(df[args.y_data].tolist())

    plot(
        x=data[0],
        y=data[1],
        type=args.type,
        title=args.title,
        xLabel=args.x_label,
        yLabel=args.y_label,
        output=args.output,
        stylesheet=args.stylesheet,
    )


if __name__ == "__main__":
    main()
