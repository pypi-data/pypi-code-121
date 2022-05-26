from argparse import Namespace

import pandas
from pandas import Categorical, DataFrame, Interval, Series

from clime_bus_factor.args import developerCountArgs


def buildBusFactor(df: DataFrame, bin: int) -> DataFrame:
    daysSince0: Series = df["author_days_since_0"].unique()

    data: list = []

    maxDays: int = daysSince0.max() + bin
    bins: list = [day for day in range(maxDays) if day % bin == 0]

    df["commitBin"] = pandas.cut(
        df["author_days_since_0"], bins=bins, include_lowest=True
    )

    bins: Categorical = df["commitBin"].unique()
    binList: list = bins.tolist()

    bin: Interval
    for bin in binList:
        temp: dict = {}

        day: int = int(bin.left) if bin.left > 0 else 0

        busFactor: int = len(df[df["commitBin"] == bin]["author_email"].unique())

        temp["days_since_0"] = day
        temp["busFactor"] = busFactor

        data.append(temp)

    return DataFrame(data)


def main() -> None:
    args: Namespace = developerCountArgs()

    if args.bin < 1:
        print(f"Bin arguement must be an integer greater than 0: {args.bin}")
        quit(1)

    df: DataFrame = pandas.read_json(args.input).T
    buildBusFactor(df, bin=args.bin).to_json(args.output, indent=4)


if __name__ == "__main__":
    main()
