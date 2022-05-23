#!/usr/bin/python3

import requests
# from feii.log import Log
from feii.config import Config
from feii.request import Request

class Cluster(Config, Request):
  def __init__(self,
    cluster: str = {},
  ):
    super().__init__()
    self.cluster = cluster

  def get_status_cluster(self):
    self.cluster = requests.get("{0}/_cluster/health".format( self.ELASTIC_URL )).json()

  def check_status_cluster_not_red(self):
    return self.cluster['status'] != "red"

  def check_count_relocating_shards_in_cluster(self):
    return int(self.cluster['relocating_shards']) <= self.MAX_RELOCATING

  def check_count_pending_tasks_in_cluster(self):
    return int(self.cluster['number_of_pending_tasks']) <= self.MAX_TASKS

  def retry_failed(self):
    self.request = requests.post("{0}/_cluster/reroute?retry_failed".format( self.ELASTIC_URL ))

  def check_retry_failed(self):
    if self.status_request():
      self.logger.info("Retry_failed for index is over")
      return True
