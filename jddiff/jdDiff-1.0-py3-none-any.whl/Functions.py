from PyQt6.QtWidgets import QComboBox, QTreeWidgetItem
from typing import Any
import traceback
import hashlib
import json
import sys
import os
import re


def get_sha512_hash(path: str) -> str:
    """Calculate the SHA-512 checksum of a file
    Source: https://stackoverflow.com/questions/22058048/hashing-a-file-in-python"""
    BUF_SIZE = 65536
    sha512 = hashlib.sha512()
    with open(path, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha512.update(data)
    return sha512.hexdigest()


def select_combo_box_data(box: QComboBox, data: Any, default_index: int = 0) -> None:
    """Set the index to the item with the given data"""
    index = box.findData(data)
    if index == -1:
        box.setCurrentIndex(default_index)
    else:
        box.setCurrentIndex(index)


def natural_sort(sort_list: list[str]) -> list[str]:
    """Sorts a list naturally. Source: https://stackoverflow.com/questions/11150239/natural-sorting"""
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(sort_list, key=alphanum_key)


def sort_tree_widget_item_child(item: QTreeWidgetItem, method: str) -> None:
    """Sorts the Children of a QTreeWidgetItem,"""
    name_list = []
    item_dict = {}

    while item.childCount() != 0:
        child = item.takeChild(0)
        name_list.append(child.text(0))
        item_dict[child.text(0)] = child

    if method == "alphabeticallyAscending":
        name_list.sort()
    elif method == "alphabeticallyDescending":
        name_list.sort()
        name_list.reverse()
    elif method == "naturalAscending":
        name_list = natural_sort(name_list)
    elif method == "naturalDescending":
        name_list = natural_sort(name_list)
        name_list.reverse()

    for i in name_list:
        item.addChild(item_dict[i])


def read_json_file(path: str, default: Any) -> Any:
    """Tries to read a JSOn file"""
    if not os.path.isfile(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        print(traceback.format_exc(), end="", file=sys.stderr)


def remove_list_duplicates(old_list: list[Any]) -> list[Any]:
    """Removes all duplicates from a list"""
    new_list = []

    for i in old_list:
        if i not in new_list:
            new_list.append(i)

    return new_list
