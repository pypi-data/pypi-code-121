import re


def parse_decimal_details(details):
    """
    Parse Spark's DecimalType JSON representation for precision and scale.

    :param details: DecimalType JSON representation e.g. "decimal(5,3)" has precision 5 and scale 3.
    """
    match = re.search("^decimal\((\d+),(\d+)\)$", details)
    if match is None:
        raise Exception(f"Malformed decimal data type details {details}")

    return int(match.group(1)), int(match.group(2))
