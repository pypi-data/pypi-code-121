from argparse import Namespace

import pandas
from pandas import DataFrame

from clime_bus_factor.args import busFactorArgs


def buildBusFactor(
    df: DataFrame, *, bin: int, alpha: float = 0.0, stor: str = "busFactor"
) -> DataFrame:
    day_key = "author_days_since_0"
    lastday = df[day_key].max() + bin
    bins = list(range(0, lastday, bin))

    df["commitBin"] = pandas.cut(df[day_key], bins=bins, include_lowest=True)
    bins = df["commitBin"].unique().tolist()

    data = []
    for bin in bins:

        item = {"days_since_0": int(bin.left) if bin.left > 0 else 0}

        if alpha > 0:
            temp = df[df["commitBin"] == bin]
            abs_list = lambda l: [abs(item) for item in l]
            significance = alpha * sum(abs_list(temp["dkloc"].tolist()))

            bf = 0
            authors = set(temp["author_email"].tolist())
            for author in authors:
                author_dloc = sum(
                    abs_list(temp[temp["author_email"] == author]["dkloc"].tolist())
                )
                if author_dloc > significance:
                    bf += 1

            temp = temp[temp["dkloc"] > significance]

            item[stor] = bf
        else:
            item[stor] = len(df[df["commitBin"] == bin]["author_email"].unique())

        data.append(item)

    return DataFrame(data)


def main() -> None:
    args: Namespace = busFactorArgs()

    if args.bin < 1:
        print(f"Bin arguement must be an integer greater than 0: {args.bin}")
        quit(1)
    if args.alpha > 1:
        print("Invalid alpha value. Must be alpha =< 1 and alpha >= 0")
        quit(2)
    if args.alpha < 0:
        print("Invalid alpha value. Must be alpha =< 1 and alpha >= 0")
        quit(3)

    df: DataFrame = pandas.read_json(args.input).T
    bf: DataFrame = buildBusFactor(df, bin=args.bin, alpha=args.alpha, stor="busFactor")
    cd: DataFrame = buildBusFactor(df, bin=args.bin, alpha=0, stor="developerCount")

    cdColumn = cd["developerCount"]
    bf.join(cdColumn).to_json(args.output, indent=4)


if __name__ == "__main__":
    main()
