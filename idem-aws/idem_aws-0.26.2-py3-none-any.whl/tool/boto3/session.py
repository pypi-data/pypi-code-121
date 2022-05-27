import boto3.session


def __init__(hub):
    # Create a single session for everything to be run from
    hub.tool.boto3.SESSION = boto3.session.Session()


def get(hub, botocore_session=None) -> boto3.session.Session:
    """
    Get the current boto3 session.
    """
    if botocore_session is None:
        # Reset the session if need be for thread safety
        hub.tool.boto3.SESSION = boto3.session.Session()
    return hub.tool.boto3.SESSION
