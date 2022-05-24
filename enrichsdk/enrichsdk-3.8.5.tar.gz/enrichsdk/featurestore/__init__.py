import os
import sys
import json

from .schema import *


def post(backend, service=None, filename=None, data=None, debug=False):
    """
    Post featurestore to server

    Args:
      backend (object): Backend class enrichsdk.api.Backend
      service (object): Dictionary with name, path
      filename (str): Path to the input file to the posted
      data (dict): Dictionary to be posted (if filename not specified)

    Returns
      dict: Response dictionary from the server

    """

    if (
        (service is None)
        or (not isinstance(service, dict))
        or ("name" not in service)
        or (service["name"] not in ["run", "spec"])
    ):
        raise Exception("Unsupported service")

    url = service["path"] + "/add/?format=json"
    if not url.startswith("http"):
        url = backend.get_api_url(url, use_prefix=False)

    if debug:
        print("Backend URL: {}".format(url))

    if filename is None and data is None:
        raise Exception("Post requires either filename or data")

    try:
        if data is None:
            data = json.load(open(filename))
    except:
        raise Exception("Require a valid json file to post to server")

    name = service["name"]
    if name == "run":
        obj = FeatureGroupRun()
    elif name == "spec":
        obj = FeatureGroupSpec()
    else:
        raise Exception("Unknown service name: {}".format(name))

    # Add attributes
    for k, v in data.items():
        obj.add(k, v)

    # Check if the schema is valid
    obj.validate()

    data = obj.export()
    if debug:
        print("Data")
        print(json.dumps(data, indent=4))

    response = backend.call(url, method="post", data=data)
    return response


def download(
    backend, service=None, featuregroup_id=None, run_id=None, data=None, debug=False
):
    """
    Post featurestore to server

    Args:
      backend (object): Backend class enrichsdk.api.Backend
      service (object): Dictionary with name, path
      featuregroup_id (int): Id of the featuregroup to download
      run_id (int): Id of the run to download
      data (dict): Dictionary to be posted (if filename not specified)

    Returns
      dict: Response dictionary from the server

    """

    if (
        (service is None)
        or (not isinstance(service, dict))
        or ("name" not in service)
        or (service["name"] not in ["run", "spec"])
    ):
        raise Exception("Unsupported service")

    if featuregroup_id is not None:
        suffix = "/download/{}/?format=json".format(featuregroup_id)
    elif run_id is not None:
        suffix = "/download/{}/?format=json".format(run_id)
    else:
        raise Exception("One of featuregroup_id or run_id should be specified")

    url = service["path"] + suffix

    if not url.startswith("http"):
        url = backend.get_api_url(url, use_prefix=False)

    if debug:
        print("Backend URL: {}".format(url))

    response = backend.call(url, method="get")

    return response


def generate(backend, service=None, debug=False):
    """
    Generate sample specification files
    """

    if (
        (service is None)
        or (not isinstance(service, dict))
        or ("name" not in service)
        or (service["name"] not in ["run", "spec"])
    ):
        raise Exception("Unsupported service")

    name = service["name"]
    if name == "run":
        obj = FeatureGroupRun()
    elif name == "spec":
        obj = FeatureGroupSpec()
    else:
        raise Exception("Unknown service name: {}".format(name))

    return obj.export(dummy=True)


def search(backend, service=None, debug=False, params={}):
    """
    Search featurestore for specific featuregroups

    Args:
      backend (object): Backend class enrichsdk.api.Backend
      service (object): Dictionary with name, path
      args (dict): Search criteria as key, value paits
      debug (bool): Debug run or not

    Returns
      dict: Response dictionary from the server

    """

    if (
        (service is None)
        or (not isinstance(service, dict))
        or ("name" not in service)
        or (service["name"] not in ["run", "spec"])
    ):
        raise Exception("Unsupported service")

    suffix = "/search/?format=json"
    url = service["path"] + suffix

    if not url.startswith("http"):
        url = backend.get_api_url(url, use_prefix=False)

    if debug:
        print("Backend URL: {}".format(url))

    response = backend.call(url, method="get", params=params)

    return response
