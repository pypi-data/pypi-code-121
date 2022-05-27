import logging
import os

from vaip.json.build.build_aiu import build_aiu, build_version
from vaip.json.build.build_aic import build_granule
from vaip.utilities.s3_helper import check_for_vaip, write_new_vaip


def handle_collection_vaip(event, s3_client, latest_granule_vaip):
    """
    Helper function to orchestrate the collection-level VAIP (AIC) update.
    We assume that the AIC has already been created in the collection state
    machine.
    :param event: Used to pull values from the extract_granule_metadata step.
    :param s3_client: Reuse the client for efficiency.
    :param latest_granule_vaip: The new GVAIP JSON blob.
    :return: NA.
    """
    collection_aip_key = "collections/" + \
                         event['granule']['shortname'].split(":")[-1] + ".json"
    init_collection_vaip = check_for_vaip(s3_client, collection_aip_key)
    if init_collection_vaip is None:
        raise IOError(
            "Expected to find an extant AIC file at "
            f"{os.environ['AIP_BUCKET']}/{collection_aip_key}. "
            "The collection may not have been processed successfully. "
            "Try to ingest it again."
        )

    logging.debug(f"Latest AIC: {init_collection_vaip}")
    aip_full_key = latest_granule_vaip['package_description'][
        'associated_description']['key']

    latest_collection_vaip = update_collection_vaip(
        init_collection_vaip,
        event['key'], aip_full_key,
        event['granule']['uuid'], event['granule']['vaip']['poc']
    )
    logging.debug(f"Latest AIC: {latest_collection_vaip}")

    write_new_vaip(s3_client, latest_collection_vaip, collection_aip_key)

    return latest_collection_vaip


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

    new_vaip = update_or_instantiate_granule_vaip(
        event, latest_vaip, event['key'],
        aip_full_key
    )
    logging.debug(f"New AIU: {new_vaip}")

    write_new_vaip(s3_client, new_vaip, aip_full_key)

    return new_vaip


def update_collection_vaip(collection_vaip, data_key, aip_full_key, uuid, poc):
    """
    Make a collection-level VAIP that has a list of each granule in the
    collection, keyed by UUID.
    :param collection_vaip: Any previously existing CVAIP that may have been found.
    :param data_key: Key to the data file in the archive bucket.
    :param aip_full_key: Key to the granule VAIP.
    :param uuid: Granule UUID.
    :param poc: Point of contact information
    :return: The Collection VAIP JSON blob.
    """
    json_key = 'granules/' + aip_full_key.replace(aip_full_key[aip_full_key.rfind('.'):], '.json')
    s3_base = "https://s3.console.aws.amazon.com/s3/object/" \
              "{0}?region=us-east-1&prefix={1}"
    data_file_uri = s3_base.format(os.environ['ARCHIVE_BUCKET'], data_key)
    vaip_uri = s3_base.format(os.environ['AIP_BUCKET'], json_key)
    granule_obj = build_granule(uuid, data_file_uri, vaip_uri)

    collection_vaip['preservation_description_information'][
        'provenance']['granules'].append(granule_obj.to_dict())
    collection_vaip['poc'] = poc
    return collection_vaip


def update_or_instantiate_granule_vaip(event, latest_aip, data_key, aip_full_key):
    """
    If latest_aip is not none, append to revisions. If latest_aip is
    none, build a new AIP from scratch.
    :param event: The event JSON from Lambda.
    :param latest_aip: Current AIP JSON if one exists.
    :param data_key: Full key of the data file.
    :param aip_full_key: Same filename and prefix as original data file,
        with json extension. Added an AIP folder before the basename.
    :return: A new VAIP JSON blob to save to the AIP bucket.
    """
    # Get values from event
    version_id = event["archive_result"]["VersionId"]
    date = event.get("archive_result").get("CopyObjectResult").get(
        "LastModified")

    checksum = event['granule']['checksum']
    size = event['granule']['size']
    vaip_config = event['granule']['vaip']
    retention = vaip_config['retention']
    algorithm = vaip_config['algorithm']

    if latest_aip is None:
        s3_base = "https://s3.console.aws.amazon.com/s3/object/" \
                  "{0}?region=us-east-1&prefix={1}"
        granule_uri = s3_base.format(os.environ['ARCHIVE_BUCKET'], data_key)
        vaip_uri = s3_base.format(os.environ['AIP_BUCKET'], aip_full_key)

        # TODO Change these values if we find different implementation
        vaip_class = 'archive_information_package'
        aip_type = 'archival_information_unit'
        package_description_type = 'unit description'

        vaip_obj = build_aiu(
            vaip_class, aip_type, event['granule']['uuid'],
            package_description_type, data_key,
            os.environ['ARCHIVE_BUCKET'], granule_uri, vaip_uri,
            checksum, algorithm, size, date, retention, 0, version_id
        )

        return vaip_obj.to_dict()

    else:
        versions_list = latest_aip["preservation_description_information"][
            "provenance"]["versions"]
        last_version = versions_list[-1]['version']
        new_version = last_version + 1
        new_version_obj = build_version(
            version_id, checksum, algorithm, size,
            date, retention, new_version
        )
        versions_list.append(new_version_obj.to_dict())

        return latest_aip
