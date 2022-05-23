#!/usr/bin/python3

# import requests
# from feii.config import Config

class Request:
  def __init__(self,
    request: str = '',
  ):
    super().__init__()
    self.request = request

  def status_request(self):
    return self.request.status_code == 200 or self.request.status_code == 201
