from pypers.core.interfaces.db import get_operation_db
from pypers.core.interfaces import msgbus
import time


class Publish:

    def __init__(self, run_id):
        self.run_id = run_id

    def check_still_running(self):
        for coll in get_operation_db().get_run(self.run_id):
            if coll.get('pipeline_status', None) == 'RUNNING':
                return True
        return False

    def publish(self):
        # Loop for endings
        while self.check_still_running():
            print("Just check for pipeline ending. Still working..")
            time.sleep(10)
        # Trigger publish
        msgbus.get_publish_bus().send_message(
            self.run_id,
            [x['collection'] for x in get_operation_db().get_run(self.run_id) if x['pipeline_status'] == 'SUCCESS']
        )



