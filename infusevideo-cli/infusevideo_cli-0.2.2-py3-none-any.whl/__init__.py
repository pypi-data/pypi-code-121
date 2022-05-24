#!/usr/bin/env python3

from docopt import docopt
import json
import os
from pydantic import BaseSettings, Field, ValidationError, validator
import sys
from typing import Optional, Literal, Any, Union
import urllib.parse
import warnings

import infusevideo


doc = """
Usage: ivc METHOD ROUTEPART ...
           [--json=JSON] [--query=QUERY ...]
           [--file=PATH] [--file-field=FIELD]
           [--profile=NAME]
           [--script]
       ivc --generate-config
       ivc --clear-token [--profile=NAME]
       ivc --help

Arguments:
  METHOD      the method to use (GET, POST, PUT, PATCH or DELETE)
  ROUTEPART   the desired route, full or partial. Can be specified as:
                actual route "/media/abcdef/url"
                route parts "media" "abcdef" "url"

Options:
  --json=JSON          the JSON string to send in the request body
  --query=QUERY        data to pass on in the query string, as "name=value"
  --file=PATH          path to the file to upload. This will be sent as
                       multipart/form-data
  --file-field=FIELD   name of the field used for file upload. Default "file"
  --profile=NAME       name of the configuration profile to use
  --script             skip human authentication methods, when using this
                       program in a script. Alternatively, the program "ivs"
                       is the same as "ivc --script".

First use:
  --generate-config   generates a sample configuration file

Other:
  --clear-token   Clears the cached authentication token for the selected
                  profile. Only necessary when permissions were changed.

Help:
  -h --help   show this help
"""

warnings.filterwarnings(
	"ignore",
	"aliases are no longer used by BaseSettings to define which environment variables to read",
	FutureWarning,
)


class CommandlineOptions(BaseSettings):
	generateConfig: bool = Field(alias="--generate-config")
	clearToken: bool = Field(alias="--clear-token")
	profile: Optional[str] = Field(alias="--profile")
	help: bool = Field(alias="--help")
	script: bool = Field(alias="--script")
	fileField: str = Field(alias="--file-field", default="file")
	file: Optional[str] = Field(alias="--file")
	jsonData: Optional[str] = Field(alias="--json")
	queryData: list[str] = Field(alias="--query")
	method: Optional[str] = Field(alias="METHOD")
	routeparts: list[str] = Field(alias="ROUTEPART")

	@validator("method")
	def method_uppercase(cls, value: str) -> str:
		"""Validate the method is valid and convert it to uppercase"""
		if value is None:
			return value
		methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
		method = value.upper()
		if method not in methods:
			raise ValueError(f"Invalid value {value!r}, permitted: {', '.join(methods)}")
		return method

	@validator("jsonData")
	def is_valid_json(cls, value: Optional[str]) -> str:
		"""Validate the JSON is correct"""
		if value is None:
			return value
		try:
			json.loads(value)
		except json.decoder.JSONDecodeError as e:
			raise ValueError(f"Invalid JSON: {e}")
		return value

	@validator("queryData")
	def is_valid_querydata(cls, values: list[str]) -> list[str]:
		"""Validate the query data is in the correct format"""
		for value in values:
			if "=" not in value:
				raise ValueError(f"Missing '=' in {value!r}")
		return values

	@property
	def route(self) -> str:
		"""The route to query"""
		return "/" + "/".join([part.strip("/") for part in self.routeparts])

	@property
	def queryParams(self) -> list[tuple[str, str]]:
		"""The query parameters, split into a list of tuples"""
		return [tuple(query.split("=", maxsplit=1)) for query in self.queryData]


def cli() -> None:
	"""The actual CLI program"""
	# Process commandline options
	try:
		options = CommandlineOptions(**{k: v for k, v in docopt(doc).items() if v is not None})
	except ValidationError as e:
		print(e)
		sys.exit(1)

	# Determine whether ivc or ivs was invoked
	if os.path.basename(sys.argv[0]).startswith("ivs"):
		options.script = True

	# If requested, generate config and exit
	if options.generateConfig:
		try:
			path = infusevideo.Config.generate_sample_config()
			print(f"Sample configuration created at {path}.")
			sys.exit(0)
		except infusevideo.errors.ConfigAlreadyExists as e:
			print(str(e), file=sys.stderr)
			sys.exit(1)

	# Instantiate InfuseVideo
	try:
		api = infusevideo.InfuseVideo(options.profile, disableHumanAuth=options.script)
	except infusevideo.errors.ConfigNotFound as e:
		print(str(e), file=sys.stderr)
		print("A sample configuration file can be created by running:", file=sys.stderr)
		print(f"  {sys.argv[0]} --generate-config", file=sys.stderr)
		sys.exit(1)
	except infusevideo.Error as e:
		print(f"Error: {e}", file=sys.stderr)
		sys.exit(1)

	# If requested, clear the token cache and exit
	if options.clearToken:
		api.client.auth.clear_cache()
		print(f"Token cache cleared for profile {api.client.profile.name}")
		sys.exit(0)

	# Execute according to options
	try:
		response = api.client.request(
			options.method,
			options.route,
			params=options.queryParams,
			data=options.jsonData,
			fileName=options.file,
			fileField=options.fileField,
		)
		print(response)
	except infusevideo.errors.ApiError as e:
		print(f"!!! Request returned error code {e.response.code}", file=sys.stderr)
		print(e)
	except infusevideo.errors.RequestedScopeError as e:
		print(f"Authorization error: {e}", file=sys.stderr)
		print(f"You can refresh your token by executing:", file=sys.stderr)
		print(f"    {sys.argv[0]} --clear-token --profile {e.profile.name}", file=sys.stderr)
		print(f"and then trying again.", file=sys.stderr)
		sys.exit(1)
	except infusevideo.errors.AuthorizationError as e:
		print("An authorization error occurred:", file=sys.stderr)
		print(str(e), file=sys.stderr)
		sys.exit(1)
	except infusevideo.errors.AuthenticationError as e:
		print("An authentication error occurred:", file=sys.stderr)
		print(str(e), file=sys.stderr)
		sys.exit(1)
	except infusevideo.Error as e:
		print(f"Error: {e}", file=sys.stderr)
		sys.exit(1)
