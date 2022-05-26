"""
Ascend Session module

The Session module encapsulates an HTTP session, and adds authentication.
All API requests pass through the Session.
"""

from __future__ import annotations

from ascend.auth.auth import AwsV4Auth, BearerAuth, RefreshAuth

import requests
from retry import retry
import urllib3


class Session:
  """
  Session implements an authenticated HTTP session to an Ascend host,
  including handling token exchange.

  # Parameters
  environment_hostname (str):
      hostname on which the Ascend environment you wish connect to is deployed
  access_key (str):
      Access Key ID you wish to use to authenticate with Ascend
  secret_key (str):
      Secret Access Key to use to authenticate with Ascend
  verify_ssl (bool):
      verify the server's SSL certificate
      (default is `True`)
  """
  @retry(tries=3)
  def __init__(self, environment_hostname, access_key, secret_key, verify_ssl=True):
    if not access_key:
      raise ValueError("Missing api access key")
    if not secret_key:
      raise ValueError("Missing api secret key")
    if not environment_hostname:
      raise ValueError("Missing environment hostname")
    if not verify_ssl:
      requests.packages.urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

    self.verify_ssl = verify_ssl
    self.base_uri = "https://{}:443/".format(environment_hostname)
    self.signed_session = requests.session()
    self.signed_session.auth = AwsV4Auth(access_key, secret_key, environment_hostname, "POST")

    self.init_token_exchange()

    self.bearer_session = requests.session()
    self.bearer_session.headers["Ascend-Service-Name"] = "sdk"
    self.bearer_session.auth = BearerAuth(self.access_token)

    self.refresh_session = requests.session()
    self.refresh_session.auth = RefreshAuth(self.refresh_token)

  def init_token_exchange(self):
    resp = self.signed_session.post(self.base_uri + "authn/tokenExchange", verify=self.verify_ssl)
    resp.raise_for_status()
    respJson = resp.json()
    self.access_token, self.refresh_token = respJson["data"]["access_token"], respJson["data"]["refresh_token"]
    import datetime
    self.expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)

  def refresh_api_key_hook(self, configuration):
    import datetime
    if (self.expiry - datetime.datetime.now()).total_seconds() < 0:
      self.exchange_tokens()
    configuration.api_key = {"Authorization": self.access_token}

  def refresh_token_exchange(self):
    resp = self.refresh_session.post(self.base_uri + "authn/tokenExchange", verify=self.verify_ssl)
    resp.raise_for_status()
    respJson = resp.json()
    self.access_token, self.refresh_token = respJson["data"]["access_token"], respJson["data"]["refresh_token"]
    self.bearer_session.auth = BearerAuth(self.access_token)
    self.refresh_session.auth = RefreshAuth(self.refresh_token)

  def exchange_tokens(self):
    if self.refresh_token:
      self.refresh_token_exchange()
    else:
      self.init_token_exchange()
