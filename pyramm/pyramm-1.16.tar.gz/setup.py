# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyramm', 'pyramm.ops']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.7.1,<2.0.0',
 'frozendict>=2.3.2,<3.0.0',
 'geopandas>=0.8.1,<0.9.0',
 'numpy>=1.19.4,<2.0.0',
 'pandas>=1.1.4,<2.0.0',
 'pyproj>=3.0.0,<4.0.0',
 'requests>=2.25.0,<3.0.0',
 'scipy>=1.5.4,<2.0.0',
 'unsync>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'pyramm',
    'version': '1.16',
    'description': 'Provides a wrapper to the RAMM API and additional tools for positional referencing',
    'long_description': '# pyramm\n\n<img align="right" src="https://github.com/captif-nz/pyramm/actions/workflows/push.yml/badge.svg">\n\n\nPython wrapper for RAMM API.\n\n**Users must have their own login for the RAMM database.**\n\n## Installation\n\n```bash\npip install pyramm\n```\n\n## Issues\n\nPlease submit an issue if you find a bug or have an idea for an improvement.\n\n## Initialise\n\nYou must first initialise the connection to the RAMM API as follows. Note that the\n`database` argument defaults to `"SH New Zealand"` if it is not provided.\n\n```python\nfrom pyramm.api import Connection\nconn = Connection(username, password, database="SH New Zealand")\n```\n\nAlternatively the username and password can be stored in file called `.pyramm.ini`. This\nfile must be saved in the users home directory (`"~"` on linux) and contain the following:\n\n```ini\n[RAMM]\nUSERNAME = username\nPASSWORD = password\n```\n\nYou are then able to initialise the RAMM API connection without providing your login\ncredentials each time.\n\n```python\nfrom pyramm.api import Connection\nconn = Connection()\n```\n\n## Table and column names\n\nA list of available tables can be accessed using:\n\n```python\ntable_names = conn.table_names()\n```\n\nA list of columns for a given table can be accessed using:\n\n```python\ncolumn_names = conn.column_names(table_name)\n```\n\n## Table data\n\nSome methods are attached to the `Connection` object to provide convenient access to\nselected RAMM tables. These helper methods implement some additional filtering (exposed\nas method arguments) and automatically set the DataFrame index to the correct table\ncolumn(s).\n\nTables not listed in the sections below can be accessed using the general `get_data()`\nmethod:\n\n```python\ndf = conn.get_data(table_name)\n```\n\n### General tables:\n```python\nroadnames = conn.roadnames()\n```\n```python\ncarrway = conn.carr_way(road_id=None)\n```\n```python\nc_surface = conn.c_surface(road_id=None)\n```\n```python\ntop_surface = conn.top_surface()\n```\n```python\nsurf_material = conn.surf_material()\n```\n```python\nsurf_category = conn.surf_category()\n```\n```python\nminor_structure = conn.minor_structure()\n```\n\n### HSD tables:\n\n```python\nhsd_roughness = conn.hsd_roughness(road_id, latest=True, survey_year=None)\n```\n```python\nhsd_roughness_hdr = conn.hsd_roughness_hdr()\n```\n```python\nhsd_rutting = conn.hsd_rutting(road_id, latest=True, survey_year=None)\n```\n```python\nhsd_rutting_hdr = conn.hsd_rutting_hdr()\n```\n```python\nhsd_texture = conn.hsd_texture(road_id, latest=True, survey_year=None)\n```\n```python\nhsd_texture_hdr = conn.hsd_texture_hdr()\n```\n\n## Centreline\n\nThe `Centreline` object is provided to:\n - assist with generating geometry for table entries (based on `road_id`, `start_m` and\n`end_m` values),\n <!-- - find the nearest geometry element to give a point (`latitude`, `longitude`),\n - find the displacement (in metres) along the nearest geometry element given a point\n(`latitude`, `longitude`). -->\n\nThe base geometry used by the `Centreline` object is derived from the `carr_way` table.\n\n### Create a Centreline instance:\n\n```python\ncentreline = conn.centreline()\n```\n\n### Append geometry to table:\n\nFor a table containing `road_id`, `start_m` and `end_m` columns, the geometry can be\nappended using the `append_geometry()` method:\n\n```python\ndf = centreline.append_geometry(df, geometry_type="wkt")\n```\n\nThe `geometry_type` argument defaults to `"wkt"`. This will provide a\n[WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry)\nLineString for each row.\n\nAlternatively, `geometry_type` can be set to `"coord"` to append\na `northing` and `easting` column to the DataFrame.\n\n### Find carriageway and position from point coordinates:\n\nThe carriageway and position information (e.g. Rs/Rp) can be determined for a point coordinate\nusing the `position()` method:\n\n```python\npoint = Point((172.618567, -43.441594))  # Shapely Point object\nposition = centreline.position(point, point_crs=4326)\n```\n\nThe point coordinate reference system defaults to WGS84 but can be adjusted using the\n`point_crs` argument. The value must be an integer corresponing to the\n[EPSG code](https://epsg.io/) (e.g. `4326` for WGS84).\n\n#### Partial centreline\n\nSometimes it is necessary to match only to selected parts of the RAMM centreline. In this\ncase a partial centreline can be generated and used for the matching:\n\n```python\n# Generate a partial centreline containing only road_id 3656 between route position 10m\n# and 100m:\npartial_centreline = conn.centreline(lengths={3656: [10, 100]})\n\npoint = Point((172.608406, -43.451023))\nposition = partial_centreline.position(point)\n```\n\nThe `lengths` argument is a Python dictionary containing `road_id` keys and start/end\nposition pair values. Some examples include:\n\n- `{3656: None}` includes the entire centreline for road_id 3656.\n- `{3656: [10, 100]}` includes only the section of centreline for road_id 3656 between route position 10m and 100m.\n- `{3656: [500, None]}` includes only the section of centreline for road_id 3656 from route position 500m.\n',
    'author': 'John Bull',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/captif-nz/pyramm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
