import json
import os
from datetime import datetime
from pypers.core.interfaces.db import get_pre_prod_db
from pypers.core.interfaces.db import get_pre_prod_db_history


class Snapshot:

    def __init__(self, collection, type):
        self.collection = collection
        self.pipeline_type = type
        self.results = {}
        self._office_extraction_dates = set()

    def get_live_data(self):
        db = get_pre_prod_db()
        query_params = {
            'IndexName': 'gbd_docs_live_gbd_collection_st13',
            'KeyConditionExpression': "gbd_collection = :name_value",
            'ExpressionAttributeValues': {
                ":name_value": self.collection
            }
        }
        try:
            respone = db.table.query(**query_params)
            payload = db.replace_decimals(respone['Items'])
            for item in payload:
                self.results[item['st13']] = item
                self._office_extraction_dates.add(item['office_extraction_date'])
        except Exception as e:
            print("Error in getting the live data: %s" % e)

    def get_copies_data(self):
        db = get_pre_prod_db_history()
        for archive_date in list(self._office_extraction_dates):
            query_params = {
                'IndexName': 'gbd_docs_copies_office_extraction_date_st13',
                'KeyConditionExpression': "office_extraction_date = :name_value",
                'ExpressionAttributeValues': {
                    ":name_value": archive_date
                }
            }
            try:
                respone = db.table.query(**query_params)
                payload = db.replace_decimals(respone['Items'])
                for item in payload:
                    st13 = item['st13']
                    if st13 in self.results.keys():
                        self.results[item['st13']].update({
                            'ori_logo': item.get('logo', []),
                            'ori_document': item.get('biblio', None)
                        })
            except Exception as e:
                print("Error in getting the copies data: %s" % e)

    def collect_data(self, path='./'):
        self.get_live_data()
        self.get_copies_data()
        snapshot_name = 'snapshot.%s.%s' % (
            datetime.now().strftime('%Y%m%d%H%M'), self.collection
        )
        payload = [self.results[x] for x in self.results.keys()]
        snapshot_name = os.path.join(path, snapshot_name)
        with open(snapshot_name, 'w') as f:
            f.write(json.dumps(payload))
        print("Snapshot created in %s" % os.path.abspath(snapshot_name))
