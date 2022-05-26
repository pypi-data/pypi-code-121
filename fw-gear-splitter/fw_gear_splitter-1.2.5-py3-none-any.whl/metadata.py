"""Metadata handling."""
import datetime
import logging
import re
import typing as t
from collections import Counter
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.qc import add_qc_info
from fw_file.dicom import DICOMCollection
from fw_file.dicom.utils import generate_uid
from fw_meta.imports import load_file_name
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence
from tzlocal import get_localzone

from . import __version__, pkg_name

log = logging.getLogger(__name__)

VERSION = re.split(r"[^\d]+", __version__)


class SeriesName:
    def __init__(
        self,
        series_number: t.Optional[int],
        modality: t.Optional[str],
        series_description: t.Optional[str],
        number: t.Optional[int],
        localizer: bool = False,
    ):
        self.series_number = series_number
        self.modality = modality
        self.series_description = series_description
        self.number = number
        self.localizer = localizer

    def __eq__(self, other: "SeriesName") -> bool:
        return repr(self) == repr(other)

    def __hash__(self) -> str:
        return hash(repr(self))

    @classmethod
    def gen_name(
        cls,
        dcm: DICOMCollection,
        series_number: t.Optional[str] = None,
        number: t.Optional[int] = None,
    ) -> "SeriesName":
        """Class method to generate a SeriesName from a collection and optional series number.

        Args:
            dcm (DICOMCollection): Dicom archive
            series_number (t.Optional[str]): Optional series number.

        Returns:
            SeriesName: SeriesName object.
        """
        series_description: t.Optional[str] = Counter(
            dcm.bulk_get("SeriesDescription")
        ).most_common()[0][0]
        modality: t.Optional[str] = Counter(dcm.bulk_get("Modality")).most_common()[0][
            0
        ]
        if not series_number:
            series_number = Counter(dcm.bulk_get("SeriesNumber")).most_common()[0][0]

        return cls(series_number, modality, series_description, number)

    @classmethod
    def from_name(cls, other: "SeriesName"):
        return cls(
            other.series_number,
            other.modality,
            other.series_description,
            other.number,
            other.localizer,
        )

    def __repr__(self) -> str:
        s_num = "series-1"
        if self.series_number:
            s_num = f"series-{self.series_number}"
        mod = f"_{self.modality}" if self.modality else ""
        descr = f"_{self.series_description}" if self.series_description else ""
        num = f"_{self.number}" if self.number else ""
        name = s_num + mod + descr + num
        if self.localizer:
            name += "_localizer"
        return load_file_name(name)


def add_contributing_equipment(dcm: DICOMCollection) -> None:
    """Helper function to populate ContributingEquipmentSequence."""
    cont_dat = Dataset()
    cont_dat.Manufacturer = "Flywheel"
    cont_dat.ManufacturerModelName = pkg_name
    cont_dat.SoftwareVersions = ".".join(VERSION)

    for dcm_slice in dcm:
        raw = dcm_slice.dataset.raw
        if not raw.get("ContributingEquipmentSequence"):
            raw.ContributingEquipmentSequence = Sequence()
        raw.ContributingEquipmentSequence.append(cont_dat)


def update_modified_attributes_sequence(
    dcm: DICOMCollection,
    modified: t.Dict[str, t.Any],
    mod_system: str = "fw_gear_splitter",
    source: t.Optional[str] = None,
    reason: str = "COERCE",
) -> None:
    """Update modified attributes sequence for a collection.

    Args:
        dcm (DICOMCollection): Collection to modify
        modified (t.Dict[str, Any]): key and value pairs to set.
        mod_system (t.Optional[str], optional): System doing modification.
            Defaults to None.
        source (t.Optional[str], optional): Original source of data.
            Defaults to None.
        reason (str, optional): Reason for modifying, either 'COERCE',
            or 'CORRECT' in order to comply with dicom standard.
                Defaults to 'COERCE'.
    """
    # Modified attributes dataset
    mod_dat = Dataset()
    for key, value in modified.items():
        setattr(mod_dat, key, value)
    # Original attributes dataset
    orig_dat = Dataset()
    # Add Modified attributes dataset as a sequence
    orig_dat.ModifiedAttributesSequence = Sequence([mod_dat])
    if mod_system:
        orig_dat.ModifyingSystem = mod_system
    if source:
        orig_dat.SourceOfPreviousValues = source
    orig_dat.ReasonForTheAttributeModification = reason
    time_zone = get_localzone()
    curr_dt = time_zone.localize(datetime.datetime.now())
    curr_dt_str = curr_dt.strftime("%Y%m%d%H%M%S.%f%z")
    orig_dat.AttributeModificationDateTime = curr_dt_str

    for dcm_slice in dcm:
        # Append original attributes sequence dataset for each dicom
        #   in archive
        raw = dcm_slice.dataset.raw

        if not raw.get("OriginalAttributesSequence", None):
            raw.OriginalAttributesSequence = Sequence()
        raw.OriginalAttributesSequence.append(orig_dat)


def gen_series_uid(dcm: DICOMCollection) -> str:
    """Simple helper to generate and set uid."""
    uid = generate_uid()
    dcm.set("SeriesInstanceUID", uid)
    return uid


def populate_qc(context: GearToolkitContext, file_name: str) -> None:
    """Utility to populate splitter specific qc info on an output filename."""
    dicom = context.get_input("dicom")
    get_parent_fn = getattr(context.client, f"get_{dicom['hierarchy']['type']}")
    parent = get_parent_fn(dicom["hierarchy"]["id"])
    orig = parent.get_file(dicom["location"]["name"])

    original = {
        "original": {
            "filename": orig.name,
            "file_id": getattr(orig, "file_id", ""),
        }
    }

    info = add_qc_info(context, file_name, split=True, **original)
    context.update_file_metadata(file_name, info=info)


def populate_tags(
    context: GearToolkitContext,
    output_paths: t.Tuple,
    set_deleted: bool = False,
) -> None:
    """Utility to populate splitter specific tags on output files and input file."""

    tags = context.get_input("dicom")["object"]["tags"][:]  # copy
    tag = context.config.get("tag")
    if tag and tag not in tags:
        tags.append(tag)

    input_tags = tags[:]
    if set_deleted:
        input_tags.append("delete")

    # input file
    context.update_file_metadata(context.get_input_filename("dicom"), tags=input_tags)

    # output files
    for path in output_paths:
        file_ = Path(path).name
        context.update_file_metadata(file_, tags=tags)


def update_localizer_frames(
    dcm: DICOMCollection,
    orig_series_uid: t.Optional[str],
    orig_series_num: t.Optional[str],
) -> str:
    log.info(
        "Updating modified attributes sequence with original "
        + f"SeriesInstanceUID: {orig_series_uid}, "
        + f"original SeriesNumber: {orig_series_num}",
    )
    update_modified_attributes_sequence(
        dcm,
        modified={
            "SeriesInstanceUID": orig_series_uid,
            "SeriesNumber": orig_series_num,
        },
    )
    new_series_uid = gen_series_uid(dcm)
    new_series_num = int(orig_series_num or 1) + 1000
    dcm.set("SeriesNumber", new_series_num)
    log.info(
        f"Adding new SeriesInstanceUID: {new_series_uid}"
        + f", SeriesNumber: {new_series_num}"
    )
    return new_series_num
