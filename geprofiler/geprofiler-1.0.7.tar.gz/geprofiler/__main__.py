# coding: utf-8

from __future__ import annotations
import asyncio
import codecs
from datetime import datetime

import optparse
import os
import sys
import tempfile
from typing import List, Type, cast
import webbrowser
import urllib.parse
import json
import strictyaml

import geprofiler
from geprofiler.renderers.html import HTMLRenderer
from geprofiler.util import add_header_to_curl, call_curl

def read_yaml(path: str):
    try:
        with open(path, "r") as f:
            yaml_file = strictyaml.load(f.read())
        return yaml_file, None
    except Exception as exc:
        print(exc)
        return None, exc

def main():
    usage = "usage: geprofiler [yaml file]"
    version_string = "geprofiler {v}, on Python {pyv[0]}.{pyv[1]}.{pyv[2]}".format(
        v=geprofiler.__version__,
        pyv=sys.version_info,
    )
    parser = optparse.OptionParser(usage=usage, version=version_string)
    parser.allow_interspersed_args = False

    parser.parse_args()

    yaml_file, err = read_yaml(os.path.join(os.getcwd(), "geprofiler.yaml"))
    if err: parser.error('File "geprofiler.yaml" is not found or not valid')

    params = yaml_file.data
    retry = params.get("retry", 1)
    request = params.get("request", {})
    output_dir = params.get("output_dir", None)

    curl_list = request.get("list", [])
    if len(curl_list) == 0:
        parser.error('request.list is not provided in "geprofiler.yaml"')

    curl_list = [add_header_to_curl(curl, "geprofiler: json") for curl in curl_list]

    responses = []
    loop = asyncio.get_event_loop()
    for req in curl_list:
        responses.append(loop.run_until_complete(call_curl(req)))

    # filtering responses
    filter = request.get("filter", None)
    if filter:
        min_duration = int(filter.get("min_duration", 0))
        if min_duration:
            responses = [r for r in responses if r['duration'] * 1000 >= min_duration]
    

    if len(responses) == 0:
        print("There is no response that matches the filter") 
        sys.exit(0)

    html_output = HTMLRenderer().render(None, json.dumps(responses))
    
    if output_dir is None:
        output_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        output_filename = output_file.name
        with codecs.getwriter("utf-8")(output_file) as f:
            f.write(html_output)
        url = urllib.parse.urlunparse(("file", "", output_filename, "", "", ""))
    else:
        filename = "geprofiler-{date}.html".format(
            date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        )
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_filename = os.path.join(output_dir, filename)
        with codecs.open(output_filename, "w+", "utf-8") as f:
            f.write(html_output)
        url = "file:///" + os.getcwd() + "/" + output_filename

    webbrowser.open(url)

if __name__ == "__main__":
    main()