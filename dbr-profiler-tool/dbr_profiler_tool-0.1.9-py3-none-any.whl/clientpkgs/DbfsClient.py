import ast
import json
import os
import time
from datetime import timedelta
from timeit import default_timer as timer

from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient


class DbfsClient(dbclient):

    @staticmethod
    def get_num_of_lines(fname):
        if not os.path.exists(fname):
            return 0
        else:
            i = 0
            with open(fname) as fp:
                for line in fp:
                    i += 1
            return i

    def get_dbfs_mounts(self, cid):
        ec_id = self.get_execution_context(cid)

        # get all dbfs mount metadata
        all_mounts_cmd = 'all_mounts = [{"path": x.mountPoint, "source": x.source, ' \
                                        '"encryptionType": x.encryptionType} for x in dbutils.fs.mounts()]'
        results = self.submit_command(cid, ec_id, all_mounts_cmd)
        results = self.submit_command(cid, ec_id, 'print(all_mounts)')
        dataresults = ast.literal_eval(results['data'])
        return dataresults


