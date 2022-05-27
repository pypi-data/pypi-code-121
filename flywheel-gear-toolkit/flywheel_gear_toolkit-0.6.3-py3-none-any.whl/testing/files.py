"""Testing fixtures for creating/mocking certain files."""
import io
import logging
import typing as t

import pytest

log = logging.getLogger(__name__)

# Pydicom and fw-file are optional deps.
try:
    import pydicom
    from fw_file import dicom
except (ImportError, ModuleNotFoundError):
    pass


#### Gear files
@pytest.fixture
def manifest():
    """Return a default manifest for a gear."""
    return {
        "name": "test",
        "version": "0.0.1",
        "author": "",
        "config": {},
        "description": "",
        "inputs": {},
        "label": "",
        "license": "MIT",
        "source": "",
        "url": "",
        "custom": {"gear-builder": {"image": "flywheel/test:0.0.1"}},
    }


@pytest.fixture
def run():
    """Return a dummy run file for a gear."""
    return """
    #!/usr/bin/env python
    print('Gear is running')
    """


@pytest.fixture
def dockerfile():
    """Return a dummy Dockerfile for a gear."""
    return """
    FROM python:3.8-buster
    COPY run.py ./
    COPY manifest.json ./

    RUN chmod +x run.py
    ENTRYPOINT ["python","run.py"]
    """


#### DCM files
# Borrowed from:
# https://gitlab.com/flywheel-io/tools/lib/fw-file/-/blob/1.3.3/tests/conftest.py#L60


def merge_dcmdict(custom: dict, default: dict) -> dict:
    """Merge a custom dict onto some defaults."""
    custom = custom or {}
    merged = {}
    for key, value in default.items():
        merged[key] = value
    for key, value in custom.items():
        if value is UNSET:
            merged.pop(key)
        else:
            merged[key] = value
    return merged


def apply_dcmdict(dataset: "pydicom.Dataset", dcmdict: dict) -> None:
    """Add dataelements to a dataset from the given dcmdict."""
    # pylint: disable=invalid-name
    try:
        dcmdict = dcmdict or {}
        for key, value in dcmdict.items():
            if isinstance(value, (list, tuple)) and len(value) == 2:
                VR_dict = pydicom.datadict.dictionary_VR(key)
                VR, value = value
                if VR == VR_dict:
                    dataset.add_new(key, VR, value)
                else:
                    try:
                        dataset.add_new(key, VR_dict, value)
                    except:
                        log.error(
                            f"Could not add key {key}, VR {VR_dict}, value {value}"
                        )
            else:
                VR = pydicom.datadict.dictionary_VR(key)
                dataset.add_new(key, VR, value)
    except NameError:
        log.error("Need pydicom to use this fixture.")
        return None


# sentinel value for merge() to skip default_dcmdict keys
UNSET = object()


default_dcmdict = dict(
    SOPClassUID="1.2.840.10008.5.1.4.1.1.4",  # MR Image Storage
    SOPInstanceUID="1.2.3",
    PatientID="test",
    StudyInstanceUID="1",
    SeriesInstanceUID="1.2",
)


@pytest.fixture
def default_dcmdict_fixture():
    """default dataset dict used in create_dcm."""
    return default_dcmdict


def create_ds(**dcmdict) -> t.Optional["pydicom.Dataset"]:
    try:
        dataset = pydicom.Dataset()
        apply_dcmdict(dataset, dcmdict)
        return dataset
    except NameError:
        log.error("Need pydicom to use this fixture.")
        return None


@pytest.fixture
def create_ds_fixture():
    """Create and return a dataset from a dcmdict."""
    return create_ds


def create_dcm(file=None, preamble=None, file_meta=None, **dcmdict):
    """Create a dummy dicom with configurable values.

    Args:
        file: Optional filepath
        preamble: Optional byte-string to set as the dataset preamble
        file_meta: Optional `pydicom.dataset.FileMetaDataset()`
        dcmdict: Dictionary with either `{<tag>: <value>}` or:
        .. code-block:: python

            {
                <key>: (<VR>, <value>)
            }
    Returns:
        (fw_file.dicom.DICOM): Dicom

    """
    try:
        dcmdict = merge_dcmdict(dcmdict, default_dcmdict)
        dataset = pydicom.FileDataset(file, create_ds(**dcmdict))
        dataset.preamble = preamble or b"\x00" * 128
        dataset.file_meta = pydicom.dataset.FileMetaDataset()
        apply_dcmdict(dataset.file_meta, file_meta)
        file = file or io.BytesIO()
        pydicom.dcmwrite(file, dataset, write_like_original=bool(file_meta))
        if isinstance(file, io.BytesIO):
            file.seek(0)
        return dicom.DICOM(file)
    except NameError:
        log.error("Need pydicom and fw-file to use this fixture.")
        return None


@pytest.fixture
def create_dcm_fixture():  # pylint: disable=redefined-outer-name
    """Wrapper for `create_dcm` function."""

    return create_dcm
