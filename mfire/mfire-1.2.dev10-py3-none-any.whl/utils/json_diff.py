"""function made to check the differences between two given json files
    and highlighting the differences if needed.
"""

import argparse
import sys
import json
from typing import Any


class Log:
    """Log management
    """

    def __init__(self, header: str, verbose: int = 2) -> None:
        self.header = f"{header}\t: " if header else ""
        self.verbose = verbose
        self.channel = None
        if verbose:
            self.channel = sys.stdout if verbose == 1 else sys.stderr

    def __call__(self, msg: str = "") -> Any:
        full_msg = f"{self.header}{msg}"
        if self.verbose:
            print(full_msg, file=self.channel)


class FormatDict(dict):
    """FormatDict: dictionnary extension for handling string formatting
    with missing keys.
    """

    def __missing__(self, key):
        return "{" + key + "}"


def dict_diff(
    left: Any, right: Any, index_list: str = "", verbose: int = 2, **kwargs,
) -> bool:
    """Recursive function made to check the difference between two given values
    and to highlight the differences.

    Args:
        left (Any): Value 1
        right (Any): Value 2
        index_list (str, optional): Inde. Defaults to "".
        verbose (int, optional): Level of description of the differences..
            Defaults to 2.

    Returns:
        bool: True if left and right are equal, else False
    """
    log = Log(header=index_list, verbose=verbose)
    if not isinstance(left, type(right)):
        log(f"type mismatch ('{type(left)}' | '{type(right)}')")
        return False

    if isinstance(left, dict):
        keysl = set(left)
        keysr = set(right)
        results = []
        if keysl - keysr:
            log(f"missing keys in right dict {keysl - keysr}")
            results += [False]
        if keysr - keysl:
            log(f"missing keys in left dict {keysr - keysl}")
            results += [False]
        for key in keysl & keysr:
            results += [
                dict_diff(
                    left=left[key],
                    right=right[key],
                    index_list=index_list + f"['{key}']",
                    verbose=verbose,
                    **kwargs,
                )
            ]
        return all(results)

    if isinstance(left, list):
        len_left = len(left)
        len_right = len(right)
        if len_left != len_right:
            log(f"lengths of iterables don't match ({len_left} | {len_right})")
            return False

        if len_left > 0 and all([isinstance(d, dict) for d in left]):
            sorting_key = next(
                (key for key in ("hazard", "level") if key in left[0]), None
            )
            if sorting_key is not None:
                sorted_left = sorted(left, key=lambda d: d[sorting_key])
                sorted_right = sorted(right, key=lambda d: d[sorting_key])
                return all(
                    [
                        dict_diff(
                            left=sorted_left[i],
                            right=sorted_right[i],
                            index_list=index_list
                            + f"[{sorting_key}={sorted_left[i][sorting_key]}]",
                            verbose=verbose,
                            **kwargs,
                        )
                        for i in range(len_left)
                    ]
                )

        return all(
            [
                dict_diff(
                    left=left[i],
                    right=right[i],
                    index_list=index_list + f"[{i}]",
                    verbose=verbose,
                    **kwargs,
                )
                for i in range(len_left)
            ]
        )

    if isinstance(left, str):
        if left == right:
            return True
        if kwargs is None:
            log(f"str values don't match ('{left}' | '{right}')")
            return False
        format_kwargs = FormatDict(kwargs)
        formatted_left = left.format_map(format_kwargs)
        formatted_right = right.format_map(format_kwargs)
        if formatted_left != formatted_right:
            log(
                "formatted str values don't match "
                f"('{formatted_left}' | '{formatted_right}')"
            )
            return False
        return True

    if left != right:
        log(f"values don't match ('{left}' | '{right}')")
        return False

    return True


def json_diff(left: str, right: str, verbose: int = 2, **kwargs) -> bool:
    """function made to check the differences between two given json files
    and highlighting the differences if needed.

    Args:
        left (str): Path to a json file
        right (str): Path to a json file
        verbose (int, optional): Level of description of the differences.
            Defaults to 2.

    Returns:
        bool: [description]
    """
    with open(left) as lfp:
        left_dico = json.load(lfp)

    with open(right) as rfp:
        right_dico = json.load(rfp)

    return dict_diff(
        left=left_dico, right=right_dico, index_list="", verbose=verbose, **kwargs,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("left")
    parser.add_argument("right")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    args = parser.parse_args()
    print(args)
    print()
    result = json_diff(left=args.left, right=args.right, verbose=args.verbose)
    print(f"Given files identical : {result}")
    sys.exit(not result)
