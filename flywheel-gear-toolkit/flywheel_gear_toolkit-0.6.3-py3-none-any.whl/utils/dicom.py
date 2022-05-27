import copy
import logging
import re
import sys
import typing as t
import warnings

log = logging.getLogger(__name__)

try:
    from fw_file.dicom import DICOM, DICOMCollection, get_config
    from fw_file.dicom.dicom import get_value
    from fw_meta import MetaData

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from nibabel.nicom import csareader
    from pydicom.datadict import tag_for_keyword
except (ModuleNotFoundError, ImportError):
    raise ValueError(
        "fw-file and nibabel required to use this module."
        " Hint: install the extra `dicom`"
    )

# Enabling some pydicom callbacks
CONFIG = get_config()


DENY_TAGS = {
    "PixelData",
    "Pixel Data",
    "ContourData",
    "EncryptedAttributesSequence",
    "OriginalAttributesSequence",
    "SpectroscopyData",
    "MrPhoenixProtocol",  # From Siemens CSA
    "MrEvaProtocol",  # From Siemens CSA
    "FileMetaInformationVersion",  # OB in file_meta
}

# TODO: extend that set
ARRAY_TAGS = {
    "AcquisitionNumber",
    "AcquisitionTime",
    "EchoTime",
    "ImageOrientationPatient",
    "ImagePositionPatient",
    "ImageType",
    "InstanceNumber",
    "SliceLocation",
}

# Private Dicom tag to keep, in the format (PrivateCreatorName, 0099xx10)
PRIVATE_TAGS = set()

# matches either hexadecimal, keyword or private tag notation
# e.g. "00100020" or "PatientID" or "GEMS_PARM_01, 0043xx01"
VALID_KEY = re.compile(r"^[\dA-Fa-f]{8}$|^[A-Za-z]+$|^\w+,\s*\d{4}[xX]{2}\d{2}$")


def remove_empty_values(d: t.Dict, recurse=True) -> t.Dict:
    """Removes empty value in dictionary.

    Args:
        d (dict): A dictionary.
        recurse (bool): If true, recurse nested dictionary.

    Returns:
        dict: A filtered dictionary.
    """
    d_copy = copy.deepcopy(d)
    for k, v in d.items():
        if isinstance(v, dict) and recurse:
            d_copy[k] = remove_empty_values(v, recurse=recurse)
        if v == "" or v is None or v == [] or v == {}:
            d_copy.pop(k)
    return d_copy


def update_array_tag(custom_tags: t.Dict[str, bool]):
    """Update PRIVATE_TAGS and ARRAY_TAGS list.

    Args:
        custom_tags (dict): Dictionary of type with key/value of type tag: bool.
            If bool=True, tag is added to PRIVATE_TAGS and ARRAY_TAGS. If bool=False,
            tag is removed from PRIVATE_TAGS and ARRAY_TAGS.
    """
    if custom_tags:
        # validate key/value
        for k, v in custom_tags.items():
            if not VALID_KEY.match(k):
                log.error(
                    "Invalid key defined in project.info.context.header.dicom: %s\n"
                    "Valid key format is hexadecimal (e.g. '00100020'), "
                    "keyword (e.g. 'PatientID') or "
                    "private tag notation (e.g. 'GEMS_PARM_01, 0043xx01'). "
                    "Please check your project context.",
                    k,
                )
                sys.exit(1)
            if isinstance(v, str):
                if v.strip().lower() == "false":
                    custom_tags[k] = False
                elif v.strip().lower() == "true":
                    custom_tags[k] = True
                else:
                    log.error(
                        "Invalid value defined in project.info.context.header.dicom "
                        "for key %s. Valid value is boolean, 'True' or 'False'",
                        k,
                    )
                    sys.exit(1)

        for k, bool_val in custom_tags.items():
            is_private = False

            if "," in k:  # key pattern is "PrivateCreatorName, GGGGxxEE"
                k = tuple(p.strip() for p in k.split(","))  # type: ignore
                is_private = True

            if bool_val:
                if is_private and k not in PRIVATE_TAGS:
                    PRIVATE_TAGS.add(k)
                if k not in ARRAY_TAGS:
                    ARRAY_TAGS.add(k)  # type: ignore
            else:
                if k in PRIVATE_TAGS:
                    PRIVATE_TAGS.remove(k)
                if k in ARRAY_TAGS:
                    ARRAY_TAGS.remove(k)
                if k not in DENY_TAGS:
                    DENY_TAGS.add(k)  # type: ignore


def get_preamble_dicom_header(dcm: DICOM):
    """Returns a dictionary representation of the dicom header preamble of the DICOM instance.

    Args:
        dcm (DICOM): The DICOM instance.

    Returns:
        dict: A dictionary representation of the dicom preamble header.
    """
    header = {}

    for kw in dcm.dataset.file_meta.dir():
        if kw in DENY_TAGS:
            continue
        header[kw] = get_value(dcm.dataset.file_meta[kw].value)
    return header


def get_core_dicom_header(dcm: DICOM):
    """Returns a dictionary representation of the dicom header but the preamble.

    Args:
        dcm (DICOM): The DICOM instance.

    Returns:
        dict: A dictionary representation of the dicom header.
    """
    header: t.Dict[str, t.Any] = {}

    for kw in dcm.dir() + list(PRIVATE_TAGS):
        if kw in DENY_TAGS:
            log.debug(f"Skipping {kw} - in DENY_TAGS.")
            continue
        # some keyword may be repeating group and none unique
        if tag_for_keyword(kw) is None and kw not in PRIVATE_TAGS:
            log.debug(f"Skipping {kw} - none unique.")
            continue
        try:
            elem = dcm.get_dataelem(kw)
            if elem.is_private and isinstance(kw, tuple):
                header_kw = ",".join(kw)
            else:
                header_kw = kw
            if elem.VR == "SQ":
                header[header_kw] = []
                for i, ds in enumerate(dcm[kw]):
                    header[header_kw].append(get_core_dicom_header(ds))
            else:
                header[header_kw] = dcm[kw]
        except KeyError:  # private tag
            continue

    return header


def get_siemens_csa_header(dcm: DICOM) -> t.Dict:
    """Returns a dict containing the Siemens CSA header for image and series.

    More on Siemens CSA header at https://nipy.org/nibabel/dicom/siemens_csa.html.

    Args:
        dcm (DICOM): The DICOM instance.

    Returns:
        dict: A dictionary containing the CSA header.

    """
    csa_header: t.Dict[str, t.Any] = {"image": {}, "series": {}}
    csa_header_image = csareader.get_csa_header(dcm.dataset.raw, csa_type="image")
    if csa_header_image:
        csa_header_image_tags = csa_header_image.get("tags", {})
        for k, v in csa_header_image_tags.items():
            if (v["items"] is not None and not v["items"] == []) and k not in DENY_TAGS:
                csa_header["image"][k] = v["items"]

    csa_header_series = csareader.get_csa_header(dcm.dataset.raw, csa_type="series")
    if csa_header_series:
        csa_header_series_tags = csa_header_series.get("tags", {})
        for k, v in csa_header_series_tags.items():
            if (v["items"] is not None and not v["items"] == []) and k not in DENY_TAGS:
                csa_header["series"][k] = v["items"]

    return csa_header


def get_dicom_array_header(collection: DICOMCollection):
    """Returns array of dicom tags for tag in ARRAY_TAGS."""
    array_header = {}
    for t in ARRAY_TAGS:
        arr = collection.bulk_get(t)
        if any(arr):
            array_header[t] = arr
    return array_header


def get_dicom_header(dcm: DICOM):
    """Returns a dictionary representation of the dicom header of the DICOM instance.

    Args:
        dcm (DICOM): The DICOM instance.

    Returns:
        dict: A dictionary representation of the dicom header.
    """
    header = {}

    header.update(get_preamble_dicom_header(dcm))
    header.update(get_core_dicom_header(dcm))
    header = remove_empty_values(header)

    return header


def get_file_info_header(
    dcm: DICOM,
    collection: t.Optional[DICOMCollection] = None,
    siemens_csa: bool = False,
) -> t.Dict:
    """Returns a dictionary representing the header of the DICOM instance.

    Args:
        dcm (DICOM): The DICOM instance.
        collection (DICOMCollection or None): A DICOMCollection instance.
        siemens_csa (bool): If true, extracts the Siemens CSA header and stores under
            "csa" key.

    Returns:
        dict: A dictionary containing the header information.
    """
    header = dict()
    header["dicom"] = get_dicom_header(dcm)
    if collection:
        header["dicom_array"] = get_dicom_array_header(collection)
    if siemens_csa:
        manufacturer = header["dicom"].get("Manufacturer")
        if (
            manufacturer
            and isinstance(manufacturer, str)
            and manufacturer.lower().strip() != "siemens"
        ):
            log.info("Manufacturer is not Siemens - skipping CSA parsing")
            return header
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                header["csa"] = get_siemens_csa_header(dcm)
    return header
