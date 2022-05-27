import json
import logging
import os


def check_for_vaip(s3_client, aip_full_key):
    """
    Checks to see if a collection- or granule-level AIP exists.
    :param s3_client: Use the same client to save some effort.
    :param aip_full_key: Same filename and prefix as original data file,
    with json extension. Added an AIP folder before the basename.
    :return: None if no AIP already exists. The JSON if so.
    """
    try:
        s3_client.head_object(
            Bucket=os.environ['AIP_BUCKET'],
            Key=aip_full_key
        )
    except s3_client.exceptions.ClientError:
        logging.debug("No AIP currently exists. Making a new one.")
        return None

    logging.info("Found previous VAIP file. Will append to it.")
    vaip = s3_client.get_object(
        Bucket=os.environ['AIP_BUCKET'],
        Key=aip_full_key
    )
    return json.loads(vaip["Body"].read())


def write_new_vaip(client, vaip_json, aip_full_key):
    """
    Write a collection- or granule-level VAIP to the VAIP bucket.
    Granule VAIP:
        [AIP_BUCKET}/granules/[Same prefix as data file in archive bucket]/
            [same basename].json
        e.g., [AIP_BUCKET]/granules/NCEI/AVHRR/OISST/nc/oisst-avhrr-v02r01.20200607.json
    Collection VAIP:
        [AIP_BUCKET]/collections/[shortname, with : replaced with .].json
        e.g., [AIP_BUCKET]/collections/C00844.json
    :param client: Use the same s3 client to save effort.
    :param vaip_json: The AIP.
    :param aip_full_key: Same filename and prefix as original data file,
    with json extension. Added an AIP folder before the basename.
    :return: n/a
    """
    # todo regex to parse version+revision from granule files => v{1}\d{1,4}r{1}\d{1,4}
    #  future work: use the version# from metadata models or parse from file to use as part of AIP key
    # Example path granules/NCEI/AVHRR/OISST/v02r01/oisst-avhrr-v02r01.20200724.json
    return client.put_object(
        Bucket=os.environ["AIP_BUCKET"],
        Key=aip_full_key,
        Body=json.dumps(vaip_json).encode('utf-8'),
        StorageClass='STANDARD'
    )

def get_filename(path):
    basename = os.path.basename(path)
    return basename