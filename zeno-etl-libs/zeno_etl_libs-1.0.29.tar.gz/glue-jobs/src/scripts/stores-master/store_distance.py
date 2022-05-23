#!/usr/bin/env python
# coding: utf-8
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper import helper
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.config.common import Config
from zeno_etl_libs.helper.email.email import Email

import argparse
import pandas as pd
import datetime
import numpy as np
import math
import simplejson, urllib.request
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False)
parser.add_argument('-et', '--email_to', default="saurav.maskar@zeno.health", type=str,
                    required=False)
args, unknown = parser.parse_known_args()
env = args.env
os.environ['env'] = env

email_to = args.email_to

logger = get_logger()

logger.info(f"env: {env}")

start_time = datetime.now()

rs_db = DB()

rs_db.open_connection()

s3 = S3()

# Start
logger.info('Script Manager Initialized')

# =============================================================================
# Fetching store in clusters
# =============================================================================

store_clusters_query = f'''
    select
	sf."store-id",
	sc."cluster-id"
from
	"prod2-generico".features f
join "prod2-generico"."store-features" sf on
	f.id = sf."feature-id"
join "prod2-generico"."store-clusters" sc on
	sc."store-id" = sf."store-id"
where
	sf."feature-id" = 69
	and sf."is-active" = 1
	and sc."is-active" = 1
    '''

store_clusters = rs_db.get_df(store_clusters_query)

if isinstance(store_clusters, type(None)):
    store_clusters = pd.DataFrame(columns=['store-id', 'cluster-id'])

logger.info("")
logger.info("Fetched Store Clusters")

str_info_cross = pd.DataFrame()

for cluster in store_clusters['cluster-id'].unique():
    temp = store_clusters[store_clusters['cluster-id'] == cluster]

    cluster_stores = tuple(map(int, list(temp['store-id'].unique())))

    strs = """
    select
        id as "store-id",
        name as "store-name",
        lat ,
        lon
    from
        "prod2-generico".stores
    where
        id in {}
        """.format(cluster_stores)

    str_info = rs_db.get_df(strs)

    str_info['key'] = 0

    str_info_cross_cluster = str_info.merge(str_info, on='key', how='outer', suffixes=('-x', '-y'))

    str_info_cross_cluster = str_info_cross_cluster[(str_info_cross_cluster['store-id-x'] !=
                                                     str_info_cross_cluster['store-id-y'])]

    del str_info_cross_cluster['key']

    str_info_cross = str_info_cross.append(str_info_cross_cluster, ignore_index=True)

    if isinstance(str_info_cross, type(None)):
        str_info_cross = pd.DataFrame(columns=['store-id-x', 'store-name-x', 'lat-x', 'lon-x', 'store-id-y',
                                               'store-name-y', 'lat-y', 'lon-y'])

logger.info("")
logger.info("Created Store Mapping in Cluster")

# =============================================================================
# Checking If New Stores are added or not
# Distance calculation will only run if there is change in cluster stores
# =============================================================================

strs2 = """
select
sd."store-id-x" as "store-id-x-in-dss",
sd."store-id-y" as "store-id-y-in-dss"
from
"prod2-generico"."store-distance" sd
"""

str_info_in_DSS = rs_db.get_df(strs2)

if isinstance(str_info_in_DSS, type(None)):
    str_info_in_DSS = pd.DataFrame(columns=['store-id-x-in-dss', 'store-id-y-in-dss'])

check_if_change_in_cluster_store = str_info_cross.merge(str_info_in_DSS, left_on=['store-id-x', 'store-id-y'],
                                                        right_on=['store-id-x-in-dss', 'store-id-y-in-dss'], how='left')

differece = len(check_if_change_in_cluster_store[check_if_change_in_cluster_store['store-id-x-in-dss'].isna()])

logger.info("")
logger.info("Changes in store clusters - {}".format(differece))

if differece == 0:
    logger.info("")
    logger.info("No Changes in Cluster stores So not running GMAPS API part to fetch distance")
    status2 = True
    table_status = 'Unchanged'
    api_status = 'No hit'
else:
    logger.info("")
    logger.info("Changes in Cluster stores So running GMAPS API part to fetch distance")
    table_status = 'Updated'
    api_status = 'hit'

    # =========================================================================
    # Calculating Distance in air
    # =========================================================================

    def distance_cal(a, b, c, d):
        R = 6373.0

        lat1 = math.radians(a)
        lon1 = math.radians(b)
        lat2 = math.radians(c)
        lon2 = math.radians(d)

        dlon = lon2 - lon1

        dlat = lat2 - lat1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        distance = distance * 1000  # To convert in meters

        distance = round(distance, 0)

        distance = int(distance)
        return distance


    str_info_cross['lat-x'] = str_info_cross['lat-x'].astype('float')
    str_info_cross['lon-x'] = str_info_cross['lon-x'].astype('float')
    str_info_cross['lat-y'] = str_info_cross['lat-y'].astype('float')
    str_info_cross['lon-y'] = str_info_cross['lon-y'].astype('float')

    str_info_cross['distance-in-air'] = np.vectorize(distance_cal)(str_info_cross['lat-x'], str_info_cross['lon-x'],
                                                                   str_info_cross['lat-y'], str_info_cross['lon-y'])

    logger.info('')
    logger.info('Calculated Distance in Air')

    # =========================================================================
    # Calculating Distance on road
    # =========================================================================
    str_info_cross['lat-x'] = str_info_cross['lat-x'].astype('str')
    str_info_cross['lon-x'] = str_info_cross['lon-x'].astype('str')
    str_info_cross['lat-y'] = str_info_cross['lat-y'].astype('str')
    str_info_cross['lon-y'] = str_info_cross['lon-y'].astype('str')

    str_info_cross['lat-lon-x'] = str_info_cross[['lat-x', 'lon-x']].apply(lambda x: ','.join(x[x.notnull()]), axis=1)
    str_info_cross['lat-lon-y'] = str_info_cross[['lat-y', 'lon-y']].apply(lambda x: ','.join(x[x.notnull()]), axis=1)

    configobj = Config.get_instance()
    secrets = configobj.get_secrets()
    api_key = secrets['GMAPS_API_KEY']
    gmaps_op = pd.DataFrame()
    distance_matrix = pd.DataFrame()

    for index, row in str_info_cross.iterrows():
        # logger.info (index)

        lat_lon_x = row['lat-lon-x']
        lat_lon_y = row['lat-lon-y']

        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false&key={2}".format(
            str(lat_lon_x), str(lat_lon_y), api_key)

        result = simplejson.load(urllib.request.urlopen(url))
        distance = result["rows"][0]["elements"][0]["distance"]["value"]

        gmaps_op['store-id-x'] = row[0:1]
        gmaps_op['store-id-y'] = row['store-id-y']
        gmaps_op['distance'] = distance

        distance_matrix = distance_matrix.append([gmaps_op]).reset_index(drop=True)

    str_info_cross = pd.merge(left=str_info_cross, right=distance_matrix,
                              how='left', on=['store-id-x', 'store-id-y'])

    str_info_cross.rename(columns={'distance': 'distance-on-road'}, inplace=True)

    del str_info_cross['lat-lon-x']
    del str_info_cross['lat-lon-y']

    logger.info('')
    logger.info('Calculated Distance on road via GMAPS API')

    # str_info_cross['distance-on-road']=10

    str_info_cross['uploaded-at'] = datetime.datetime.now()

    # =========================================================================
    # Writing table in Redshift
    # =========================================================================
    schema = 'prod2-generico'
    table_name = 'store-distance'
    table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

    if isinstance(table_info, type(None)):
        logger.info('')
        logger.info(f"Table:{table_name} table does not exist - table uploaded")
        s3.write_df_to_db(df=str_info_cross[table_info['column_name']], table_name=table_name, db=rs_db,
                          schema=schema)
    else:
        logger.info('')
        logger.info(f"Table:{table_name} table exist")

        truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
        rs_db.execute(truncate_query)
        logger.info(f"Table:{table_name} table truncated")

        s3.write_df_to_db(df=str_info_cross[table_info['column_name']], table_name=table_name, db=rs_db,
                          schema=schema)
        logger.info(f"Table:{table_name} table uploaded")

if status2 is True:
    status = 'Success'
else:
    status = 'Failed'

end_time = datetime.now()
difference = end_time - start_time
min_to_complete = round(difference.total_seconds() / 60, 2)

email = Email()

email.send_email_file(subject='{} {} : store_distance table {} - GMAPS API - {}'.format(
                 env, status, table_status, api_status),
    mail_body=f" pso-stock-transfer-mapping table updated, Time for job completion - {min_to_complete} mins ",
    to_emails=email_to, file_uris=[])
rs_db.close_connection()
