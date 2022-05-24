#!/usr/bin/env python3

import argparse
import logging
from bioblu.ds_manage import img_cutting

if __name__ == "__main__":
    loglevel = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    logging.disable()

    p = argparse.ArgumentParser()
    p.add_argument('-s', '--img-source', dest='fdir')
    p.add_argument('-th', '--horz_tile_count', dest='horz_n', default=3, type=int)
    p.add_argument('-tv', '--vert_tile_count', dest='vert_n', default=2, type=int)
    p.add_argument('-a', '--altitude_m', dest='altitude', type=int)
    p.add_argument('-l', '--location', dest='location', default='no_location', type=str)
    p.add_argument('--save-tiles', dest='save_tiles', action='store_true', default=False)
    p.add_argument('--save-csv', dest='save_csv', action='store_true', default=False)
    p.add_argument('-o', '--output-dir', dest='target_dir', default=None)
    p.add_argument('--no-gps', dest='gps', action='store_false', default=True)
    args = p.parse_args()

    img_cutting.create_tiles(img_dir=args.fdir,
                             horizontal_tile_count=args.horz_n,
                             vertical_tile_count=args.vert_n,
                             altitude_m=args.altitude,
                             save_tiles_csv=args.save_csv,
                             save_tile_images=args.save_tiles,
                             target_dir=args.target_dir,
                             location=args.location,
                             use_gps=args.gps)

# Example:
# python3 create_tiles.py -s /home/user/img_dir -th 3 -tv 2 -a 5 --save-tiles --save-csv --location "testbeach"
# python3 create_tiles.py -s /home/findux/Desktop/nonsquare_test/output/ -th 3 -tv 2 -a 7 --save-tiles --save-csv --location "Ramla" --no-gps
# python3 create_tiles.py -s /media/findux/DATA/Documents/Malta_II/surveys/Messina/DJI/frames/ -th 3 -tv 2 -a 7 --save-tiles --save-csv --location "Ramla" --no-gps
# python3 create_tiles.py -s /media/findux/DATA/Documents/Malta_II/surveys/2022-05-03_Ramla/DJI_0153-003_48_frame_interval/ -th 3 -tv 2 -a 7 --save-tiles --save-csv --location "Ramla" --no-gps