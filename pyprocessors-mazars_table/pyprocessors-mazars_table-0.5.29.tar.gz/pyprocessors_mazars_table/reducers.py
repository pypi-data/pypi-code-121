from itertools import combinations
from typing import List

import pendulum
from thefuzz import fuzz


def NoReducer(texts: List[str]) -> List[str]:
    return texts


def Deduplicate(items: List[str]) -> List[str]:
    # strict duplicate
    return list(set(items))


def MostRecent(items: List[str]) -> List[str]:
    # if many dates keep the most recent
    if items:
        dates = {}
        not_dates = []
        for item in items:
            try:
                dt = pendulum.from_format(item, "DD/MM/YYYY")
                dates[item] = dt
            except BaseException:
                not_dates.append(item)
        if dates:
            sorted_dates = sorted(dates.items(), key=lambda item: item[1], reverse=True)
            return [sorted_dates[0][0]]
        else:
            return not_dates
    return items


def GreaterThan30(items: List[str]) -> List[str]:
    # more than 30 days
    items2 = []
    if items:
        for item in items:
            if item.endswith(" jours"):
                duration = item[0: -len(" jours")]
                if duration.isdigit() and int(duration) >= 30:
                    items2.append(item)
            else:
                items2.append(item)
    return items2


def FuzzyDeduplicate(items: List[str]) -> List[str]:
    sorted_items = list(sorted(items, key=len, reverse=True))
    while True:
        filteredOne = False
        for s, t in combinations(sorted_items, 2):
            # remove partial items
            if t.lower() in s.lower():
                sorted_items.remove(t)
                filteredOne = True
                break
            # remove fuzzy items
            ratio = fuzz.ratio(s.lower(), t.lower())
            if ratio > 80:
                sorted_items.remove(t)
                filteredOne = True
                break
        if not filteredOne:
            break
    return sorted_items
