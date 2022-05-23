#!/usr/bin/python3

# import sys
import logging
from os import path, remove

class Log:
  def __init__(self,
    log_file_name: str = 'feii.log'
  ):
    super().__init__()
    self.log_file_name = log_file_name
    self.logger = logging.getLogger()
    self.log_file_format = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

  def get_file_handler(self):
    self.file_handler = logging.FileHandler(self.log_file_name)
    self.file_handler.setFormatter(self.log_file_format)

  def get_stream_handler(self):
    self.stream_handler = logging.StreamHandler()
    self.stream_handler.setFormatter(self.log_file_format)

  def get_logger(self):
    self.logger.setLevel(logging.DEBUG)
    self.logger.addHandler(self.file_handler)
    self.logger.addHandler(self.stream_handler)

  def remove_old_log_file(self):
    if path.isfile(self.log_file_name):
      remove(self.log_file_name)

  def logging_level_critical(self, level):
    if level == 'critical' or level == 'CRITICAL' or level == '=critical' or level == '=CRITICAL':
      self.logger.setLevel(logging.CRITICAL)

  def logging_level_error(self, level):
    if level == 'error' or level == 'ERROR' or level == '=error' or level == '=ERROR':
      self.logger.setLevel(logging.ERROR)

  def logging_level_warning(self, level):
    if level == 'warning' or level == 'WARNING' or level == '=warning' or level == '=WARNING':
      self.logger.setLevel(logging.WARNING)

  def logging_level_info(self, level):
    if level == 'info' or level == 'INFO' or level == '=info' or level == '=INFO':
      self.logger.setLevel(logging.INFO)

  def logging_level_debug(self, level):
    if level == 'debug' or level == 'DEBUG' or level == '=debug' or level == '=DEBUG':
      self.logger.setLevel(logging.DEBUG)

  def logging_level_notset(self, level):
    if level == 'notset' or level == 'NOTSET' or level == '=notset' or level == '=NOTSET':
      self.logger.setLevel(logging.NOTSET)
