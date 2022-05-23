import argparse
import os
import sys

from zeno_etl_libs.db.db import DB

sys.path.append('../../../..')
from zeno_etl_libs.logger import get_logger
from zeno_etl_libs.helper.aws.s3 import S3

parser = argparse.ArgumentParser(description="This is ETL script.")
parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                    help="This is env(dev, stage, prod)")

args, unknown = parser.parse_known_args()
env = args.env

os.environ['env'] = env
logger = get_logger()

db = DB(read_only=False)
db.open_connection()

tables_meta = {
    "acm": {
        "pk": ["code", "Slcd"],
        "full_dump": 1
    },
    "item": {
        "pk": ["code"],
        "full_dump": 1
    },
    "fifo": {
        "pk": ["psrlno"],
        "full_dump": 1
    },
    "salepurchase1": {
        "pk": ["vtyp", "vdt", "vno", "subvno"],
        "full_dump": 1
    },
    "salepurchase2": {
        "pk": ["Vtype", "Vdt", "Vno", "Itemc", "Psrlno", "srlno"],
        "full_dump": 1
    },
    "master": {
        "pk": ["code"],
        "full_dump": 1
    },
    "billtrackmst": {
        "pk": ["srl"],
        "full_dump": 1
    },
    "company": {
        "pk": ["code"],
        "full_dump": 1
    },
    "acmextra": {
        "pk": ["Code", "slcd"],
        "full_dump": 1
    },
    "dispatchstmt": {
        "pk": ["TagNo", "TagDt", "Vdt", "Vtype", "Vno"],
        "full_dump": 1
    },
    "app-sp2upd": {
        "pk": ["Vtype", "Vdt", "Vno", "Itemc", "Psrlno", "NewPsrlno", "PorderNo"]
    },
    "acknow": {
        "pk": ["vtype", "Vno", "Srl"],
        "full_dump": 1
    },
    "proofsp1": {
        "pk": ["Vtype", "Vdt", "Vno"]
    },
    "proofsp2": {
        "pk": ["Vtype", "Vdt", "Vno", "Ordno", "Itemc"]
    },
    "porder": {
        "pk": ["Ordno", "acno", "itemc"],
        "full_dump": 1
    },
    "porderupd": {
        "pk": ["Ordno", "acno", "itemc"]
    },
    "salt": {
        "pk": ["code"],
        "full_dump": 1
    },
    "billost": {
        "pk": ["Vtype", "vdt", "Vno", "SubVno"],
        "full_dump": 1
    },
    "rcptpymt": {
        "pk": ["vtype", "vdt", "vno"],
        "full_dump": 1
    },
    "app-sp2": {
        "pk": ["Vtype", "Vdt", "Vno", "Itemc", "Psrlno", "NewPsrlno", "PorderNo"],
        "full_dump": 1
    },
    "adjstmnt": {
        "pk": ["vtype", "vdt", "vno", "avtype", "avdt", "avno", "amount", "Srlno", "SubVno", "RefNo"],
        "full_dump": 1
    }
}

""" Since s3 lists everything in asc order so processing on First Come basic """
# list all the date folder on s3
bucket_name = 'generico-node-internal'
schema = "prod2-generico"

s3 = S3(bucket_name=bucket_name)
env_folder = "production" if env == "prod" else "staging"

date_list_response = s3.s3_client.list_objects_v2(
    Bucket=bucket_name,
    Delimiter='/',
    MaxKeys=100,
    Prefix=f"wms/data-sync-to-s3/non-processed/{env_folder}/"
)

for date_data in date_list_response['CommonPrefixes']:
    file_list_response = s3.s3_client.list_objects_v2(
        Bucket='generico-node-internal',
        Delimiter='/',
        MaxKeys=100,
        Prefix=date_data['Prefix']
    )
    for file in file_list_response['Contents']:
        key = file['Key']
        file_name = key.split("/")[-1]
        table_name = file_name.split("_")[0].lower()
        temp_table_name = f"temp-{table_name}"
        file_s3_uri = f"s3://{bucket_name}/{key}"

        if table_name in [t.lower() for t in tables_meta.keys()]:

            logger.info(f"Syncing key: {key}")
            try:
                """ create temp table """
                create_temp_table_query = f"""
                create temp table IF NOT EXISTS "{temp_table_name}" (like "{schema}"."{table_name}");
                """
                db.execute(query=create_temp_table_query)
                logger.info(f"Created temp table: {temp_table_name}")

                """ insert data into the temp table """
                s3.write_to_db_from_s3_csv(table_name=temp_table_name, file_s3_uri=file_s3_uri, db=db)
                logger.info(f"Inserted data in temp table: {temp_table_name}")

                """ delete the common data between the temp and original table """
                if tables_meta[table_name].get("full_dump"):
                    delete_common_data_query = f""" DELETE FROM "{schema}"."{table_name}" ; """
                else:
                    filter_list = []
                    for pk in tables_meta[table_name]['pk']:
                        _pk = pk.lower()
                        filter_list.append(f""" "{schema}"."{table_name}"."{_pk}" = source."{_pk}" """)
                    filter_str = " and ".join(filter_list)

                    delete_common_data_query = f"""
                        DELETE FROM 
                            "{schema}"."{table_name}"
                        USING 
                            "{temp_table_name}" source
                        WHERE 
                            {filter_str};
                    """
                db.execute(query=delete_common_data_query)
                logger.info(f"Deleted old data from target table: {table_name}")

                """ Insert the new data """
                insert_query = f"""
                    insert into "{schema}"."{table_name}" select * from "{temp_table_name}"
                """
                db.execute(query=insert_query)
                logger.info(f"Inserted new data in target table: {table_name}")

                """ clear the temp table """
                clear_temp_table_query = f"""
                    delete from "{temp_table_name}"
                """
                db.execute(query=clear_temp_table_query)
                logger.info(f"Clearing temp table for next round: {temp_table_name}")

                """ move the file to processed folder from non-processed """
                target_key = key.replace("non-processed", "processed")
                s3.move_s3_obj(source=f"/{bucket_name}/{key}", target_key=target_key)
                logger.info(f"Moved file to processed folder: {target_key}")
            except Exception as e:
                logger.exception(e)
