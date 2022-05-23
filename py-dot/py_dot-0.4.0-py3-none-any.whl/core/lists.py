from typing import List


def safe_insert(target: List, index, value, fill=None):
    size = len(target)

    if size > index:
        target[index] = value
    else:
        while size != index:
            target.append(fill)
            size += 1

        target.insert(index, value)

    return target
