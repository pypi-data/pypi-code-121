


"""
The Kolibri corpus and module downloader is inspired from Kolibri downloader.  This module defines several
interfaces which can be used to download corpora, models, and other
data packages that can be used with Kolibri.

Downloading Packages
====================
If called with no arguments, ``download()`` will display an interactive
interface which can be used to download and install new packages.
If Tkinter is available, then a graphical interface will be shown,
otherwise a simple text interface will be provided.
"""


import functools
import itertools
import json
import os
import kolibri
import subprocess
import sys
import textwrap
import threading
import time
import warnings
import zipfile
from hashlib import md5
from kdmt.path import is_writable
from kolibri.settings import DATA_PATH

from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# urllib2 = nltk.internals.import_from_stdlib('urllib2')


######################################################################
# Directory entry objects (from the data server's index file)
######################################################################


class Resource:
    """
    A directory entry for a downloadable package.
    """

    def __init__(
        self,
        package_id,
        url,
        name=None,
        subdir="",
        size=None,
        unzipped_size=None,
        checksum=None,
        git_revision=None,
        copyright="Unknown",
        contact="Unknown",
        license="Unknown",
        author="Unknown",
        unzip=True,
        **kw,
    ):
        self.id = package_id
        """A unique identifier for this package."""

        self.name = name or package_id
        """A string name for this package."""

        self.subdir = subdir
        """The subdirectory where this package should be installed.
           E.g., ``'corpora'`` or ``'taggers'``."""

        self.url = url
        """A URL that can be used to download this package's file."""

        self.size = int(size)
        """The filesize (in bytes) of the package file."""

        self.unzipped_size = int(unzipped_size)
        """The total filesize of the files contained in the package's
           zipfile."""

        self.checksum = checksum
        """The MD-5 checksum of the package file."""

        self.svn_revision = git_revision
        """A subversion revision number for this package."""

        self.copyright = copyright
        """Copyright holder for this package."""

        self.contact = contact
        """Name & email of the person who should be contacted with
           questions about this package."""

        self.license = license
        """License information for this package."""

        self.author = author
        """Author of this package."""

        ext = os.path.splitext(url.split("/")[-1])[1]
        self.filename = os.path.join(subdir, id + ext)
        """The filename that should be used for this package's file.  It
           is formed by joining ``self.subdir`` with ``self.id``, and
           using the same extension as ``url``."""

        self.unzip = bool(int(unzip))  # '0' or '1'
        """A flag indicating whether this corpus should be unzipped by
           default."""

        # Include any other attributes provided by the XML file.
        self.__dict__.update(kw)

    @staticmethod
    def fromjson(json_dict):

        for key in json_dict:
            json_dict[key] = str(json_dict[key])
        return Resource(**json_dict)

    def __lt__(self, other):
        return self.id < other.id

    def __repr__(self):
        return "<Package %s>" % self.id


class Resources:
    """
    A directory entry for a collection of downloadable packages.
    These entries are extracted from the XML index file that is
    downloaded by ``Downloader``.
    """

    def __init__(self, id, children, name=None, **kw):
        self.id = id
        """A unique identifier for this collection."""

        self.name = name or id
        """A string name for this collection."""

        self.children = children
        """A list of the ``Collections`` or ``Packages`` directly
           contained by this collection."""

        self.packages = None
        """A list of ``Packages`` contained by this collection or any
           collections it recursively contains."""

        # Include any other attributes provided by the XML file.
        self.__dict__.update(kw)

    @staticmethod
    def fromjson(json_dict):

        for key in json_dict.attrib:
            json_dict[key] = str(json_dict[key])
        children = [child.get("ref") for child in json_dict.findall("item")]
        return Resources(children=children, **json_dict.attrib)

    def __lt__(self, other):
        return self.id < other.id

    def __repr__(self):
        return "<Collection %s>" % self.id


######################################################################
# Message Passing Objects
######################################################################


class DownloaderMessage:
    """A status message object, used by ``incr_download`` to
    communicate its progress."""


class StartCollectionMessage(DownloaderMessage):
    """Data server has started working on a collection of packages."""

    def __init__(self, collection):
        self.collection = collection


class FinishCollectionMessage(DownloaderMessage):
    """Data server has finished working on a collection of packages."""

    def __init__(self, collection):
        self.collection = collection


class StartPackageMessage(DownloaderMessage):
    """Data server has started working on a package."""

    def __init__(self, package):
        self.package = package


class FinishPackageMessage(DownloaderMessage):
    """Data server has finished working on a package."""

    def __init__(self, package):
        self.package = package


class StartDownloadMessage(DownloaderMessage):
    """Data server has started downloading a package."""

    def __init__(self, package):
        self.package = package


class FinishDownloadMessage(DownloaderMessage):
    """Data server has finished downloading a package."""

    def __init__(self, package):
        self.package = package


class StartUnzipMessage(DownloaderMessage):
    """Data server has started unzipping a package."""

    def __init__(self, package):
        self.package = package


class FinishUnzipMessage(DownloaderMessage):
    """Data server has finished unzipping a package."""

    def __init__(self, package):
        self.package = package


class UpToDateMessage(DownloaderMessage):
    """The package download file is already up-to-date"""

    def __init__(self, package):
        self.package = package


class StaleMessage(DownloaderMessage):
    """The package download file is out-of-date or corrupt"""

    def __init__(self, package):
        self.package = package


class ErrorMessage(DownloaderMessage):
    """Data server encountered an error"""

    def __init__(self, package, message):
        self.package = package
        if isinstance(message, Exception):
            self.message = str(message)
        else:
            self.message = message


class ProgressMessage(DownloaderMessage):
    """Indicates how much progress the data server has made"""

    def __init__(self, progress):
        self.progress = progress


class SelectDownloadDirMessage(DownloaderMessage):
    """Indicates what download directory the data server is using"""

    def __init__(self, download_dir):
        self.download_dir = download_dir


######################################################################
# Kolibri Data Server
######################################################################


class Downloader:
    """
    A class used to access the Kolibri data server, which can be used to
    download corpora and other data packages.
    """

    # /////////////////////////////////////////////////////////////////
    # Configuration
    # /////////////////////////////////////////////////////////////////

    INDEX_TIMEOUT = 60 * 60  # 1 hour
    """The amount of time after which the cached copy of the data
       server index will be considered 'stale,' and will be
       re-downloaded."""

    DEFAULT_URL = "https://raw.githubusercontent.com/mbenhaddou/kolibri-data/main/index.json"
    """The default URL for the Kolibri data server's index.  An
       alternative URL can be specified when creating a new
       ``Downloader`` object."""

    # /////////////////////////////////////////////////////////////////
    # Status Constants
    # /////////////////////////////////////////////////////////////////

    INSTALLED = "installed"
    """A status string indicating that a package or collection is
       installed and up-to-date."""
    NOT_INSTALLED = "not installed"
    """A status string indicating that a package or collection is
       not installed."""
    STALE = "out of date"
    """A status string indicating that a package or collection is
       corrupt or out-of-date."""
    PARTIAL = "partial"
    """A status string indicating that a collection is partially
       installed (i.e., only some of its packages are installed.)"""

    # /////////////////////////////////////////////////////////////////
    # Constructor
    # /////////////////////////////////////////////////////////////////

    def __init__(self, server_index_url=None, download_dir=None):
        self._url = server_index_url or self.DEFAULT_URL
        """The URL for the data server's index file."""

        self._packages = {}
        """Dictionary from package identifier to ``Package``"""

        self._download_dir = download_dir
        """The default directory to which packages will be downloaded."""

        self._index = None
        """The XML index file downloaded from the data server"""

        self._index_timestamp = None
        """Time at which ``self._index`` was downloaded.  If it is more
           than ``INDEX_TIMEOUT`` seconds old, it will be re-downloaded."""

        self._status_cache = {}
        """Dictionary from package/collection identifier to status
           string (``INSTALLED``, ``NOT_INSTALLED``, ``STALE``, or
           ``PARTIAL``).  Cache is used for packages only, not
           collections."""

        self._errors = None
        """Flag for telling if all packages got successfully downloaded or not."""

        # decide where we're going to save things to.
        if self._download_dir is None:
            self._download_dir = self.default_download_dir()

    # /////////////////////////////////////////////////////////////////
    # Information
    # /////////////////////////////////////////////////////////////////

    def list(
        self,
        download_dir=None,
        show_packages=True,
        show_collections=True,
        header=True,
        more_prompt=False,
        skip_installed=False,
    ):
        lines = 0  # for more_prompt
        if download_dir is None:
            download_dir = self._download_dir
            print("Using default data directory (%s)" % download_dir)
        if header:
            print("=" * (26 + len(self._url)))
            print(" Data server index for <%s>" % self._url)
            print("=" * (26 + len(self._url)))
            lines += 3  # for more_prompt
        stale = partial = False

        categories = []
        if show_packages:
            categories.append("packages")
        if show_collections:
            categories.append("collections")
        for category in categories:
            print("%s:" % category.capitalize())
            lines += 1  # for more_prompt
            for info in sorted(getattr(self, category)(), key=str):
                status = self.status(info, download_dir)
                if status == self.INSTALLED and skip_installed:
                    continue
                if status == self.STALE:
                    stale = True
                if status == self.PARTIAL:
                    partial = True
                prefix = {
                    self.INSTALLED: "*",
                    self.STALE: "-",
                    self.PARTIAL: "P",
                    self.NOT_INSTALLED: " ",
                }[status]
                name = textwrap.fill(
                    "-" * 27 + (info.name or info.id), 75, subsequent_indent=27 * " "
                )[27:]
                print("  [{}] {} {}".format(prefix, info.id.ljust(20, "."), name))
                lines += len(name.split("\n"))  # for more_prompt
                if more_prompt and lines > 20:
                    user_input = input("Hit Enter to continue: ")
                    if user_input.lower() in ("x", "q"):
                        return
                    lines = 0
            print()
        msg = "([*] marks installed packages"
        if stale:
            msg += "; [-] marks out-of-date or corrupt packages"
        if partial:
            msg += "; [P] marks partially installed collections"
        print(textwrap.fill(msg + ")", subsequent_indent=" ", width=76))

    def packages(self):
        self._update_index()
        return self._packages.values()

    def corpora(self):
        self._update_index()
        return [pkg for (id, pkg) in self._packages.items() if pkg.subdir == "corpora"]

    def models(self):
        self._update_index()
        return [pkg for (id, pkg) in self._packages.items() if pkg.subdir != "corpora"]

    def collections(self):
        self._update_index()
        return self._collections.values()

    # /////////////////////////////////////////////////////////////////
    # Downloading
    # /////////////////////////////////////////////////////////////////

    def _info_or_id(self, info_or_id):
        if isinstance(info_or_id, str):
            return self.info(info_or_id)
        else:
            return info_or_id

    # [xx] When during downloading is it 'safe' to abort?  Only unsafe
    # time is *during* an unzip -- we don't want to leave a
    # partially-unzipped corpus in place because we wouldn't notice
    # it.  But if we had the exact total size of the unzipped corpus,
    # then that would be fine.  Then we could abort anytime we want!
    # So this is really what we should do.  That way the threaded
    # downloader in the gui can just kill the download thread anytime
    # it wants.

    def incr_download(self, info_or_id, download_dir=None, force=False):
        # If they didn't specify a download_dir, then use the default one.
        if download_dir is None:
            download_dir = self._download_dir
            yield SelectDownloadDirMessage(download_dir)

        # If they gave us a list of ids, then download each one.
        if isinstance(info_or_id, (list, tuple)):
            yield from self._download_list(info_or_id, download_dir, force)
            return

        # Look up the requested collection or package.
        try:
            info = self._info_or_id(info_or_id)
        except (OSError, ValueError) as e:
            yield ErrorMessage(None, f"Error loading {info_or_id}: {e}")
            return

        # Handle collections.
        if isinstance(info, Resources):
            yield StartCollectionMessage(info)
            yield from self.incr_download(info.children, download_dir, force)
            yield FinishCollectionMessage(info)

        # Handle Packages (delegate to a helper function).
        else:
            yield from self._download_package(info, download_dir, force)

    def _num_packages(self, item):
        if isinstance(item, Resource):
            return 1
        else:
            return len(item.packages)

    def _download_list(self, items, download_dir, force):
        # Look up the requested items.
        for i in range(len(items)):
            try:
                items[i] = self._info_or_id(items[i])
            except (OSError, ValueError) as e:
                yield ErrorMessage(items[i], e)
                return

        # Download each item, re-scaling their progress.
        num_packages = sum(self._num_packages(item) for item in items)
        progress = 0
        for i, item in enumerate(items):
            if isinstance(item, Resource):
                delta = 1.0 / num_packages
            else:
                delta = len(item.packages) / num_packages
            for msg in self.incr_download(item, download_dir, force):
                if isinstance(msg, ProgressMessage):
                    yield ProgressMessage(progress + msg.progress * delta)
                else:
                    yield msg

            progress += 100 * delta

    def _download_package(self, info, download_dir, force):
        yield StartPackageMessage(info)
        yield ProgressMessage(0)

        # Do we already have the current version?
        status = self.status(info, download_dir)
        if not force and status == self.INSTALLED:
            yield UpToDateMessage(info)
            yield ProgressMessage(100)
            yield FinishPackageMessage(info)
            return

        # Remove the package from our status cache
        self._status_cache.pop(info.id, None)

        # Check for (and remove) any old/stale version.
        filepath = os.path.join(download_dir, info.filename)
        if os.path.exists(filepath):
            if status == self.STALE:
                yield StaleMessage(info)
            os.remove(filepath)

        # Ensure the download_dir exists
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        if not os.path.exists(os.path.join(download_dir, info.subdir)):
            os.makedirs(os.path.join(download_dir, info.subdir))

        # Download the file.  This will raise an IOError if the url
        # is not found.
        yield StartDownloadMessage(info)
        yield ProgressMessage(5)
        try:
            infile = urlopen(info.url)
            with open(filepath, "wb") as outfile:
                num_blocks = max(1, info.size / (1024 * 16))
                for block in itertools.count():
                    s = infile.read(1024 * 16)  # 16k blocks.
                    outfile.write(s)
                    if not s:
                        break
                    if block % 2 == 0:  # how often?
                        yield ProgressMessage(min(80, 5 + 75 * (block / num_blocks)))
            infile.close()
        except OSError as e:
            yield ErrorMessage(
                info,
                "Error downloading %r from <%s>:" "\n  %s" % (info.id, info.url, e),
            )
            return
        yield FinishDownloadMessage(info)
        yield ProgressMessage(80)

        # If it's a zipfile, uncompress it.
        if info.filename.endswith(".zip"):
            zipdir = os.path.join(download_dir, info.subdir)
            # Unzip if we're unzipping by default; *or* if it's already
            # been unzipped (presumably a previous version).
            if info.unzip or os.path.exists(os.path.join(zipdir, info.id)):
                yield StartUnzipMessage(info)
                for msg in _unzip_iter(filepath, zipdir, verbose=False):
                    # Somewhat of a hack, but we need a proper package reference
                    msg.package = info
                    yield msg
                yield FinishUnzipMessage(info)

        yield FinishPackageMessage(info)

    def download(
        self,
        info_or_id=None,
        download_dir=None,
        quiet=False,
        force=False,
        prefix="[nltk_data] ",
        halt_on_error=True,
        raise_on_error=False,
        print_error_to=sys.stderr,
    ):

        print_to = functools.partial(print, file=print_error_to)
        # If no info or id is given, then use the interactive shell.
        if info_or_id is None:
            # [xx] hmm -- changing self._download_dir here seems like
            # the wrong thing to do.  Maybe the _interactive_download
            # function should make a new copy of self to use?
            if download_dir is not None:
                self._download_dir = download_dir
            self._interactive_download()
            return True

        else:
            # Define a helper function for displaying output:
            def show(s, prefix2=""):
                print_to(
                    textwrap.fill(
                        s,
                        initial_indent=prefix + prefix2,
                        subsequent_indent=prefix + prefix2 + " " * 4,
                    )
                )

            for msg in self.incr_download(info_or_id, download_dir, force):
                # Error messages
                if isinstance(msg, ErrorMessage):
                    show(msg.message)
                    if raise_on_error:
                        raise ValueError(msg.message)
                    if halt_on_error:
                        return False
                    self._errors = True
                    if not quiet:
                        print_to("Error installing package. Retry? [n/y/e]")
                        choice = input().strip()
                        if choice in ["y", "Y"]:
                            if not self.download(
                                msg.package.id,
                                download_dir,
                                quiet,
                                force,
                                prefix,
                                halt_on_error,
                                raise_on_error,
                            ):
                                return False
                        elif choice in ["e", "E"]:
                            return False

                # All other messages
                if not quiet:
                    # Collection downloading messages:
                    if isinstance(msg, StartCollectionMessage):
                        show("Downloading collection %r" % msg.collection.id)
                        prefix += "   | "
                        print_to(prefix)
                    elif isinstance(msg, FinishCollectionMessage):
                        print_to(prefix)
                        prefix = prefix[:-4]
                        if self._errors:
                            show(
                                "Downloaded collection %r with errors"
                                % msg.collection.id
                            )
                        else:
                            show("Done downloading collection %s" % msg.collection.id)

                    # Package downloading messages:
                    elif isinstance(msg, StartPackageMessage):
                        show(
                            "Downloading package %s to %s..."
                            % (msg.package.id, download_dir)
                        )
                    elif isinstance(msg, UpToDateMessage):
                        show("Package %s is already up-to-date!" % msg.package.id, "  ")
                    # elif isinstance(msg, StaleMessage):
                    #    show('Package %s is out-of-date or corrupt' %
                    #         msg.package.id, '  ')
                    elif isinstance(msg, StartUnzipMessage):
                        show("Unzipping %s." % msg.package.filename, "  ")

                    # Data directory message:
                    elif isinstance(msg, SelectDownloadDirMessage):
                        download_dir = msg.download_dir
        return True

    def is_stale(self, info_or_id, download_dir=None):
        return self.status(info_or_id, download_dir) == self.STALE

    def is_installed(self, info_or_id, download_dir=None):
        return self.status(info_or_id, download_dir) == self.INSTALLED

    def clear_status_cache(self, id=None):
        if id is None:
            self._status_cache.clear()
        else:
            self._status_cache.pop(id, None)

    def status(self, info_or_id, download_dir=None):
        """
        Return a constant describing the status of the given package
        or collection.  Status can be one of ``INSTALLED``,
        ``NOT_INSTALLED``, ``STALE``, or ``PARTIAL``.
        """
        if download_dir is None:
            download_dir = self._download_dir
        info = self._info_or_id(info_or_id)

        # Handle collections:
        if isinstance(info, Resources):
            pkg_status = [self.status(pkg.id) for pkg in info.packages]
            if self.STALE in pkg_status:
                return self.STALE
            elif self.PARTIAL in pkg_status:
                return self.PARTIAL
            elif self.INSTALLED in pkg_status and self.NOT_INSTALLED in pkg_status:
                return self.PARTIAL
            elif self.NOT_INSTALLED in pkg_status:
                return self.NOT_INSTALLED
            else:
                return self.INSTALLED

        # Handle packages:
        else:
            filepath = os.path.join(download_dir, info.filename)
            if download_dir != self._download_dir:
                return self._pkg_status(info, filepath)
            else:
                if info.id not in self._status_cache:
                    self._status_cache[info.id] = self._pkg_status(info, filepath)
                return self._status_cache[info.id]

    def _pkg_status(self, info, filepath):
        if not os.path.exists(filepath):
            return self.NOT_INSTALLED

        # Check if the file has the correct size.
        try:
            filestat = os.stat(filepath)
        except OSError:
            return self.NOT_INSTALLED
        if filestat.st_size != int(info.size):
            return self.STALE

        # Check if the file's checksum matches
        if md5_hexdigest(filepath) != info.checksum:
            return self.STALE

        # If it's a zipfile, and it's been at least partially
        # unzipped, then check if it's been fully unzipped.
        if filepath.endswith(".zip"):
            unzipdir = filepath[:-4]
            if not os.path.exists(unzipdir):
                return self.INSTALLED  # but not unzipped -- ok!
            if not os.path.isdir(unzipdir):
                return self.STALE

            unzipped_size = sum(
                os.stat(os.path.join(d, f)).st_size
                for d, _, files in os.walk(unzipdir)
                for f in files
            )
            if unzipped_size != info.unzipped_size:
                return self.STALE

        # Otherwise, everything looks good.
        return self.INSTALLED

    def update(self, quiet=False, prefix="[nltk_data] "):
        """
        Re-download any packages whose status is STALE.
        """
        self.clear_status_cache()
        for pkg in self.packages():
            if self.status(pkg) == self.STALE:
                self.download(pkg, quiet=quiet, prefix=prefix)

    # /////////////////////////////////////////////////////////////////
    # Index
    # /////////////////////////////////////////////////////////////////

    def _update_index(self, url=None):
        """A helper function that ensures that self._index is
        up-to-date.  If the index is older than self.INDEX_TIMEOUT,
        then download it again."""
        # Check if the index is already up-to-date.  If so, do nothing.
        if not (
            self._index is None
            or url is not None
            or time.time() - self._index_timestamp > self.INDEX_TIMEOUT
        ):
            return

        # If a URL was specified, then update our URL.
        self._url = url or self._url

        # Download the index file.
        self._index = json.loads(urlopen(self._url).read().decode())
        self._index_timestamp = time.time()

        # Build a dictionary of packages.
        packages = [Resource.fromjson(p) for p in self._index["kolibri_data"]["packages"]]
        self._packages = {p.id: p for p in packages}

        # Flush the status cache
        self._status_cache.clear()

    def index(self):
        """
        Return the XML index describing the packages available from
        the data server.  If necessary, this index will be downloaded
        from the data server.
        """
        self._update_index()
        return self._index

    def info(self, id):
        """Return the ``Package`` or ``Collection`` record for the
        given item."""
        self._update_index()
        if id in self._packages:
            return self._packages[id]
        if id in self._collections:
            return self._collections[id]
        raise ValueError("Package %r not found in index" % id)

    def xmlinfo(self, id):
        """Return the XML info record for the given item"""
        self._update_index()
        for package in self._index.findall("packages/package"):
            if package.get("id") == id:
                return package
        for collection in self._index.findall("collections/collection"):
            if collection.get("id") == id:
                return collection
        raise ValueError("Package %r not found in index" % id)

    # /////////////////////////////////////////////////////////////////
    # URL & Data Directory
    # /////////////////////////////////////////////////////////////////

    def _get_url(self):
        """The URL for the data server's index file."""
        return self._url

    def _set_url(self, url):
        """
        Set a new URL for the data server. If we're unable to contact
        the given url, then the original url is kept.
        """
        original_url = self._url
        try:
            self._update_index(url)
        except:
            self._url = original_url
            raise

    url = property(_get_url, _set_url)

    def default_download_dir(self):
        """
        Return the directory to which packages will be downloaded by
        default.  This value can be overridden using the constructor,
        or on a case-by-case basis using the ``download_dir`` argument when
        calling ``download()``.

        On Windows, the default download directory is
        ``PYTHONHOME/lib/nltk``, where *PYTHONHOME* is the
        directory containing Python, e.g. ``C:\\Python25``.

        On all other platforms, the default directory is the first of
        the following which exists or which can be created with write
        permission: ``/usr/share/nltk_data``, ``/usr/local/share/nltk_data``,
        ``/usr/lib/nltk_data``, ``/usr/local/lib/nltk_data``, ``~/nltk_data``.
        """
        # Check if we are on GAE where we cannot write into filesystem.
        if "APPENGINE_RUNTIME" in os.environ:
            return

        # Check if we have sufficient permissions to install in a
        # variety of system-wide locations.
        for kolibridir in kolibri.data.path:
            if os.path.exists(kolibridir) and is_writable(kolibridir):
                return kolibridir

        # On Windows, use %APPDATA%
        if sys.platform == "win32" and "APPDATA" in os.environ:
            homedir = os.environ["APPDATA"]

        # Otherwise, install in the user's home directory.
        else:
            homedir = os.path.expanduser("~/")
            if homedir == "~/":
                raise ValueError("Could not find a default download directory")

        # append ".kolibri" to the home directory
        return os.path.join(homedir, ".kolibri")

    def _get_download_dir(self):
        """
        The default directory to which packages will be downloaded.
        This defaults to the value returned by ``default_download_dir()``.
        To override this default on a case-by-case basis, use the
        ``download_dir`` argument when calling ``download()``.
        """
        return self._download_dir

    def _set_download_dir(self, download_dir):
        self._download_dir = download_dir
        # Clear the status cache.
        self._status_cache.clear()

    download_dir = property(_get_download_dir, _set_download_dir)

    # /////////////////////////////////////////////////////////////////
    # Interactive Shell
    # /////////////////////////////////////////////////////////////////

    def _interactive_download(self):
        # Try the GUI first; if that doesn't work, try the simple
        # interactive shell.
        DownloaderShell(self).run()


class DownloaderShell:
    def __init__(self, dataserver):
        self._ds = dataserver

    def _simple_interactive_menu(self, *options):
        print("-" * 75)
        spc = (68 - sum(len(o) for o in options)) // (len(options) - 1) * " "
        print("    " + spc.join(options))
        print("-" * 75)

    def run(self):
        print("Kolibri Downloader")
        while True:
            self._simple_interactive_menu(
                "d) Download",
                "l) List",
                " u) Update",
                "c) Config",
                "h) Help",
                "q) Quit",
            )
            user_input = input("Downloader> ").strip()
            if not user_input:
                print()
                continue
            command = user_input.lower().split()[0]
            args = user_input.split()[1:]
            try:
                if command == "l":
                    print()
                    self._ds.list(self._ds.download_dir, header=False, more_prompt=True)
                elif command == "h":
                    self._simple_interactive_help()
                elif command == "c":
                    self._simple_interactive_config()
                elif command in ("q", "x"):
                    return
                elif command == "d":
                    self._simple_interactive_download(args)
                elif command == "u":
                    self._simple_interactive_update()
                else:
                    print("Command %r unrecognized" % user_input)
            except HTTPError as e:
                print("Error reading from server: %s" % e)
            except URLError as e:
                print("Error connecting to server: %s" % e.reason)
            # try checking if user_input is a package name, &
            # downloading it?
            print()

    def _simple_interactive_download(self, args):
        if args:
            for arg in args:
                try:
                    self._ds.download(arg, prefix="    ")
                except (OSError, ValueError) as e:
                    print(e)
        else:
            while True:
                print()
                print("Download which package (l=list; x=cancel)?")
                user_input = input("  Identifier> ")
                if user_input.lower() == "l":
                    self._ds.list(
                        self._ds.download_dir,
                        header=False,
                        more_prompt=True,
                        skip_installed=True,
                    )
                    continue
                elif user_input.lower() in ("x", "q", ""):
                    return
                elif user_input:
                    for id in user_input.split():
                        try:
                            self._ds.download(id, prefix="    ")
                        except (OSError, ValueError) as e:
                            print(e)
                    break

    def _simple_interactive_update(self):
        while True:
            stale_packages = []
            stale = partial = False
            for info in sorted(getattr(self._ds, "packages")(), key=str):
                if self._ds.status(info) == self._ds.STALE:
                    stale_packages.append((info.id, info.name))

            print()
            if stale_packages:
                print("Will update following packages (o=ok; x=cancel)")
                for pid, pname in stale_packages:
                    name = textwrap.fill(
                        "-" * 27 + (pname), 75, subsequent_indent=27 * " "
                    )[27:]
                    print("  [ ] {} {}".format(pid.ljust(20, "."), name))
                print()

                user_input = input("  Identifier> ")
                if user_input.lower() == "o":
                    for pid, pname in stale_packages:
                        try:
                            self._ds.download(pid, prefix="    ")
                        except (OSError, ValueError) as e:
                            print(e)
                    break
                elif user_input.lower() in ("x", "q", ""):
                    return
            else:
                print("Nothing to update.")
                return

    def _simple_interactive_help(self):
        print()
        print("Commands:")
        print(
            "  d) Download a package or collection     u) Update out of date packages"
        )
        print("  l) List packages & collections          h) Help")
        print("  c) View & Modify Configuration          q) Quit")

    def _show_config(self):
        print()
        print("Data Server:")
        print("  - URL: <%s>" % self._ds.url)
        print("  - %d Package Collections Available" % len(self._ds.collections()))
        print("  - %d Individual Packages Available" % len(self._ds.packages()))
        print()
        print("Local Machine:")
        print("  - Data directory: %s" % self._ds.download_dir)

    def _simple_interactive_config(self):
        self._show_config()
        while True:
            print()
            self._simple_interactive_menu(
                "s) Show Config", "u) Set Server URL", "d) Set Data Dir", "m) Main Menu"
            )
            user_input = input("Config> ").strip().lower()
            if user_input == "s":
                self._show_config()
            elif user_input == "d":
                new_dl_dir = input("  New Directory> ").strip()
                if new_dl_dir in ("", "x", "q", "X", "Q"):
                    print("  Cancelled!")
                elif os.path.isdir(new_dl_dir):
                    self._ds.download_dir = new_dl_dir
                else:
                    print("Directory %r not found!  Create it first." % new_dl_dir)
            elif user_input == "u":
                new_url = input("  New URL> ").strip()
                if new_url in ("", "x", "q", "X", "Q"):
                    print("  Cancelled!")
                else:
                    if not new_url.startswith(("http://", "https://")):
                        new_url = "http://" + new_url
                    try:
                        self._ds.url = new_url
                    except Exception as e:
                        print(f"Error reading <{new_url!r}>:\n  {e}")
            elif user_input == "m":
                break


######################################################################
# Helper Functions
######################################################################
# [xx] It may make sense to move these to nltk.internals.


def md5_hexdigest(file):
    """
    Calculate and return the MD5 checksum for a given file.
    ``file`` may either be a filename or an open stream.
    """
    if isinstance(file, str):
        with open(file, "rb") as infile:
            return _md5_hexdigest(infile)
    return _md5_hexdigest(file)


def _md5_hexdigest(fp):
    md5_digest = md5()
    while True:
        block = fp.read(1024 * 16)  # 16k blocks
        if not block:
            break
        md5_digest.update(block)
    return md5_digest.hexdigest()


# change this to periodically yield progress messages?
# [xx] get rid of topdir parameter -- we should be checking
# this when we build the index, anyway.
def unzip(filename, root, verbose=True):
    """
    Extract the contents of the zip file ``filename`` into the
    directory ``root``.
    """
    for message in _unzip_iter(filename, root, verbose):
        if isinstance(message, ErrorMessage):
            raise Exception(message)


def _unzip_iter(filename, root, verbose=True):
    if verbose:
        sys.stdout.write("Unzipping %s" % os.path.split(filename)[1])
        sys.stdout.flush()

    try:
        zf = zipfile.ZipFile(filename)
    except zipfile.error as e:
        yield ErrorMessage(filename, "Error with downloaded zip file")
        return
    except Exception as e:
        yield ErrorMessage(filename, e)
        return

    zf.extractall(root)

    if verbose:
        print()


_downloader = Downloader()
download = _downloader.download


def download_shell():
    DownloaderShell(_downloader).run()


def update():
    _downloader.update()


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        "-d",
        "--dir",
        dest="dir",
        help="download package to directory DIR",
        metavar="DIR",
    )
    parser.add_option(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        default=False,
        help="work quietly",
    )
    parser.add_option(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="download even if already installed",
    )
    parser.add_option(
        "-e",
        "--exit-on-error",
        dest="halt_on_error",
        action="store_true",
        default=False,
        help="exit if an error occurs",
    )
    parser.add_option(
        "-u",
        "--url",
        dest="server_index_url",
        default=os.environ.get("Kolibri_DOWNLOAD_URL"),
        help="download server index url",
    )

    (options, args) = parser.parse_args()

    downloader = Downloader(server_index_url=options.server_index_url)

    if args:
        for pkg_id in args:
            rv = downloader.download(
                info_or_id=pkg_id,
                download_dir=options.dir,
                quiet=options.quiet,
                force=options.force,
                halt_on_error=options.halt_on_error,
            )
            if rv == False and options.halt_on_error:
                break
    else:
        downloader.download(
            download_dir=options.dir,
            quiet=options.quiet,
            force=options.force,
            halt_on_error=options.halt_on_error,
        )



