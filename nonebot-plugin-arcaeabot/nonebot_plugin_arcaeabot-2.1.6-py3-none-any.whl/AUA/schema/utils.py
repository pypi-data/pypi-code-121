def diffstr2num(diff: str):
    diff_dict = {
        "PAST": 0,
        "PST": 0,
        "PRESENT": 1,
        "PRS": 1,
        "FUTURE": 2,
        "FTR": 2,
        "BEYOND": 3,
        "BYD": 3,
        "ALL": -1,
    }
    return diff_dict.get(diff, None)
