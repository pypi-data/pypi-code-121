import argparse
import sys
import os
sys.path.append('../../../..')

from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.db.db import DB
from zeno_etl_libs.helper.aws.s3 import S3
from zeno_etl_libs.helper import helper
import pandas as pd
import numpy as np
import datetime
from dateutil.tz import gettz


def main(rs_db, s3):
    schema = 'prod2-generico'
    table_name = 'ecomm-pso-substitution'
    table_info = helper.get_table_info(db=rs_db, table_name=table_name, schema=schema)

    # ethical generic leads
    base_q = """
        select
            e."zeno-order-id",
            e."patient-id" ,
            e."order-type" ,
            e."zeno-created-at" ,
            e."zeno-drug-created-by" ,
            e."order-number" ,
            e."preferred-store-id" ,
            e."type",
            e.category ,
            e."composition-master-id",
            e.composition ,
            e.status,
            e."zeno-drug-id",
            e."zeno-drug-name"
        from
            "prod2-generico".ecomm e
        where
            date(e."zeno-created-at") >= '2020-12-25'
            and e."type" in ('generic', 'ethical')
            and e."zeno-drug-created-by" = 'user@generico.in'
    """
    rs_db.execute(base_q, params=None)
    base: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    base['gen-cnt'] = np.where(base['type'] == 'generic', 1, 0)
    base['eth-cnt'] = np.where(base['type'] == 'ethical', 1, 0)
    fixed_gen_eth_cnt = base.groupby(['zeno-order-id', 'composition']).agg({'gen-cnt': "sum", 'eth-cnt': "sum"}).reset_index()
    # to exclude case where lead contains same composition both ethical and generic drug
    exclusion = fixed_gen_eth_cnt[(fixed_gen_eth_cnt['gen-cnt'] > 0) & (fixed_gen_eth_cnt['eth-cnt'] > 0)]
    #take only ethical as left table
    base_eth = base[(base['type'] == 'ethical')]
    base_eth.drop(['gen-cnt', 'eth-cnt'],
                  axis='columns', inplace=True)
    base_eth['zeno-order-id'] = base_eth['zeno-order-id'].astype(str)
    exclusion['zeno-order-id'] = exclusion['zeno-order-id'].astype(str)
    base_eth['composition'] = base_eth['composition'].astype(str)
    exclusion['composition'] = exclusion['composition'].astype(str)
    datamerge = pd.merge(base_eth, exclusion, how='left', on=['zeno-order-id', 'composition'])
    # exclude leads with both eth gen same composition
    final_eth = datamerge[datamerge['gen-cnt'].isna()]
    final_eth.drop(['gen-cnt', 'eth-cnt'],
                   axis='columns', inplace=True)
    # join pso to check whether ethical was substituted to gen by CRM
    pso_q = """
    select
            pso."zeno-order-id",
            pso."drug-id" as "pso-drug-id",
            pso."drug-name" as "pso-drug-name",
            pso."store-id",
            d.composition,
            d."type" as "pso-drug-type",
            pso."created-by" as "pso-created-by"
        from 
           (select * ,ROW_NUMBER () over (partition by  pso."zeno-order-id" order by pso."created-at" desc) rk 
            from  "prod2-generico"."patients-store-orders" pso
                where "order-source" = 'zeno'
            ) pso
        left join "prod2-generico"."drugs" d on
            d.id = pso."drug-id"
        where rk = 1
        """
    rs_db.execute(pso_q, params=None)
    pso: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    pso['zeno-order-id'] = pso['zeno-order-id'].astype(str)
    pso['composition'] = pso['composition'].astype(str)
    datamerge = pd.merge(final_eth, pso, how='left', on=['zeno-order-id', 'composition'])
    joined = datamerge.copy()
    # substitutables
    substitutable_q = """
        select
            distinct id as "composition-master-id" ,
            "composition"  as "substitutable-composition"  from
            "prod2-generico"."substitutable-compositions"
            """
    rs_db.execute(substitutable_q, params=None)
    substitutable: pd.DataFrame = rs_db.cursor.fetch_dataframe()
    joined['composition-master-id'] = joined['composition-master-id'].astype(int,errors='ignore')
    substitutable['composition-master-id'] = substitutable['composition-master-id'].astype(int,errors='ignore')
    datamerge = pd.merge(joined, substitutable, how='left', on=['composition-master-id'])
    datamerge['substitutable-composition-flag'] = np.where(pd.isnull(datamerge['substitutable-composition']) == False, 1, 0)
    datamerge.drop(['substitutable-composition'],
                   axis='columns', inplace=True)
    ecomm_pso_sub = datamerge.copy()
    # only consider leads for which pso was made
    ecomm_pso_sub = ecomm_pso_sub[(pd.isnull(datamerge['pso-drug-id'])==False)]
    ecomm_pso_sub['preferred-store-id'] = ecomm_pso_sub['preferred-store-id'].astype(int, errors='ignore')
    ecomm_pso_sub['store-id'] = ecomm_pso_sub['store-id'].astype(int, errors='ignore')
    #etl
    ecomm_pso_sub['created-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    ecomm_pso_sub['updated-at'] = datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    ecomm_pso_sub['created-by'] = 'etl-automation'
    ecomm_pso_sub['updated-by'] = 'etl-automation'
    if isinstance(table_info, type(None)):
        raise Exception(f"table: {table_name} do not exist, create the table first")
    else:
        logger.info(f"Table:{table_name} exists")

        truncate_query = f''' DELETE FROM "{schema}"."{table_name}" '''
        rs_db.execute(truncate_query)

        s3.write_df_to_db(df=ecomm_pso_sub[table_info['column_name']], table_name=table_name, db=rs_db,
                          schema=schema)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    parser.add_argument('-l', '--limit', default=None, type=int, required=False)
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    logger = get_logger()
    logger.info(f"env: {env}")
    logger.info(f"logger.info the env again: {env}")

    rs_db = DB()
    rs_db.open_connection()

    s3 = S3()

    """ calling the main function """
    main(rs_db=rs_db, s3=s3)

    # Closing the DB Connection
    rs_db.close_connection()
