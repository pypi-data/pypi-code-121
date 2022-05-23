""""
directory_paths

Define functions to get common hydrogen directory paths.
"""
import os
import json

def get_hydrodata_directory():
    """Returns the full path of the hydroframe /hydrodata directory containing large files."""
    result = os.environ.get("HYDRODATA", None)
    if not result or not os.path.exists(result):
        # If the HYDRODATA environment variable is not used use default
        result = "/hydrodata"

    return result


def get_hydro_common_directory():
    """Returns the common directory in /home/HYDROAPP/common that contains common static files for all users."""

    # The 'standard' place is different depending upon whether code is running on the client, the VM host or a Docker container
    # It is one of the directories specified by these environment variables
    result = None
    hydrocommon = os.environ.get("HYDROCOMMON", "")
    directory_options = [hydrocommon, "/hydrocommon", "/home/HYDROAPP/common"]
    for dirpath in directory_options:
        if os.path.exists(dirpath):
            result = dirpath
            break
    return result


def get_data_directory():
    """Returns the full path name of the data directory where files are stored, or None if not configured."""

    # The 'standard' place is different depending upon whether code is running on the client, the VM host or a Docker container
    # It is one of the directories specified by these environment variables
    result = None
    directory_env_variables = [
        "CONTAINER_HYDRO_DATA_PATH",
        "CLIENT_HYDRO_DATA_PATH",
        "HOST_HYDRO_DATA_PATH",
    ]
    for env_var in directory_env_variables:
        dirpath = os.environ.get(env_var, None)
        if dirpath is not None and os.path.exists(dirpath):
            result = dirpath
            break
    return result


def get_domain_path(message):
    """
    Returns the full path name to the domain directory.
    Use the user_id and domain_directory values in the message dict.
    """

    user_id = message.get("user_id", None)
    domain_directory = message.get("domain_directory", None)

    if user_id is None:
        raise Exception("No user_id provided.")
    if domain_directory is None:
        raise Exception("No domain_directory provided.")
    data_dir = get_data_directory()
    domain_path = f"{data_dir}/{user_id}/{domain_directory}"
    if not os.path.exists(domain_path):
        raise Exception(f"The domain directory '{domain_path}' does not exist.")
    return domain_path


def get_domain_state(message):
    """
    Return the contents of the domain_state.json object of the domain directory.
    Use the user_id and domain_directory values in the message dict.
    """

    result = None
    domain_path = get_domain_path(message)
    domain_state_name = f"{domain_path}/domain_state.json"
    database_name = f"{domain_path}/database.json"
    if os.path.exists(domain_state_name):
        with open(domain_state_name, "r") as stream:
            database = stream.read()
            result = json.loads(database)
    elif os.path.exists(database_name):
        # This is for backward compatibility until file name is changed
        with open(database_name, "r") as stream:
            database = stream.read()
            result = json.loads(database)
    return result

def get_domain_database(message):
    """
    Return the contents of the databse.json object of the domain directory.
    Use the user_id and domain_directory values in the message dict.
    This is deprecated. use get_domain_state() instead.
    """

    return get_domain_state(message)


def get_widget(message):
    """
    Return the visualization widget from the domain database associated with the
    domain and widget_id defined by the user_id, domain_directory and widget_id from
    the message dict.
    """

    result = None
    widget_id = message.get("widget_id", None)
    database = get_domain_database(message)
    if database is not None:
        for vis_index, vis in enumerate(database.get("visualizations", [])):
            for w_index, w in enumerate(vis.get("widgets", [])):
                if f"{vis_index}.{w_index}" == widget_id:
                    result = w
                    break
            if result:
                break
    return result
