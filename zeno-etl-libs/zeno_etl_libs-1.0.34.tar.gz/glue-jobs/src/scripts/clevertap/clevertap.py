import argparse
import os
import sys

sys.path.append('../../../..')

from zeno_etl_libs.helper.clervertap.clevertap import CleverTap


def main():
    ct = CleverTap(api_name="profiles.json", event_name="App Launched", batch_size=100, from_date=20220501,
                   to_date=20220501)
    ct.get_profile_data_all_records()
    print(f"All records count: {len(ct.all_records)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This is ETL script.")
    parser.add_argument('-e', '--env', default="dev", type=str, required=False,
                        help="This is env(dev, stag, prod)")
    args, unknown = parser.parse_known_args()
    env = args.env
    os.environ['env'] = env
    print(f"env: {env}")

    """ calling the main function """
    main()

    # # Closing the DB Connection
    # rs_db.close_connection()
