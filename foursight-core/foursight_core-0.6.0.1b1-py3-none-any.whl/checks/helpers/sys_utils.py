import re
from datetime import datetime, timedelta
from dateutil import tz
from dcicutils import (
    es_utils,
)
from dcicutils.misc_utils import Retry


BUILD_INDICES_REGEX = re.compile('^[0-9]')  # build indices are prefixed by numbers


def wipe_build_indices(es_url, check):
    """ Wipes all number-prefixed indices on the given es_url. Be careful not to run while
        builds are running as this will cause them to fail.
    """
    check.status = 'PASS'
    check.summary = check.description = 'Wiped all test indices on url: %s' % es_url
    client = es_utils.create_es_client(es_url, True)
    full_output = []
    _, indices = cat_indices(client)  # index name is index 2 in row
    for index in indices:
        try:
            index_name = index[2]
        except IndexError:  # empty [] sometimes returned by API call
            continue
        if re.match(BUILD_INDICES_REGEX, index_name) is not None:
            try:
                resp = Retry.retrying(client.indices.delete, retries_allowed=3)(index=index_name)
            except Exception as e:
                full_output.append({'acknowledged': True, 'error': str(e)})
            else:
                full_output.append(resp)

    if any(output['acknowledged'] is not True for output in full_output):
        check.status = 'FAIL'
        check.summary = check.description = 'Failed to wipe all test indices, see full output'
    check.full_output = full_output
    return check


def parse_datetime_to_utc(time_str, manual_format=None):
    """
    Attempt to parse the string time_str with the given string format.
    If no format is given, attempt to automatically parse the given string
    that may or may not contain timezone information.
    Returns a datetime object of the string in UTC
    or None if the parsing was unsuccessful.
    """
    if manual_format and isinstance(manual_format, str):
        timeobj = datetime.strptime(time_str, manual_format)
    else:  # automatic parsing
        if len(time_str) > 26 and time_str[26] in ['+', '-']:
            try:
                timeobj = datetime.strptime(time_str[:26],'%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                return None
            if time_str[26]=='+':
                timeobj -= timedelta(hours=int(time_str[27:29]), minutes=int(time_str[30:]))
            elif time_str[26]=='-':
                timeobj += timedelta(hours=int(time_str[27:29]), minutes=int(time_str[30:]))
        elif len(time_str) == 26 and '+' not in time_str[-6:] and '-' not in time_str[-6:]:
            # nothing known about tz, just parse it without tz in this cause
            try:
                timeobj = datetime.strptime(time_str[0:26],'%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                return None
        else:
            # last try: attempt without milliseconds
            try:
                timeobj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return None
    return timeobj.replace(tzinfo=tz.tzutc())


def cat_indices(client):
    """ Wrapper function for the ES API _cat/indices so that the result returned is comprehensible.

        :param client: es client to use
        :returns: 2-tuple lists of header, rows
    """
    if not client:
        return [], []
    indices = client.cat.indices(v=True).split('\n')
    split_indices = [ind.split() for ind in indices]
    headers = split_indices.pop(0)  # first row is header
    return headers, split_indices
