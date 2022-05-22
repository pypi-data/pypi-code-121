# batch_node_id.py: runs on node to identify its batch POOL and NODE_ID
# batch_monitor.py: monitor the preemption/restart of nodes in an Azure Batch job
import sys

# from xtlib.backends.backend_batch import AzureBatch
# from xtlib.helpers import xt_config
# from xtlib import job_helper
# from xtlib.storage.store import Store

from azure.batch.models import TaskState, ComputeNodeState, JobState
import azure.batch.batch_auth as batch_auth
import azure.batch as batch

def main(args):
    batch_job_id = args[1]
    node_index = int(args[2])
    target = args[3]
    target_url = args[4]
    target_key = args[5]
    
    # config = xt_config.get_merged_config()    
    # store = Store(config=config)
    # compute = None  #  "labcoatbatch"

    # batch = AzureBatch(compute=target, compute_def=None, core=None, config=config)
    # batch.create_batch_client()

    credentials = batch_auth.SharedKeyCredentials(target, target_key)
    batch_client = batch.BatchServiceClient(credentials, batch_url= target_url)

    # get JOB_INFO 
    # job_info = job_helper.get_job_record(store, ws_id, job_id, {"pool_info": 1, "service_job_info": 1, "service_info_by_node": 1})
    # service_job_info = job_info["service_job_info"]
    # batch_job_id = service_job_info["batch_job_id"]

    # get TASK INFO
    task_id = "task" + str(node_index)
    print("batch_node_id: node_index: {}, batch_job_id: {}, task_id: {}".format(node_index, batch_job_id, task_id))

    task = batch_client.task.get(batch_job_id, task_id)
    node_info = task.node_info

    print("batch_node_id: task.state: {}, node_id: {}, pool_id: {}". \
        format(task.state, node_info.node_id, node_info.pool_id))

if __name__ == "__main__":
    # run as: python batch_node_id <batch_job_id> <node_index> <target> <target_url> <target_key> 
    # example: python -m xtlib.backends.batch_node_id tpx-store__tpx__job16 88 labcoatbatch https://labcoatbatch.eastus.batch.azure.com <key>
    main(sys.argv)