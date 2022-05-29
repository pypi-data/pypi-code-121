
def latlng_to_xy(latlng):
    lat, lng = latlng
    return [lng, lat]


def xy_to_latlng(xy):
    x, y = xy
    return [y, x]


def get_bbox(xy_list):
    max_x, max_y = min_x, min_y = xy_list[0]
    for [x, y] in xy_list[1:]:
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    x_span = max_x - min_x
    y_span = max_y - min_y

    return [
        [min_x, min_y],
        [max_x, max_y],
        [x_span, y_span],
    ]


def get_func_transform(width, height, padding, xy_list):
    [
        [min_x, min_y],
        [max_x, max_y],
        [x_span, y_span],
    ] = get_bbox(xy_list)

    padded_width, padded_height = width - padding * 2, height - padding * 2
    r = (x_span / padded_width) / (y_span / padded_height)
    if r > 1:
        padded_height /= r
    else:
        padded_width *= r

    padding_width = (width - padded_width) / 2
    padding_height = (height - padded_height) / 2

    def func_transform(xy):
        [x, y] = xy
        px = (x - min_x) / x_span
        py = (y - min_y) / y_span

        x = (px) * padded_width + padding_width
        y = (1 - py) * padded_height + padding_height
        return [x, y]

    return func_transform
