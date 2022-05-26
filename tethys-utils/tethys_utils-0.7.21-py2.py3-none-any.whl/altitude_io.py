"""
Functions to query APIs for altitude data.

"""
import requests
import pandas as pd
import numpy as np
from tethysts import Tethys
from shapely.geometry import mapping
from shapely import wkb

######################################
#### Parameters

koordinates_rater_format = '{base_url}/services/query/v1/raster.json?key={key}&layer={layer_id}&x={lon}&y={lat}'

dem_remote = {'bucket': 'nasa-data', 'connection_config': 'https://b2.tethys-ts.xyz', 'version': 2}
dem_ds_id = '4690821a39b3fb65c197a540'

#####################################
### Functions


def koordinates_raster_query(base_url: str, key: str, layer_id: (int, str), lon: float, lat: float):
    """

    """
    url_request = koordinates_rater_format.format(base_url=base_url, key=key, layer_id=layer_id, lon=lon, lat=lat)
    resp = requests.get(url_request)

    if resp.ok:
        layer1 = resp.json()['rasterQuery']['layers'][str(layer_id)]

        status = layer1['status']

        if status == 'ok':
            bands = layer1['bands']

            return bands
        else:
            print('status is: ' + status)
            return None

    else:
        return resp.content.decode()


def get_altitude(stn_df, dem_remote=dem_remote, dem_ds_id=dem_ds_id, source_ds_id=None, source_remote=None):
    """

    """
    stn_df1 = stn_df[['station_id', 'geometry']].drop_duplicates(subset=['station_id']).copy()

    ## Get existing stns
    if isinstance(source_remote, dict) and isinstance(source_ds_id, str):
        try:
            t1 = Tethys([source_remote])
            old_stns = t1.get_stations(source_ds_id)
        except:
            old_stns = []
    else:
        old_stns = []

    ## Combine new stations with existing stations
    if old_stns:
        old_stns_alt = [{'station_id': s['station_id'], 'altitude': s['altitude']} for s in old_stns if 'altitude' in s]
        if old_stns_alt:
            old_stns_df = pd.DataFrame(old_stns_alt)
            combo1 = pd.merge(stn_df1, old_stns_df, how='left', on='station_id')
        else:
            combo1 = stn_df1.copy()
            combo1['altitude'] = np.nan
    else:
        combo1 = stn_df1.copy()
        combo1['altitude'] = np.nan

    ## Iterate through stations for altitude
    t1 = Tethys([dem_remote])

    alt_list = []
    for i, row in combo1.iterrows():
        # print(i)
        if np.isnan(row['altitude']):
            geo1 = mapping(wkb.loads(row['geometry'], True))
            results = t1.get_results(dem_ds_id, lon=float(geo1['coordinates'][0]), lat=float(geo1['coordinates'][1]), squeeze_dims=True, output='DataArray', cache='memory')
            alt = int(results)
        else:
            alt = int(row['altitude'])

        alt_list.append({'station_id': row['station_id'], 'altitude': alt})

    ## Package up and return
    alt_df = pd.DataFrame(alt_list)

    return alt_df


####################################
### Testing

# base_url = 'https://data.linz.govt.nz'
# key = ''
# layer_id = 51768
# lon = 172.084790
# lat = -43.222752
#
#
#
# bands1 = koordinates_raster_query(base_url, key, layer_id, lon, lat)
