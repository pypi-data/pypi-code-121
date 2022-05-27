import logging
import re

from vaip.utilities.s3_helper import write_new_vaip, check_for_vaip


def get_shortname_from_config(extract_dict, obj_key):
    """
    Determine the shortname to match to the AIC.
    :param extract_dict: The configuration specifying the shortname.
    :param obj_key: The file's basename.
    :return: The shortname
    """
    for key in extract_dict['datastream'].keys():
        regex = extract_dict['datastream'][key]['regex']
        if re.search(rf"{regex}", rf"{obj_key}"):
            return extract_dict['datastream'][key]['short_name']

    raise KeyError(f"Unable to find datastream configuration for {obj_key}")


def remove_entry_from_collection_vaip(config, event, s3_client, uuid):
    """
    Remove the entry for this granule's UUID since it's been deleted.
    :param config: Parsed shortname from metadata_model.json.
    :param event: The event JSON from Lambda.
    :param s3_client: Use the same client to save some effort.
    :param uuid: The granule's UUID, which is the key for the granule array
        in the AIC.
    :return: Nothing.
    """
    shortname = get_shortname_from_config(config, event['key'])
    collection_aip_key = "collections/" + \
                         shortname[shortname.find(':') + 1:] + ".json"
    latest_collection_vaip = check_for_vaip(s3_client, collection_aip_key)
    if latest_collection_vaip is None:
        raise IOError(f"The AIC {collection_aip_key} was not found. "
                      f"This is unexpected for a delete event. Failing.")
    print(f"Latest AIC: {latest_collection_vaip}")

    granules = latest_collection_vaip[
        'preservation_description_information']['provenance']['granules']
    basename = event['key'].split('/')[-1]
    print("testing deleter AIC before for-loop.")
    for idx, granule in enumerate(granules):
        if basename in granule['uri']:
            logging.info("Removing this granule in the Collection VAIP.")
            granules.pop(idx)
            write_new_vaip(
                s3_client, latest_collection_vaip, collection_aip_key)
            return latest_collection_vaip

    raise IOError(
        f"Basename {basename} is not in the AIC {collection_aip_key}. "
        "This is unexpected for a delete event. Failing.")


def handle_granule_vaip(event, s3_client, aip_full_key):
    """
    Helper function to orchestrate the granule-level VAIP instantiation or
    update.
    :param event: Used to pull values from the extract_granule_metadata step.
    :param s3_client: Reuse the client for efficiency.
    :param aip_full_key: Prefixes and basename for the AIP file.
    :return: The new GVAIP JSON blob.
    """
    latest_vaip = check_for_vaip(s3_client, aip_full_key)
    logging.debug(f"Latest AIU: {latest_vaip}")

    if latest_vaip is None:
        raise IOError(f"The AIU {aip_full_key} was not found. "
                      f"This is unexpected for a delete event. Failing.")

    new_vaip = add_delete_version_to_gvaip(event, latest_vaip)
    logging.debug(f"New AIU: {new_vaip}")

    write_new_vaip(s3_client, new_vaip, aip_full_key)

    return new_vaip


def add_delete_version_to_gvaip(event, latest_aip):
    """
    Add a new version to a VAIP that registers the granule as deleted.
    :param event: The event JSON from Lambda.
    :param latest_aip: Current AIP JSON. Must exist or else an IOError is
        emitted.
    :return: The modified GVAIP.
    """
    # Taking version out for now
    # "id": version,
    prov_dict = {
        "action": "DELETED ({} BE RESTORED)",
        "folder": "version-0", "date": event['s3_event']['time']
    }

    if 'x-amz-delete-marker' not in event['s3_event']['detail']['responseElements']:
        logging.info("Registering a hard deletion. The object will not be "
                     "recoverable in the archive.")
        prov_dict['action'] = prov_dict['action'].format("CANNOT")
    else:
        logging.info("Registering a soft deletion. The object can still be "
                     "recovered in the archive using s3 versioning.")
        prov_dict['action'] = prov_dict['action'].format("CAN")

    versions_list = \
        latest_aip['preservation_description_information']['provenance'][
            'versions']
    last_version = versions_list[-1]['version']
    prov_dict['version'] = last_version + 1
    versions_list.append(prov_dict)

    return latest_aip