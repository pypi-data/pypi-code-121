import re


def search_one(text,patten):
    match =  re.search(text,patten)
    if match:
        return match[0]
    else:
        return ""