#!/usr/bin/python3

# import os
from configparser import ConfigParser
from feii.config import Config

class PathToFile(Config):
  def __init__(self,
  ):
    super().__init__()

  def get_config(self):
    config_file = ConfigParser()
    config_file.read(self.path)
    self.t1 = config_file

    if config_file.has_option("CONFIG", "elastic_url"):
      Config.ELASTIC_URL = config_file.get("CONFIG", "elastic_url")

  def get_setting(self):
    if "CONFIG" in self.t1:
      for one, test in self.t1["CONFIG"].items():
        print("Name [{0}] - [{1}]".format( one, test ))
