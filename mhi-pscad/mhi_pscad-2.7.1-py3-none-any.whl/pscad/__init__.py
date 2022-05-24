#===============================================================================
# Manitoba Hydro Internation / Power Technology Center
# mhi.pscad package
#===============================================================================

"""
Connection Methods
==================

The PSCAD Automation Library provides three methods of connecting to the PSCAD
Application:

1. Launching a new instance of PSCAD
2. Connect to an existing PSCAD instance
3. Connect to an existing PSCAD instance if any, or launch a new instance of PSCAD otherwise.


New Instance
------------

To launch and connect to new PSCAD instance, use the following command:

.. autofunction:: mhi.pscad.launch


Existing Instance
-----------------

To connect to already running PSCAD instance, use the following command:

.. autofunction:: mhi.pscad.connect

If multiple instances are running, the Automation Library will connect
to one of them.
If the port which the desired instance of PSCAD is listening on is known,
the ``port=#`` option may be given in ``connect()``::

   pscad = mhi.pscad.connect(port=54321)

If the desired PSCAD instance is running on another machine,
the ``host="..."`` parameter must be given as well::

   pscad = mhi.pscad.connect(host="192.168.0.123", port=54321)

Existing or New
---------------

To connect to any running PSCAD instance,
or launch & connect to a new PSCAD instance if there are no existing instances,
or if running the script from inside PSCAD itself, use the following command:

.. autofunction:: mhi.pscad.application

"""

#===============================================================================
# Imports
#===============================================================================

import os, sys, warnings, logging
import mhi.common

from typing import cast, List, Tuple
from xml.etree import ElementTree as _ET

from mhi.common import config
from mhi.common.remote import Remotable, deprecated, Context
from mhi.common.codec import MapCodec

from .pscad import PSCAD
from .project import Project, Layer, Resource, GlobalSubstitution
from .simset import SimulationSet, SimsetTask, ProjectTask, ExternalTask
from .canvas import Canvas, UserCanvas
from .definition import Definition
from .component import ZComponent, Component, UserCmp
from .component import Wire, StickyWire, Bus, TLine, Cable
from .annotation import Sticky, Divider
from .graph import GraphFrame, GraphPanel, OverlayGraph, PolyGraph, PlotFrame, Curve
from .control import ControlFrame, Control, Button, Switch, Selector, Slider
from .instrument import Instrument, PolyMeter, PhasorMeter, Oscilloscope
from .certificate import Certificate, Feature
from .graphics import GfxCanvas, GfxComponent, Port, Text
from .graphics import GfxBase, Line, Rect, Oval, Arc, Shape


#===============================================================================
# Script Version Identifiers
#===============================================================================

VERSION = '2.7.1'
VERSION_HEX = 0x020701f0


#===============================================================================
# Logging
#===============================================================================

_LOG = logging.getLogger(__name__)


#===============================================================================
# Options
#===============================================================================

OPTIONS = config.fetch("~/.mhi.pscad.py")


#===============================================================================
# Connection and Application Start
#===============================================================================

def application() -> PSCAD:
    """
    This method will find try to find a currently running PSCAD application,
    and connect to it.  If no running PSCAD application can be found, or
    if it is unable to connect to that application, a new PSCAD application
    will be launched and a connection will be made to it.

    If running inside a Python environment embedded within an PSCAD
    application, the containing application instance is always returned.

    Returns:
        PSCAD: The PSCAD application proxy object

    Example::

        import mhi.pscad
        pscad = mhi.pscad.application()
        pscad.load('myproject.pscx')

    .. versionadded:: 2.0
    """

    app_ = Context._application(connect, launch, 'PSCAD%.exe') # pylint: disable=protected-access
    return cast('PSCAD', app_)


def connect(host: str = 'localhost', port: int = None,
            timeout: float = 5) -> PSCAD:

    """
    This method will find try to find a currently running PSCAD application,
    and connect to it.

    Parameters:
        host (str): The host the PSCAD application is running on
            (defaults to the local host)

        port (int): The port to connect to.  Required if running multiple
            PSCAD instances.

        timeout (float): Seconds to wait for the connection to be accepted.

    Returns:
        PSCAD: The PSCAD application proxy object

    Example::

        import mhi.pscad
        pscad = mhi.pscad.connect()
        pscad.load('myproject.pscx')

    .. versionadded:: 2.0
    """

    if host == 'localhost':
        if not port:
            from mhi.common import process # pylint: disable=import-outside-toplevel
            ports = process.listener_ports_by_name('PSCAD%')
            if not ports:
                raise ProcessLookupError("No availiable PSCAD process")

            addr, port, pid, appname = ports[0]
            _LOG.info("%s [%d] listening on %s:%d", appname, pid, addr, port)

    _LOG.info("Connecting to %s:%d", host, port)

    app_ = Context._connect(host=host, port=port, timeout=timeout) # pylint: disable=protected-access
    app = cast('PSCAD', app_)

    app._initialize()                         # pylint: disable=protected-access

    return app


def launch(port=None, silence=True, minimize=False, splash=False, timeout=5,
           version=None, x64=None, settings=None, load_user_profile=None,
           minimum='5.0', maximum=None, allow_alpha=True, allow_beta=True,
           extra_args=None, **options) -> PSCAD:  # pylint: disable=too-many-arguments

    """
    Launch a new PSCAD instance and return a connection to it.

    Parameters:
        port (int): The port to connect to.  Required if running multiple
            PSCAD instances.

        silence (bool): Suppresses dialogs which can block automation.

        minimize (bool): `True` to minimize PSCAD to an icon.

        splash (bool): `False` to disable the startup splash/logo window.

        timeout (float): Time (seconds) to wait for the connection to be
            accepted.

        version (str): Specific version to launch if multiple versions present.

        x64 (bool): `True` for 64-bit version, `False` for 32-bit version.

        settings (dict): Setting values to set immediately upon startup.

        load_user_profile (bool): Set to False to disable loading user profile.

        minimum (str): Minimum allowed PSCAD version to run (default '5.0')

        maximum (str): Maximum allowed PSCAD version to run (default: unlimited)

        allow_alpha (bool): Allow launching an "alpha" version of PSCAD.

        allow_beta (bool): Allow launching a "beta" version of PSCAD.

        extra_args (list[str]): Additional command-line arguments

        **options: Additional keyword=value options

    Returns:
        PSCAD: The PSCAD application proxy object

    Example::

        import mhi.pscad
        pscad = mhi.pscad.launch()
        pscad.load('myproject.pscx')

    .. versionchanged:: 2.4
        added `extra_args` parameter.
    """

    from mhi.common import process # pylint: disable=import-outside-toplevel

    options = dict(OPTIONS, **options) if OPTIONS else options

    args = ["{exe}", "/startup:au", "/port:{port}"]

    if splash is not None:
        args.append("/splash:{}".format(str(splash).lower()))

    if load_user_profile is not None:
        args.append("/load-user-profile:{}".format(load_user_profile))

    if silence is not None:
        args.append("/silence:{}".format(str(silence).lower()))

    if extra_args:
        args.extend(extra_args)

    if not options.get('exe', None):
        options['exe'] = process.find_exe('PSCAD', version, x64,
                                          minimum, maximum,
                                          allow_alpha, allow_beta)
        if not options['exe']:
            raise ValueError("Unable to find required version")

    if not os.path.isfile(options['exe']):
        raise ValueError("No such executable: " + options['exe'])

    if not port:
        port = process.unused_tcp_port()
        _LOG.info("Automation server port: %d", port)

    process.launch(*args, port=port, minimize=minimize, **options)

    app = connect(port=port, timeout=timeout)

    # Legacy launch keyword arguments:
    for key in ('certificate', 'fortran_version', 'matlab_version'):
        if key in options:
            if settings is None:
                settings = {}
            settings[key] = options[key]
            warnings.warn(
                'Support for keyword parameter "{0}={1!r}" will be removed.\n'
                'Use "settings={{{0!r}: {1!r}}}" to specify setting value'
                .format(key, options[key]), DeprecationWarning, stacklevel=2)

    # First things first: if any settings have been given, set them.
    if settings:
        app.settings(**settings)

    return app


#===============================================================================
# PSCAD Versions
#===============================================================================

def versions() -> List[Tuple[str, bool]]:
    """
    Find the installed versions of PSCAD

    Returns:
        List[Tuple]: List of tuples of version and bit-size
    """

    from mhi.common import process # pylint: disable=import-outside-toplevel

    return process.versions('PSCAD')


#===============================================================================
# Fortran/Matlab Versions
#===============================================================================

def _product_list():
    if 'cache' not in _product_list.__dict__:

        product_list = {'pscad': {}, 'fortran': {}, 'matlab': {}}

        file = r"~public\Documents\Manitoba HVDC Research Centre\ATS\ProductList.xml"
        file = os.path.expanduser(file)
        if os.path.isfile(file):
            doc = _ET.parse(file)
            root = doc.getroot()
            for paramlist in root:
                paramlist_name = paramlist.get('name')
                try:
                    params = product_list[paramlist_name]
                except KeyError:
                    params = product_list[paramlist_name] = {}

                for param in paramlist:
                    name = param.get('name')
                    value = param.get('value', '')
                    params[name] = value

        _product_list.cache = product_list

    return _product_list.cache


def fortran_versions() -> List[str]:
    """
    Find the installed versions of Fortran

    Returns:
        List[str]: List of Fortran versions
    """

    return list(_product_list()['fortran'].keys())


def matlab_versions() -> List[str]:
    """
    Find the installed versions of Matlab

    Returns:
        List[str]: List of Matlab versions
    """

    return list(_product_list()['matlab'].keys())


def fortran_codec():
    """
    Coder/Decoder for FORTRAN version strings
    """

    return MapCodec(_product_list()['fortran'])


def matlab_codec():
    """
    Coder/Decoder for Matlab version strings
    """

    mapping = _product_list()['matlab']
    if not mapping:
        mapping = {'':''}
    return MapCodec(mapping)
