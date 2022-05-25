import json

import pandas as pd
import os
import astropy.coordinates as coords
import astroplan

data_dir = os.path.dirname(__file__)

summer_fields_path = os.path.join(data_dir, "summer_fields.txt")
summer_fields = pd.read_csv(summer_fields_path, sep='\s+')

summer_filters = ["u", "g", "r", "i"]

camera_field_size = 0.26112 / 2

max_target_priority = 100.

program_db_host = 'jagati.caltech.edu'

too_schedule_config_path = os.path.join(data_dir, "observing_request_schema.json")

with open(too_schedule_config_path, "rb") as f:
    too_db_schedule_config = json.load(f)


def get_default_value(
        key: str
):
    return too_db_schedule_config["properties"][key]["default"]


# define location of Palomar Observatory
palomar_loc = coords.EarthLocation(lat=coords.Latitude('33d21m25.5s'),
                                   lon=coords.Longitude('-116d51m58.4s'),
                                   height=1696.)

palomar_observer = astroplan.Observer(location=palomar_loc)
