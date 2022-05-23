#!/usr/bin/python3

# import re
import requests
from multiprocessing.dummy import Pool as ThreadPool
from feii.config import Config

class Init(Config):
  def __init__(self,
    count: int = 1,
  ):
    super().__init__()
    self.count = count

  def list_pools(self):
    pool = ThreadPool(int(self.count))
    results = pool.map(requests.get, self.ES_URLS)
    pool.close()
    return results
