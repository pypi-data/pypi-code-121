#!/usr/bin/env python3

"""
The grassgis module contains functions for using GRASS GIS
as data warehouse for data from geonorge.no

This module is incomplete!

Use the module like this:

.. code-block:: python

   import os
   # Import downloader class from module
   from osgeonorge.grassgis import GRASSGISAdapter
   # Initialize class
   ogng = GRASSGISAdapter(grassdata="/data/grassdata", cores=5)

"""


import subprocess
import re
from osgeonorge.utils import norwegian_to_ascii, compile_ogr_cmd, ogr_casts

from grass_session import Session
import grass.script as gscript


class GRASSGISAdapter:
    """
    Basic class for importing data from geonorge.no into GRASS GIS

    """

    def __init__(
        self,
        grassdata="./",
        cores=1,
        verbose=True,
    ):
        #: Attribute containg the path to the GRASS GIS database
        self.grassdata = grassdata
        #: Attribute containg the path to the GRASS GIS database
        self.cores = cores
        #: Attribute containg the name of the current GRASS GIS location
        self.current_location = None
        #: Attribute containg the name of the current GRASS GIS mapset
        self.current_mapset = None

    def import_raster(self, raster_file, raster_map):
        """Method to import raster data into GRASS GIS"""
        with Session(
            gisdb=self.grassdata,
            location=self.current_location,
            mapset=self.current_mapset,
        ):
            gscript.run_command("r.in.gdal", input=raster_file, output=raster_map)

    def import_vector(self, vector_file, vector_map):
        """Method to import vector data into GRASS GIS"""
        with Session(
            gisdb=self.grassdata,
            location=self.current_location,
            mapset=self.current_mapset,
        ):
            gscript.run_command("v.in.ogr", input=vector_file, output=vector_map)
