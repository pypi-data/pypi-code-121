#!/usr/bin/env python3

"""
The geonorge module contains functions and global variables for
interaction with ATOM feeds and download API of geonorge.no

Use the module like this:

.. code-block:: python

   # Import module
   from osgeonorge.geonorge import GeonorgeAdapter
   # Initialize class
   gn_download = GeonorgeAdapter()
   # List available feeds in a pretty table format
   gn_download.print_feeds()

This returns something like this:

.. code-block:: python

   AdminstrativeEnheter GML   30-Oct-2019 05:27 1677 https://nedlasting.geonorge.no/geonorge/ATOM-Feeds/AdminstrativeEn...

Next pick a dataset and format to parse and download:

.. code-block:: python

   # Parse feed of dataset 'Sprstrandsoner' in 'FGDB' format
   gn_download.parse_feed('Sprstrandsoner', 'FGDB')
   # Get a list of datasets that cover the whole country
   gn_download.get_data_list(coverage="Landsdekkende", crs=(3045, 5973, 25833))


Finally, download the currently selected dataset(s):

.. code-block:: python

   gn_download.download_datasets()
   gn_download.extract_datasets()
   gn_download.get_files()
   gn_download.get_metadata()

Now you are ready to e.g. import data to PostgreSQL using the
:obj:`~osgeonorge.postgres.PostGISAdapter`

"""

import base64
import os
import urllib.request
import re
import warnings
import zipfile

from functools import partial
from multiprocessing import Pool
from xml.etree import ElementTree as ET
from html.parser import HTMLParser
from http.client import IncompleteRead
from io import BytesIO

# Non-builtin imports
import requests
from osgeonorge.utils import extract_zip, slice_dict, extract_metadata, remove_suffixes
from osgeonorge.sosi import recode_sosi


class GeonorgeAdapter:
    """
    Basic class for listing, downloading, extracting and parsing  data from
    ATOM feeds in geonorge.no

    :todo: a) add option to store logs
           b) option to only update if needed and also clean in future
           Globbing the download_dir could help
           c) add option to remove zip files
           d) add option to use config file
    """

    #: Attribute containg a dict with supported formats and suffix keys for extracting data from zip archives
    ogr_supported_formats = {
        "CSV": [".csv"],
        "FGDB": [".gdb/gdb"],
        "GEOJSON": [".json"],
        "GML": [".gml"],
        "GPX": [".gpx"],
        "GeoJSON": [".json"],
        "SOSI": [".sos"],
        "Shape": [".shp"],
        "SpatiaLite": [".sqlite"],
        "XYZ": ["xyz"],
    }
    #: Attribute containg a dict with supported formats and suffix keys for extracting data from zip archives
    gdal_supported_formats = {
        "BIN": [".bil"],
        "CSV": [".csv"],
        "DEM": [".dem"],
        "GeoTIFF": [".tif", ".tiff", ".gtif", ".gtiff"],
        "IMG": [".img"],
        "JPEG": [".jpg", ".jpeg"],
        "MrSID": [".mr", ".sid"],
        "SpatiaLite": [".sqlite"],
        "TIFF": [".tif", ".tiff", ".gtif", ".gtiff"],
        "XYZ": [".xyz"],
    }
    #: Attribute containg a dict with other supported formats not readable by GDAL/OGR
    other_supported_formats = {
        "POSTGIS": [".backup"],
        "PostGIS": [".backup"],
    }
    #: Attribute containg a tuple with (currently) unsupported or non-spatial formats
    currently_unsupported_formats = (
        "AI",
        "DAT",
        "DLL",
        "EMF",
        "ENH",
        "JSON",
        "NED",
        "PDF",
        "PPTX",
        "S57",
        "XLSX",
    )
    #: Attribute containg a tuple with (currently) tested formats
    currently_tested_formats = ["FGDB"]
    #: Arrtibute containg a tuple of target EPSG codes (defaults to country wide valid EPSG codes)
    target_crs = (32633, 25833, 3045, 5973)

    def __init__(
        self,
        atom_url="https://nedlasting.geonorge.no/geonorge/ATOM-Feeds",
        download_dir="./",
        work_dir="./",
        credits_file=None,
        cores=1,
        verbose=True,
    ):
        #: Attribute containg the URL to the website listing available ATOM feeds from geonorge.no
        self.atom_url = atom_url
        #: Attribute containg aictionary with parsed list of ATOM feeds
        self.feeds = {}
        self.get_feeds()
        #: Attribute containg a set of all available formats in geonorge feeds
        self.available_formats = {k for val in self.feeds.values() for k in val.keys()}
        #: Attribute containg directory to which data is downloaded or written to
        self.download_dir = download_dir
        #: Attribute containg the working directory where zip files are extracted to
        self.work_dir = work_dir
        #: Attribute containg dictionary with metadata of the current, parsed dataset feed
        self.current_feed_dict = {}
        #: Attribute containg dictionary the format of the current, parsed dataset feed
        self.current_feed_format = None
        #: Attribute containg dictionary with metadata of the current, parsed dataset of a selected format
        self.current_data_dict = {}
        #: Attribute containg a list of dictionaries with members of the zip files downloaded and extracted from the current_data_dict
        self.current_zip_content = None
        #: Attribute containg a list of OGR readable files in the zip files downloaded and extracted from the current_data_dict
        self.current_ogr_files = None
        #: Attribute containg a maximum number for retries for incomplete downloads (may happen if connection is closed prematurely or empty chunk of data is send
        self.max_retries = 10
        #: Attribute containg geonorge credits as tuple (username, password)
        self.user_credits = (None, None)
        self.get_geonorge_credits(credits_file)
        #: Number of cores to use for parallel download (if relevant)
        self.cores = cores
        #: Attribute to define if verbose messages should be given
        self.verbose = verbose
        # Check if download directory is writable
        self.__check_permissions(self.download_dir, "Download")
        # Check if working directory is writable
        self.__check_permissions(self.work_dir, "Extraction of zip files")

    def __check_permissions(self, directory, mode, log_level="warning"):
        """"""
        if not os.access(directory, os.W_OK):
            user_message = "Cannot write to directory {directory}. {mode} will fail."
            if log_level == "warning":
                warnings.warn(user_message)
            else:
                raise OSError(user_message)

    def get_feed(self, dataset, data_format):
        """
        Extract dataset information from ATOM feed and stores the meatadata
        parsed into a dictionary in the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_feed_dict` attribute.

        Currently parsing is mostly tailored at "kommuneplan" feed

        Basic elements handled so far are:

        - '{http://www.w3.org/2005/Atom}subtitle'
        - '{http://www.w3.org/2005/Atom}link'
        - '{http://www.w3.org/2005/Atom}updated'
        - '{http://www.w3.org/2005/Atom}generator'
        - '{http://www.w3.org/2005/Atom}rights'
        - '{http://www.w3.org/2005/Atom}entry'
        - '{http://www.w3.org/2005/Atom}title'
        - '{http://www.w3.org/2005/Atom}id'

        Datasets are listed as entries

        :param dataset: Dataset of which the ATOM feed XML document should be parsed
        :type dataset: str
        :param data_format: OGR readable format to fetch ATOM feed for
                           (see :attr:`~osgeonorge.geonorge.GeonorgeAdapter.available_formats`).
        :type data_format: str

        """
        if (
            data_format not in self.ogr_supported_formats
            and data_format not in self.other_supported_formats
        ):
            raise ValueError(
                f"Requested format '{data_format}' is currently not supported."
            )
        if data_format not in self.available_formats:
            raise ValueError(
                f"Requested format '{data_format}' is currently not available at geonorge.no."
            )
        if dataset not in self.feeds:
            raise ValueError(f"No ATOM feed found for dataset {dataset} on geonorge.")
        if data_format not in self.feeds[dataset]:
            raise ValueError(
                f"Format {data_format} not found for dataset {dataset} on geonorge."
            )

        feed_dict = {}
        feed = requests.get(self.feeds[dataset][data_format]["url"])
        root = ET.fromstring(feed.text)
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            updated = entry.find("{http://www.w3.org/2005/Atom}updated").text
            title = [
                e.strip()
                for e in entry.find("{http://www.w3.org/2005/Atom}title").text.split(
                    ","
                )
            ]
            url = entry.find("{http://www.w3.org/2005/Atom}id").text.replace(
                f"_{updated}", ""
            )
            crs = [
                e.attrib["term"]
                for e in entry.findall("{http://www.w3.org/2005/Atom}category")
                if "scheme" in e.attrib
                and e.attrib["scheme"] == "http://www.opengis.net/def/crs/"
            ][0]
            feed_dict[url.split("/")[-1]] = {
                "updated": updated,
                "title": title,
                "url": url,
                "crs": crs,
            }

        self.current_feed_dict = feed_dict
        self.current_feed_format = data_format

    def get_feeds(self):
        """
        Method to fetch available ATOM feeds and store the results as a dict
        in the :attr:`~osgeonorge.geonorge.GeonorgeAdapter.feeds` attribute.

        :param atom_url: URL to ATOM feed XML document to parse
        :type atom_url: str
        """
        atom_list_dict = {}
        parse_atom = ParseATOMList()
        with urllib.request.urlopen(self.atom_url) as response:
            parse_atom.feed(response.read().decode())
        for key, val in parse_atom.feed_dict.items():
            key_elements = key.replace(".xml", "").split("_AtomFeed")
            if len(key_elements) != 2:
                continue
            if key_elements[0] in atom_list_dict:
                atom_list_dict[key_elements[0]][key_elements[1]] = {
                    "url": f"{self.atom_url}/{key}",
                    "updated": val[1][0],
                    "size": val[1][1],
                }
            else:
                atom_list_dict[key_elements[0]] = {
                    key_elements[1]: {
                        "url": f"{self.atom_url}/{key}",
                        "updated": val[1][0],
                        "size": val[1][1],
                    }
                }

        self.feeds = atom_list_dict

    def get_geonorge_credits(self, credits_file=None):
        """
        Method to fetch user credits for Geonorge.no and store it in the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.user_credits` attribute.
        Credentials for authentication to geonorge API can be either given
        using a credtis_file (see .geonorge.example) or by defining
        environment variables:

        :envvar:`GEONORGE_USER`
        :envvar:`GEONORGE_PASSWORD`

        The user's :envvar:`HOME` directoy is allways searched for a .geonorge
        credits file.

        Username and password need to represent BAAT authentication (and not GeoID)

        :param credits_file: Path to credis file to read
        :type credits_file: str
        """
        # Get authentication
        user = os.environ.get("GEONORGE_USER")
        password = os.environ.get("GEONORGE_PASSWORD")

        credits_file = credits_file or os.path.expanduser("~/.geonorge")
        if os.path.exists(credits_file):
            try:
                with open(credits_file, "r") as geonorge_credits:
                    user, password = geonorge_credits.read().split("\n")[0:2]
            except OSError as e:
                raise e
        if not all((user, password)):
            warnings.warn(
                "No authentication provided. Downloading data is thus not possible.\n"
                "Please provide authentication information"
            )
        self.user_credits = (user, password)

    def print_feeds(self, pattern=None):
        """
        Method to print available ATOM feeds in table like style

        :param pattern: Regular expression for filtering feeds by dataset name
        :type pattern: str
        """
        for key, val in self.feeds.items():
            for k, v in val.items():
                print(f"{key:<75} {k:<7} {v['updated']:<17} {v['size']:<8} {v['url']}")

    def print_datasets(self):
        """
        Method to print a list of available datasets from ATOM feeds
        """
        print("\n".join(self.feeds.keys()))

    def print_all_formats(self):
        """
        Method to print a list of all available formats from ATOM feeds
        """
        print("\n".join(self.available_formats))

    def print_currect_feed(self):
        """
        Method to print content of an ATOM feed in table like style
        """
        if not self.current_feed_dict:
            warnings.warn("No feed initialized. Run 'get_feed' method first.")
        else:
            for key, val in self.current_feed_dict:
                print(
                    f"{key:<75} {val['updated']:<20} {val['crs'].replace('EPSG:', ''):<5} {val['title'][-1]:<15}"
                )

    def get_data_dict(self, coverage="Landsdekkende", crs=None):
        """
        Method to store metadata of a selected coverage and crs from the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_feed_dict`
        in the :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_data_dict`
        attribute. A current feed has to be fetched beforehand with the
        :func:`~osgeonorge.geonorge.GeonorgeAdapter.get_feed` method.

        :param coverage: Coverage of dataset whos feed(s) to parse (allowed values: "Landsdekkende", "Fylkevis", "Kommunevis")
        :type coverage: str
        :param crs: Coordinate reference system of feed(s) to parse
        :type crs: tuple of int
        """

        self.current_data_dict = {
            key: val
            for key, val in self.current_feed_dict.items()
            if (crs is None or val["crs"] in (f"EPSG:{c}" for c in crs))
            and (
                (coverage == "Landsdekkende" and coverage in val["title"][-1])
                or (coverage == "Fylkevis" and val["title"][-1][0].isdigit())
                or (
                    coverage == "Kommunevis"
                    and val["title"][1].isdigit()
                    and "Landsdekkende" not in val["title"][-1]
                )
            )
        }

    def download_current_datasets(self, download=True):
        """
        Method to download data from the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_data_dict` attribute
        """
        self.__check_permissions(self.download_dir, "Download", log_level="error")
        files_n = len(self.current_data_dict)
        if files_n == 1 or self.cores == 1:
            dict_keys = [
                self._download_geonorge({key: val}, download=download)
                for key, val in self.current_data_dict.items()
            ]
        elif files_n > 1 and self.cores > 1:
            download_with_kwargs = partial(self._download_geonorge, download=download)
            with Pool(self.cores) as p:
                dict_keys = p.map(
                    download_with_kwargs,
                    [
                        dict_chunk
                        for dict_chunk in slice_dict(
                            self.current_data_dict, min(files_n, self.cores)
                        )
                    ],
                )
        else:
            warnings.warn("Nothing to download in current datasets")
        # update dict keys
        if dict_keys:
            dict_keys = [item for tuple_list in dict_keys for item in tuple_list]
            for old_key, new_key in dict_keys:
                self.current_data_dict[new_key] = self.current_data_dict.pop(old_key)

    def _download_geonorge(self, atom_dict, download=True):
        """
        Private method to download all data in the the atom_dict from geonorge nedlasting API

        :todo: Should only update if needed and also clean in future
               Globbing the download_dir could help

        """
        # Setup http session
        s = requests.Session()

        # Check provided authentication
        if (
            len(self.user_credits) != 2
            or type(self.user_credits) != tuple
            or not all(
                [type(auth_element) == str for auth_element in self.user_credits]
            )
        ):
            raise ValueError("No or invalid authentication provided.")

        # Authenticate with basic http authentication by adding header to session
        s.auth = self.user_credits

        dict_key_list = []
        # Download dict content
        for file_id, file_dict in atom_dict.items():
            if self.verbose:
                print(f"Downloading {file_dict['url']}...")
            zip_file = s.get(file_dict["url"], allow_redirects=True, stream=True)
            file_name = zip_file.headers.get("Content-Disposition")
            if file_name and "filename=" in file_name:
                file_name = file_name.split("filename=")[1].strip('"')
            else:
                file_name = file_id
            file_name = os.path.join(self.download_dir, file_name)
            print(file_name)
            if not zip_file.ok:
                zip_file.raise_for_status()
            dict_key_list.append((file_id, file_name))
            if not download:
                continue
            if zip_file.headers["Content-Type"] == "application/zip":
                # Download binary
                with open(file_name, "wb") as f:
                    f.write(zip_file.content)
            elif zip_file.headers["Content-Type"] == "application/octet-stream":
                request = urllib.request.Request(file_dict["url"])
                base64string = base64.b64encode(
                    bytes("%s:%s" % self.user_credits, "ascii")
                )
                request.add_header(
                    "Authorization", "Basic %s" % base64string.decode("utf8")
                )
                retries = 0
                success = False
                data = BytesIO()
                while not success and retries < self.max_retries:
                    try:
                        with urllib.request.urlopen(request) as response:
                            data.write(response.read())
                        success = True
                    except IncompleteRead as e:
                        data.write(e.partial)
                        request.add_header("Range", f"bytes={data.tell()}-")
                        retries += 1

                with open(file_name, "wb") as of:
                    of.write(data.getvalue())

                    """if retries > 0:
                        warnings.warn(
                            f"IncompleteReadError, retry {retries} of max {self.max_retries}"
                        )
                    zip_file = s.get(
                        file_dict["url"],
                        allow_redirects=True,
                        stream=True,
                    )
                    print(zip_file.headers)
                    with open(os.path.join(self.download_dir, file_name), "wb") as f:
                        for content in zip_file.iter_content(1024 * 1024 * 30):
                            f.write(content)
                        f.flush()
                    if float(os.path.getsize()) == float(
                        float(zip_file.headers["Content-Length"])
                    ):
                        success = True
                    else:
                        retries += 1"""
                # with open(os.path.join(self.download_dir, file_name), "wb") as f:
                #     shutil.copyfileobj(zip_file.raw, f)
            else:
                # Download plain text
                with open(file_name, "w") as f:
                    f.write(zip_file.text)
        return dict_key_list

    def extract_current_datasets(self):
        """
        Method to extract data from downloaded zip file(s) from the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_feed_dict` attribute.
        Datasets have to be downloaded beforehand with the
        :func:`~osgeonorge.geonorge.GeonorgeAdapter.download_datasets` method.
        A list of extracted files is stored in the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_zip_content` attribute.
        """
        self.__check_permissions(
            self.work_dir, "Extraction of zip files", log_level="error"
        )
        zip_dict = {
            k: v for k, v in self.current_data_dict.items() if zipfile.is_zipfile(k)
        }
        if len(zip_dict) == 1 or self.cores == 1:
            self.current_zip_content = [
                extract_zip(
                    os.path.join(self.download_dir, f"{dataset_id}"),
                    workdir=self.work_dir,
                )
                for dataset_id in zip_dict
            ]
        elif len(zip_dict) > 1 and self.cores > 1:
            with Pool(self.cores) as p:
                self.current_zip_content = p.starmap(
                    extract_zip,
                    [
                        (
                            os.path.join(self.download_dir, f"{dataset_id}"),
                            self.work_dir,
                        )
                        for dataset_id in zip_dict
                    ],
                )
        else:
            warnings.warn("Nothing to extract")

    def get_current_ogr_files(self):
        """
        Method to extract OGR readable file data from downloaded zip files from the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_feed_dict` attribute.
        Datasets have to be extracted beforehand with the
        :func:`~osgeonorge.geonorge.GeonorgeAdapter.extract_datasets` method.
        """
        ogr_files_in_zips = {}
        for zip_file, zip_content in self.current_zip_content:
            ogr_files_in_zips[zip_file] = []
            for member in zip_content:
                ogr_files_in_zips[zip_file].extend(
                    [
                        os.path.join(
                            self.work_dir, remove_suffixes(member, [f"{os.sep}gdb"])
                        )
                        for suffix in self.ogr_supported_formats[
                            self.current_feed_format
                        ]
                        if member.endswith(suffix)
                    ]
                )

        self.current_ogr_files = ogr_files_in_zips

    def get_current_metadata(self, split_by_objtype=False, layer=None):
        """
        Method to extract metadata from OGR-readable files in the downloaded data

        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_ogr_files` attribute.
        Datasets have to be extracted beforehand with the
        :func:`~osgeonorge.geonorge.GeonorgeAdapter.extract_datasets` method
        and ogr readable files listed with the
        :func:`~osgeonorge.geonorge.GeonorgeAdapter.get_ogr_files` method.
        Results are stored in the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_ogr_files_metadata` attribute.
        """
        ogr_files = []
        for ogr_list in self.current_ogr_files.values():
            ogr_files += ogr_list

        if self.current_feed_format == "SOSI":
            files_n = len(ogr_files)
            if files_n <= 1 or self.cores == 1:
                [recode_sosi(sos_file) for sos_file in ogr_files]
            else:
                with Pool(self.cores) as p:
                    p.map(recode_sosi, ogr_files)

        if len(ogr_files) == 1 or self.cores == 1:
            self.current_ogr_files_metadata = {
                member: extract_metadata(
                    member,
                    target_srs=self.target_crs,
                    split_by_objtype=split_by_objtype,
                    layer_name=layer,
                )
                for member in ogr_files
            }
        else:
            extract_metadata_kwargs = partial(
                extract_metadata,
                target_srs=self.target_crs,
                split_by_objtype=split_by_objtype,
                layer_name=layer,
            )
            with Pool(self.cores) as p:
                file_metadata = p.map(extract_metadata_kwargs, ogr_files)
            self.current_ogr_files_metadata = {
                member: file_metadata[idx] for idx, member in enumerate(ogr_files)
            }

    def fetch(
        self,
        dataset,
        data_format,
        coverage,
        crs=None,
        extract=True,
        get_metadata=True,
        split_by_objtype=False,
        layer=None,
        download=True,
    ):
        """
        Wrapper method to download, extract and parse a dataset of a given
        format with a given coverage. The method assumes the user knows
        and can provide valid input for those three paramters.

        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_ogr_files` attribute.
        Datasets have to be extracted beforehand with the
        :func:`~osgeonorge.geonorge.GeonorgeAdapter.extract_datasets` method
        and ogr readable files listed with the
        :func:`~osgeonorge.geonorge.GeonorgeAdapter.get_ogr_files` method.
        Results are stored in the
        :attr:`~osgeonorge.geonorge.GeonorgeAdapter.current_ogr_files_metadata` attribute.

        :param dataset: Name of the dataset to download
        :type dataset: str
        :param dataset: Filter files of a dataset by the given data format
        :type dataset: str
        :param coverage: Filter files of a dataset by the given coverage None means no filter
        :type coverage: str
        :param crs: Filter files of a dataset by the given Coordinate reference systems None means no filter
        :type crs: tuple of int
        """
        self.get_feed(dataset, data_format)
        self.get_data_dict(coverage, crs=crs)
        self.download_current_datasets(download=download)
        if extract:
            self.extract_current_datasets()
        if get_metadata and data_format in self.ogr_supported_formats:
            self.get_current_ogr_files()
            self.get_current_metadata(split_by_objtype=split_by_objtype, layer=layer)


class ParseATOMList(HTMLParser):
    """
    A simple, basic html parser class to extract links to ATOM feeds in geonorge.no
    together with attributes (time of last update, size)
    """

    def __init__(self):
        super().__init__()
        self.reset()
        self.count = 0
        self.tag = None
        self.href = None
        self.feed_dict = {}

    def handle_starttag(self, tag, attrs):
        """
        Extract href tags and stor info a class attribute
        """
        self.tag = tag
        self.count += 1

        if tag == "a":
            self.href = attrs[0][1]
            self.feed_dict[attrs[0][1]] = []

    def handle_data(self, data):
        """
        Get data stored with href tags
        """
        if self.tag == "a":
            self.feed_dict[self.href].append(re.split(r"\s{2,}", data.strip()))
