def device_id_generator():
    """
    Generate ID for unnamed device.

    :return: string
    """
    i = 0
    while True:
        yield "Device_{}".format(i)
        i += 1


def token_generator():
    """
    Generate Token number up to 2**8.

    This token is used for client server communication.

    :return: int
    """
    token, max_token = 1, pow(2, 8)
    while True:
        yield token
        token += 1
        if token >= max_token:
            token = 1


def axis_name_generator(range_of_axis=1):
    """
    Axis name generator for n axis scan.

    :param range_of_axis:
    :type range_of_axis: int
    """
    current = 1
    names = ["Slow", "Slower", "Slowest", "Fast", "Faster", "Fastest"]
    mapping = [
        [3],
        [0, 3],
        [1, 0, 3],
        [1, 0, 3, 4],
        [2, 1, 0, 3, 4],
        [2, 1, 0, 3, 4, 5],
    ]
    col = range_of_axis - 1

    while current <= range_of_axis:
        if range_of_axis <= 6:
            yield "{}".format(names[mapping[col][current - 1]])
        elif current == range_of_axis:
            yield "Fast {}".format(current)
        elif current == 1:
            yield "Slow {}".format(current)
        else:
            yield "{}".format(current)
        current += 1
