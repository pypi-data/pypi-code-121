# ----------------------------------------------------------------------------
# Description    : Update file format utilities
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import tarfile
import zipfile
import json
import tempfile
import re
import os
import copy
from typing import Optional, BinaryIO, Callable
from qblox_instruments.cfg_man.probe import ConnectionInfo
from qblox_instruments.cfg_man.const import VERSION
from qblox_instruments.build import DeviceInfo
import qblox_instruments.cfg_man.log as log


# ----------------------------------------------------------------------------

class UpdateFile:
    """
    Representation of a device update file.
    """

    __slots__ = [
        "_fname",
        "_update_fname",
        "_tempdir",
        "_format",
        "_models",
        "_metadata",
    ]

    # ------------------------------------------------------------------------
    def __init__(self, fname: str, check_version: bool = True):
        """
        Loads an update file.

        Parameters
        ----------
        fname: str
            The file to load.
        check_version: bool
            Whether to throw a NotImplementedError if the minimum
            configuration management client version reported by the update
            file is newer than our client version.
        """
        super().__init__()

        # Save filename.
        self._fname = fname

        # Be lenient: if the user downloaded a release file and forgot to
        # extract it, extract it for them transparently.
        self._update_fname = None
        self._tempdir = None

        def extract(fin):
            log.debug(
                '"%s" looks like a release file, extracting update.tar.gz from it...',
                self._fname,
            )
            self._tempdir = tempfile.TemporaryDirectory()
            self._update_fname = os.path.join(
                self._tempdir.__enter__(),
                "update.tar.gz"
            )
            with open(self._update_fname, "wb") as fout:
                while True:
                    buf = fin.read(4096)
                    if not buf:
                        break
                    while buf:
                        buf = buf[fout.write(buf):]

        try:
            log.debug('Determining file type of "%s"...', self._fname)
            with tarfile.TarFile.open(self._fname, "r:*") as tar:
                for name in tar.getnames():
                    if name.endswith("update.tar.gz"):
                        with tar.extractfile(name) as fin:
                            extract(fin)
                        break
                else:
                    log.debug(
                        '"%s" looks like it might indeed be an update file.',
                        self._fname,
                    )
                    self._update_fname = self._fname
        except tarfile.TarError:
            try:
                with zipfile.ZipFile(self._fname, "r") as zip:
                    for name in zip.namelist():
                        if name.endswith("update.tar.gz"):
                            with zip.open(name, "r") as fin:
                                extract(fin)
                            break
            except zipfile.BadZipFile:
                pass
        if self._update_fname is None:
            raise ValueError("invalid update file")

        # Read the tar file.
        try:
            log.debug('Scanning update tar file "%s"...', self._update_fname)
            with tarfile.TarFile.open(self._update_fname, "r:gz") as tar:
                fmts = set()
                meta_json = None
                models = set()
                metadata = {}
                while True:
                    info = tar.next()
                    if info is None:
                        break
                    name = info.name
                    log.debug("  %s", name)
                    if name.startswith("."):
                        name = name[1:]
                    if name.startswith("/") or name.startswith("\\"):
                        name = name[1:]
                    name, *tail = re.split(r"/|\\", name, maxsplit=1)
                    if name == "meta.json" and not tail:
                        fmts.add("multi")
                        meta_json = info
                    elif name.startswith("only_"):
                        name = name[5:]
                        if name not in models:
                            fmts.add("multi")
                            metadata[name] = {
                                "manufacturer": "qblox",
                                "model": name
                            }
                            models.add(name)
                    elif name == "common":
                        fmts.add("multi")
                    else:
                        if name not in models:
                            fmts.add("legacy")
                            metadata[name] = {
                                "manufacturer": "qblox",
                                "model": name
                            }
                            models.add(name)
                log.debug("Scan complete")
                log.debug("")
                if meta_json is not None:
                    with tar.extractfile(meta_json) as f:
                        metadata.update(json.loads(f.read()))
                if len(fmts) != 1:
                    raise ValueError("invalid update file")
                self._format = next(iter(fmts))
                self._models = {
                    model: DeviceInfo.from_dict(metadata[model])
                    for model in sorted(models)
                }
                self._metadata = metadata.get("meta", {})
        except tarfile.TarError:
            raise ValueError("invalid update file")

        # Check client version.
        if check_version:
            if self._metadata.get("meta", {}).get("min_cfg_man_client", (0, 0, 0)) > VERSION:
                raise NotImplementedError(
                    "update file format is too new. Please update Qblox Instruments first"
                )

    # ------------------------------------------------------------------------
    def close(self):
        """
        Cleans up any operating resources that we may have claimed.

        Parameters
        ----------

        Returns
        -------
        """
        if hasattr(self, "_tempdir") and self._tempdir is not None:
            self._tempdir.cleanup()
            self._tempdir = None

    # ------------------------------------------------------------------------
    def __del__(self):
        self.close()

    # ------------------------------------------------------------------------
    def __enter__(self):
        return self

    # ------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        self.close()

    # ------------------------------------------------------------------------
    def needs_confirmation(self) -> Optional[str]:
        """
        Returns whether the update file requests the user to confirm something
        before application, and if so, what message should be printed.

        Parameters
        ----------

        Returns
        -------
        Optional[str]
            None if there is nothing exceptional about this file, otherwise
            this is the confirmation message.
        """
        return self._metadata.get("confirm", None)

    # ------------------------------------------------------------------------
    def __str__(self):
        return self._fname

    # ------------------------------------------------------------------------
    def __repr__(self):
        return repr(self._fname)

    # ------------------------------------------------------------------------
    def summarize(self) -> str:
        """
        Returns a summary of the update file format.

        Parameters
        ----------

        Returns
        -------
        str
            Update file summary.
        """
        if self._format == "legacy":
            return "legacy update file for {}".format(next(iter(self._models)))
        return "update file for {}".format(", ".join(self._models))

    # ------------------------------------------------------------------------
    def pprint(self, output: Callable[[str], None]=log.info) -> None:
        """
        Pretty-prints the update file metadata.

        Parameters
        ----------
        output: Callable[[str], None]
            The function used for printing. Each call represents a line.

        Returns
        -------
        """
        min_client = self._metadata.get("min_cfg_man_client", None)
        if min_client is not None:
            if self._format != "legacy":
                min_client = (0, 2, 0)
            min_client = ".".join(map(str, min_client))

        query_message = self._metadata.get("confirm", "None")

        output("Update file              : {}".format(self._fname))
        output("File format              : {}".format(self._format))
        output("Minimum client version   : {}".format(min_client))
        output("Query message            : {}".format(query_message))
        output("Contains updates for     : {} product(s)".format(len(self._models)))
        for model, di in self._models.items():
            output("  Model                  : {}".format(model))
            for key, pretty in (
                ("sw", "Application"),
                ("fw", "FPGA firmware"),
                ("kmod", "Kernel module"),
                ("cfg_man", "Cfg. manager"),
            ):
                try:
                    output("    {:<21}: {}".format(pretty + " version", di[key])),
                except KeyError:
                    continue

    # ------------------------------------------------------------------------
    def load(self, ci: ConnectionInfo) -> BinaryIO:
        """
        Loads an update file, checking whether the given update file is
        compatible within the given connection context. Returns a file-like
        object opened in binary read mode if compatible, or throws a
        ValueError if there is a problem.

        Parameters
        ----------
        ci: ConnectionInfo
            Connection information object retrieved from autoconf(), to verify
            that the update file is compatible, or to make it compatible, if
            possible.

        Returns
        -------
        BinaryIO
            Binary file-like object for the update file. Will at least be
            opened for reading, and rewound to the start of the file. This may
            effectively be ``open(fname, "rb")``, but could also be a
            ``tempfile.TemporaryFile`` to an update file specifically
            converted to be compatible with the given environment. It is the
            responsibility of the caller to close the file.

        Raises
        ------
        ValueError
            If there is a problem with the given update file.
        """

        # Check whether the update includes data for all the devices we need to
        # support.
        for model in ci.all_models:
            if model not in self._models:
                raise ValueError(
                    "update file is not compatible with {} devices".format(model)
                )

        # If we're connected to the server via the legacy update protocol, we
        # must also supply a legacy update file. So if this is not already in
        # the legacy format, we have to downconvert the file format.
        if ci.protocol == "legacy" and self._format != "legacy":
            if len(ci.all_models) != 1:
                raise ValueError(
                    "cannot update multiple devices at once with legacy configuration managers"
                )
            log.info(
                "Converting multi-device update to legacy update file for %s...",
                ci.device.model,
            )
            with tarfile.open(self._update_fname, "r:gz") as tar:
                common = {}
                specific = {}
                infos = []
                log.debug("Scanning input tar file...")
                while True:
                    info = tar.next()
                    if info is None:
                        break
                    log.debug("  %s", info.name)
                    infos.append(info)
                for info in infos:

                    # Split filename into the name of the root directory of the
                    # tar file and the corresponding root path on the device.
                    name = info.name
                    if name.startswith("."):
                        name = name[1:]
                    if name.startswith("/") or name.startswith("\\"):
                        name = name[1:]
                    tar_dir, *root_path = re.split(r"[\\/]", name, maxsplit=1)
                    if root_path:
                        root_path = "/" + root_path[0]
                    else:
                        root_path = "/"

                    # Save the info blocks for the files relevant to us.
                    if tar_dir == "only_" + ci.device.model:
                        specific[root_path] = info
                    elif tar_dir == "common":
                        common[root_path] = info

                # Device-specific files override common files.
                files = common
                files.update(specific)

                # Create a new tar.gz file with the files for this device
                # specifically.
                log.debug("Recompressing in legacy format...")
                file_obj = tempfile.TemporaryFile("w+b")
                try:
                    with tarfile.open(None, "w:gz", file_obj) as tar_out:
                        for idx, (path, info) in enumerate(sorted(files.items())):
                            log.progress(
                                idx / len(files),
                                "Recompressing update archive in legacy format...",
                            )

                            # Determine the path in the new tarfile.
                            out_info = copy.copy(info)
                            if path == "/":
                                out_info.name = "./{}".format(ci.device.model)
                            else:
                                out_info.name = "./{}{}".format(ci.device.model, path)

                            log.debug("  %s", out_info.name)
                            tar_out.addfile(out_info, tar.extractfile(info))
                finally:
                    log.clear_progress()

                log.debug("Legacy update file complete")
                log.debug("")

                # Rewind back to the start of the file to comply with
                # postconditions.
                file_obj.seek(0)

                return file_obj

        # No need to change the contents of the update file, so just open the
        # file as-is.
        return open(self._update_fname, "rb")
