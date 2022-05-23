import sys
import os
import click
from pprint import pprint
from docarray import DocumentArray, Document
from jina import Client

try:
    from jfc.helper import Formats # if running Python package directly
except:
    from helper import Formats # if running via `python jfc ...`

def index(host, num_docs, data, tags, **kwargs):
    """
    Index data in various formats:

    CSV FILES
    One Document per line
    jfc index foo.csv

    EXISTING DOCUMENTARRAYS (coming later)
    Existing (pushed) DocumentArray from Jina Cloud
    jfc index docarray://foo

    GLOBS
    If jfc doesn't know what to do, it assumes a glob, and will index EVERY file that matches
    jfc index foo/**/*.jpg
    """
    # if config_file:
    # config = load_config(config_file)
    # else:
    # config = default_config

    # if host:
    # config["host"] = host
    # if num_docs:
    # config["indexing"]["num_docs"] = int(num_docs)
    # if data:
    # config["indexing"]["data"] = data

    if not host:
        print("Please specify a host with --host")
        sys.exit()

    if data.split(".")[-1] in Formats.table:
        print("Indexing from csv")
        docs = DocumentArray.from_csv(data, size=num_docs)

    elif data.startswith("docarray://"):
        raise NotImplementedError

    else:
        try:
            print("Assuming that this is a glob and treating as such")
            docs = DocumentArray.from_files(data, size=num_docs)
        except:
            print("Unknown format")
            print("Please run jfc --help for more information")

    docs.summary()

    client = Client(host)
    client.post("/update", docs, show_progress=True)


def search(data, host, tags, **kwargs):
    """
    Run a search operation against a Jina Flow

    FILE
    jfc search foo.jpg

    STRING
    jfc search "foo foo foo"
    """
    if os.path.exists(data):
        search_type = "file"
        doc = Document(uri=data)
        print(f"Searching with file {doc.uri}")

    else:
        # assume it's a string
        search_type = "text"
        print(search_type)
        doc = Document(text=data)

    client = Client(host=host)
    response = client.search(doc)

    for match in response[0].matches:
        if match.text:
            print(f"Text: {match.text}")
        if match.uri:
            print(f"URI: {match.uri}")
        print(f"Score: {match.scores['cosine'].value}")
        if tags:
            print("Tags:")
            pprint(match.tags)
        print("-" * 60)

def other_endpoint(endpoint, host):
    client = Client(host=host)
    response = client.post(on=f"/{endpoint}")

    for doc in response:
        print(doc.tags)



@click.command()
@click.argument("task")
@click.argument("data", required=False)
@click.option("--num_docs", "-n")
@click.option("--host", "-h")
@click.option("--tags", is_flag=True)
# @click.option("--config_file", "-c")
def main(task: str, host, num_docs, data, tags):
    if task == "index":
        index(data, host=host, num_docs=num_docs, tags=None)
    elif task == "search":
        search(data, host=host, num_docs=num_docs, tags=tags)
    else:
        other_endpoint(endpoint=task, host=host)


if __name__ == "__main__":
    main()
