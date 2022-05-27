import sys
import json
sys.path.append('../../../..')
from zeno_etl_libs.db.db import DB


class parameter:
    def __init__(self):
        self.cursor = None

    @staticmethod
    def get_params(job_id=None):
        db = DB()
        db.open_connection()
        query = f"""
                    SELECT parameter
                    FROM "prod2-generico"."job-paramater"
                    WHERE "job-id" = {job_id}
                """
        parameter = db.get_df(query=query)
        parameter_json = parameter.values[0][0]
        return json.loads(parameter_json)
