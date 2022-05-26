from datetime import datetime,date
from enum import Enum, unique
from difflib import Differ
import re
from fuzzywuzzy import fuzz
from termcolor import colored

# This function used to check a list's continuity of date. The list must have two columns as start date and end date.
# The fromat must be "yyyy-mm-dd" or "yyy-mm".  The list has to be from most recent to past. You can force sort it by assign sort =True
# The output will be True or False, plus sorted input list and message.
def checkContinuity(data_set: list, sort=False):
    if sort:
        data_set = sorted(data_set, key=lambda x: (x[0], x[1]), reverse=True)
    ok = []
    errors = []

    def difference(l1, l2):
        if type(l1)==date: l1=l1.strftime("%Y-%m-%d")
        if type(l2)==date: l2=l2.strftime("%Y-%m-%d")

        if l2==None or l2=="Present":
            l2=datetime.today().strftime("%Y-%m-%d") if bool(re.search(r"^\d{4}-\d{2}-\d{2}", l1)) else datetime.today().strftime("%Y-%m")
        if bool(re.search(r"^\d{4}-\d{2}-\d{2}", l1)) and bool(
            re.search(r"^\d{4}-\d{2}-\d{2}", l2)
        ):
            current_start = datetime.strptime(l1, "%Y-%m-%d")
            previous_end = datetime.strptime(l2, "%Y-%m-%d") 
            return (current_start - previous_end).days, "day(s)"
        if bool(re.search(r"^\d{4}-\d{2}", l1)) and bool(
            re.search(r"^\d{4}-\d{2}", l2)
        ):
            y1, m1 = l1.split("-")
            y2, m2 = l2.split("-")
            return (int(y1) - int(y2)) * 12 + int(m1) - int(m2), "month(s)"

    for i in range(len(data_set) - 1):
        diff, unit = difference(data_set[i][0], data_set[i + 1][1])
        if diff > 1:
            ok.append(False)
            errors.append(
                f"{'List sorted. ' if sort else ''}The date is not continious between line {i+1} to {i+2} (missed {diff-1} {unit})"
            )
        elif diff < 0:
            ok.append(False)
            errors.append(
                f"{'List sorted. ' if sort else ''}The date is not continious between line {i+1} to {i+2} (overlapped {diff} {unit})"
            )
        else:
            ok.append(True)
    if all(ok):
        return True, data_set, "date is continious"
    else:
        return False, data_set, errors


#  Used to find different between two text strings. Initialize with tc=TextChanged(t1,t2), and get differences by tc.text_added or tc.text_deleted
class TextChanged:
    def __init__(self, text1, text2):
        self.text1 = text1
        self.text2 = text2

    def __get_changed(self):

        t1_lines = self.text1.splitlines()
        t2_lines = self.text2.splitlines()

        diff = Differ().compare(t1_lines, t2_lines)
        changed = list(diff)

        added = r"^\+\s(.+)"
        deleted = r"^\-\s(.+)"
        text_added = [
            d[2:] for d in changed if re.findall(added, d)
        ]  # d[2:] delete '+ ' at the begining
        text_added = "\n".join(text_added)
        text_deleted = [d[2:] for d in changed if re.findall(deleted, d)]
        text_deleted = "\n".join(text_deleted)

        return {"text_added": text_added, "text_deleted": text_deleted}

    @property
    def text_added(self):
        return self.__get_changed()["text_added"]

    @property
    def text_deleted(self):
        return self.__get_changed()["text_deleted"]


def best_match(term, list_names, min_score=0):
    max_score = -1
    max_name = ""
    for term2 in list_names:
        score = fuzz.ratio(term, term2)
        if (score > min_score) and (score > max_score):
            max_name = term2
            max_score = score
    return max_name


Month = Enum(
    "Month",
    (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ),
)


@unique
class Sex(Enum):
    Female = 0
    Male = 1


# input list and outpout markdown table text
def markdown_table(ds: list):
    head = ds[0]
    head_str = "|"
    head_sep = "|"
    for col in range(0, len(ds[0])):
        head_str += str(head[col]) + "|"
        head_sep += "------------- " + "|"
    # print(head_str)
    # print(head_sep)
    output = head_str + "\n" + head_sep + "\n"

    row_data = "|"
    for row in range(1, len(ds)):
        for col in range(0, len(ds[0])):
            row_data += str(ds[row][col]) + "|"
        # print(row_data)
        output += row_data + "\n"
        row_data = "|"

    return output


# Some common input functions
def multi_line_input():
    print("Ctrl-D  to save it.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    return "\n".join(contents)
