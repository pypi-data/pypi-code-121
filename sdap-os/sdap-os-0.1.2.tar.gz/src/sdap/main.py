import argparse
import os
import json
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from datetime import datetime, date

from sdap.data_access import CollectionLoader
from sdap.operators import get_operator
from sdap.utils import json_serial
from sdap.utils import get_log

logger = get_log(__name__)


def create_parser():
    parser = argparse.ArgumentParser()
    cwd = os.path.dirname(__file__)
    conf_rel_path = './test/data_access/collection-config.yaml'
    parser.add_argument("--conf", required=False, default=os.path.join(cwd, conf_rel_path))
    parser.add_argument("--secrets", required=False, default=None)
    parser.add_argument("--collection", required=False, default="hls")
    parser.add_argument("--bbox", required=False, nargs=4, type=float, default=[42.303, -71.272, 43.316, -71.183])
    parser.add_argument("--crs", required=False, type=str, default='EPSG:4326')
    parser.add_argument("--time-range", required=False, nargs=2, type=str,
                        default=['2017-01-01T00:00:00.000000+00:00', '2017-04-01T00:00:00.000000+00:00'])

    parser.add_argument("--operator-name", required=False, default="SpatialMean")
    parser.add_argument("--operator-args", type=str, required=False, default=None,
                        help="arguments used to initialize the operator, "
                             "repeat option for each argument")
    parser.add_argument("--plot", action='store_true', help='plot result (only supported for EVI operator)')
    return parser


def extend_range(range, margin):
    """
    :param range: bounds of the range
    :param margin: in proportion of the range, for example 0.1
    :return: extended range by the margin
    """
    actual_margin = (range[1] - range[0]) * margin
    return [range[0] - actual_margin, range[1] + actual_margin]


def plot_map(xas, lon_range, lat_range, margin):
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())

    # background
    ax.add_wmts('https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi',
                'ASTER_GDEM_Greyscale_Shaded_Relief')

    # extent
    lon_range = extend_range(lon_range, margin)
    lat_range = extend_range(lat_range, margin)
    ax.set_extent(lon_range + lat_range, crs=ccrs.PlateCarree())

    # data
    color_map = ax.pcolormesh(xas.request_x, xas.request_y, xas.isel(time=0), alpha=0.5, transform=ccrs.PlateCarree())
    fig.colorbar(color_map, ax=ax)

    # graticule
    gl = ax.gridlines(linestyle=":", draw_labels=True)

    plt.show()


def main():
    parser = create_parser()
    args = parser.parse_args()

    collection_loader = CollectionLoader(args.conf, secret_file=args.secrets)
    driver = collection_loader.get_driver(args.collection)

    time_range = [datetime.fromisoformat(t) for t in args.time_range]

    operator = get_operator(args.operator_name, args.operator_args)
    result = driver.get_all(args.bbox,
                            time_range,
                            operator,
                            crs=args.crs)
    result_str = json.dumps(result.to_dict(), default=json_serial)
    print(result_str)
    if args.plot:
        plot_map(result, args.x_range, args.y_range, 0.2)


if __name__ == '__main__':
    main()
