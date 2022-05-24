import datetime
import os
import time
import requests
from pypers.steps.base.step_generic import EmptyStep
from pypers.core.interfaces.db import get_cron_db, get_operation_db
from pypers.core.interfaces import msgbus
import boto3


class Submit(EmptyStep):
    """
    Triggers the fetch pipelines based on the db conf. Monitors the execution of them.
    Once all the triggered pipelines are done, it sends the publish message
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Triggers the fetch pipelines based on the db conf. "
            "Monitors the execution of them. Once all the triggered "
            "pipelines are done, it sends the publish message"
        ],
    }

    def get_scheduled_tasks(self):
        db_config = get_cron_db().read_config(self.pipeline_type)
        current_day = datetime.datetime.today().strftime('%w')
        to_return = []
        for collection in db_config.keys():
            if db_config[collection][int(current_day)] == '1':
                to_return.append(collection)
        return to_return

    def check_still_running(self):
        for coll in get_operation_db().get_run(self.run_id):
            if coll.get('pipeline_status', None) == 'RUNNING':
                return True
        return False

    def get_node_arn(self, cluster, pattern=None, anti_pattern=None):
        taks_per_service = {}
        client = boto3.client('ecs')
        for x in client.list_services(cluster=cluster).get('serviceArns', []):
            if pattern:
                for c in pattern:
                    if c in x.lower():
                        return x
            elif anti_pattern:
                found_node = True
                for c in anti_pattern:
                    if c in x.lower():
                        found_node = False
                        continue
                if found_node:
                    return x

    def start_service(self, cluster, pattern=None, anti_pattern=None, nb_tasks=1):
        client = boto3.client('ecs')
        service_arn = self.get_node_arn(cluster, pattern=pattern, anti_pattern=anti_pattern)
        client.update_service(
            cluster=cluster,
            service=service_arn,
            desiredCount=nb_tasks
        )
        while True:
            running_tasks = client.list_tasks(cluster=cluster, serviceName=service_arn).get('taskArns', [])
            if not running_tasks:
                continue
            desc = client.describe_tasks(cluster=cluster, tasks=running_tasks)
            is_started = True
            for task in desc.get('tasks', []):
                lastStatus = task.get('lastStatus')
                if lastStatus.lower() != 'running':
                    is_started = False
            if is_started:
                break
        return service_arn

    def stop_service(self, cluster, pattern=None, anti_pattern=None):
        client = boto3.client('ecs')
        service_arn = self.get_node_arn(cluster, pattern=pattern, anti_pattern=anti_pattern)
        client.update_service(
            cluster=cluster,
            service=service_arn,
            desiredCount=0)

    def process(self):
        cron_tab = self.get_scheduled_tasks()
        # Create the monitoring
        get_operation_db().create_run(self.run_id, cron_tab)
        # Trigger start for indexing and atac
        self.start_service('gbd-solr-ecs-cluster', anti_pattern=['blue', 'green'])
        self.start_service('gbd-etl-ecs-cluster', pattern=['atac'])
        # Trigger the messages
        for collection in cron_tab:
            output_dir = os.path.join(os.environ['WORK_DIR'],
                                      self.run_id,
                                      self.pipeline_type,
                                      collection)
            msgbus.get_msg_bus().send_message(
                self.run_id,
                collection=collection,
                type=self.pipeline_type,
                custom_config=['pipeline.output_dir=%s' % output_dir,
                               'pipeline.is_operation=True',
                               'steps.clean.chain=1'])
        # Loop for endings
        while self.check_still_running():
            self.logger.debug("Just check for pipeline ending. Still working..")
            time.sleep(10)
        # Trigger publish
        url = "%s/admin/cores?action=backup_and_release&target=brands&name=%s&repository=s3" % (
            os.environ.get('SLRW_URL', ''),
            self.run_id
        )
        result = requests.get(url)
        if result.status_code != requests.codes.ok:
            self.logger.error("%s failed with %s" % (url, result.status_code))
            result.raise_for_status()
        self.stop_service('gbd-etl-ecs-cluster', pattern=['atac'])
        #msgbus.get_publish_bus().send_message(
        #    self.run_id,
        #    [x['collection'] for x in get_operation_db().get_run(self.run_id) if x['pipeline_status'] == 'SUCCESS']
        #)



