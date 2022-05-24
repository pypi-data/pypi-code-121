import csv


def get_device_name(file_name, sys_obj_id, delimiter=":"):
    """Get device name by its SNMP sysObjectID property from the file map.

    :param str file_name:
    :param str sys_obj_id:
    :param str delimiter:
    :rtype: str
    """
    try:
        with open(file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=delimiter)
            for row in csv_reader:
                if len(row) >= 2 and row[0] == sys_obj_id:
                    return row[1]
    except OSError:
        pass  # file does not exist

    return sys_obj_id
