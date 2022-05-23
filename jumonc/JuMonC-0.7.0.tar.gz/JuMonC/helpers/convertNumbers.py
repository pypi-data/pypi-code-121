import logging

from typing import Union, Tuple


logger = logging.getLogger(__name__)



_conversion_binary_dict = {
2**50: "Pi",
2**40: "Ti",
2**30: "Gi",
2**20: "Mi",
2**10: "Ki",
}



def convertBinaryPrefix(value: Union[int, float], decimalDigits: int = 2) -> Tuple[str, str]:
    for (key, unitPrefix) in _conversion_binary_dict.items():
        if value >= 10*key:
            value = value/key
            return (("{:." + str(decimalDigits) + "f}").format(value), unitPrefix)
    if isinstance(value, int):
        return (str(value), "")
    return (("{:." + str(decimalDigits) + "f}").format(value), "")