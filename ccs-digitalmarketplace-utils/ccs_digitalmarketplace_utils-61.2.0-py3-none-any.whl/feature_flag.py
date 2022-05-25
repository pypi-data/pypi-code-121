from dmapiclient.errors import HTTPError


def is_framework_in_status(data_api_client, framework_slug, statuses):
    """Checks if the status of a framework is in the provided list.
    This is to allow for features, such as banners, to only appear
    when a framework is in a specific state

    :param data_api_client: The app's data_api_client
    :param framework_slug: The framework we wish to check
    :param statuses: A list of the status that should return True

    :return: True if framework exists and is in one of the listed statuses,
             otherwise returns false

    """

    try:
        framework = data_api_client.get_framework(framework_slug)['frameworks']

        return framework['status'] in statuses
    except HTTPError as error:
        if error.status_code == 404:
            return False
        else:
            raise
