"""
This plugin provides an interface for interacting with the raw boto3 API using idem's acct system and CLI paradigm.

All underlying calls are done asynchronously in a Threadpool Executor
"""


def __init__(hub):
    # Provides the ctx argument to all execution modules
    # which will have profile info from the account module
    hub.exec.boto3.ACCT = ["aws"]

    # Load dynamic subs for accessing boto3 clients and resources
    hub.pop.sub.dynamic(
        sub=hub.exec.boto3,
        subname="client",
        resolver=hub.tool.boto3.resolve.client,
        context=None,
    )
    hub.pop.sub.dynamic(
        sub=hub.exec.boto3,
        subname="resource",
        resolver=hub.tool.boto3.resolve.resource,
        context=None,
    )
