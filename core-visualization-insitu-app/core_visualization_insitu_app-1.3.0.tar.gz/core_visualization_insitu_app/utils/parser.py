"""Visualization Insitu parser utils"""

import csv
from os import path, remove


def parse_cell(value):
    """Return the parsed value to insert it within the insitu_data table.

    Args:
        value:

    Returns:

    """
    if value:
        dict_value = str(value)
    else:
        dict_value = ""

    value = ""
    dict_value.split(",")

    for elt in dict_value:
        if not elt == ",":
            value += elt

    return value


def get_data_table_csv(data_table_list):
    """Convert a two dimensional list to a CSV table

    Args:
        data_table_list: two dimensional list

    Returns: CSV file

    """
    # Check if file already exists
    if path.isfile("./table.csv"):
        remove("./table.csv")

    # Write first line
    data_table_list.insert(
        0, ["Project", "Build", "Part", "Data Name", "Tab Number", "Total Layers"]
    )

    # Create table
    with open("table" + ".csv", "w") as table:
        file_writer = csv.writer(
            table, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        for row in data_table_list:
            file_writer.writerow(row)
        table.close()
    with open("table" + ".csv", "r") as table:
        csv_table = table.read()
        table.close()

    return csv_table
