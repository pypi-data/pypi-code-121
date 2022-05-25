import logging
import os
import re
import time
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient


class ClustersClient(dbclient):
    create_configs = {'num_workers',
                      'autoscale',
                      'cluster_name',
                      'spark_version',
                      'spark_conf',
                      'aws_attributes',
                      'node_type_id',
                      'driver_node_type_id',
                      'ssh_public_keys',
                      'custom_tags',
                      'cluster_log_conf',
                      'init_scripts',
                      'docker_image',
                      'spark_env_vars',
                      'autotermination_minutes',
                      'enable_elastic_disk',
                      'instance_pool_id',
                      'policy_id',
                      'pinned_by_user_name',
                      'creator_user_name',
                      'cluster_id'}

    def get_cluster_list(self, alive=True):
        """
        Returns an array of json objects for the running clusters.
        Grab the cluster_name or cluster_id
        """
        clusters_list = self.get("/clusters/list").get('clusters', [])
        if alive and clusters_list:
            running = filter(lambda x: x['state'] == "RUNNING", clusters_list)
            return list(running)
        else:
            return clusters_list

    def get_cluster_acls(self, cluster_id, cluster_name):
        """
        Export all cluster permissions for a specific cluster id
        :return:
        """
        perms = self.get(f'/preview/permissions/clusters/{cluster_id}/')
        perms['cluster_name'] = cluster_name
        return perms

    #returns cluster ID
    def get_cluster_id_by_name(self, cname, running_only=False):
        cluster_list = self.get('/clusters/list').get('clusters', [])
        if running_only:
            running = list(filter(lambda x: x['state'] == "RUNNING", cluster_list))
            for x in running:
                if cname == x['cluster_name']:
                    return x['cluster_id']
        else:
            for x in cluster_list:
                if cname == x['cluster_name']:
                    return x['cluster_id']
        return None

    def get_iam_role_by_cid(self, cid):
        if self.is_aws():
            cluster_resp = self.get(f'/clusters/get?cluster_id={cid}')
            return cluster_resp.get('aws_attributes').get('instance_profile_arn', None)
        return None

    def get_instance_pools(self):
        current_pools = self.get('/instance-pools/list').get('instance_pools', None)
        return current_pools



    def get_global_init_scripts(self):
        """ return a list of global init scripts. Currently not logged """
        ls = self.get('/dbfs/list', {'path': '/databricks/init/'}).get('files', None)
        if ls is None:
            return []
        else:
            global_scripts = [{'path': x['path']} for x in ls if x['is_dir'] == False]
            return global_scripts

    def get_spark_versions(self):
        return self.get("/clusters/spark-versions")

    def get_instance_profiles_list(self):
        if self.is_aws():
            ip_json_list = self.get('/instance-profiles/list').get('instance_profiles', [])
            return ip_json_list
        return []
        
    def get_policies(self):
        """
        mapping function to get the new policy ids. ids change when migrating to a new workspace
        read the log file and map the old id to the new id
        :param old_policy_id: str of the old id
        :return: str of new policy id
        """
        current_policies = self.get('/policies/clusters/list').get('policies', [])
        return current_policies


    def is_spark_3(self, cid):
        spark_version = self.get(f'/clusters/get?cluster_id={cid}').get('spark_version', "")
        sv = int(spark_version.split('.')[0])
        if sv >= 7:
            return True
        else:
            return False


 
