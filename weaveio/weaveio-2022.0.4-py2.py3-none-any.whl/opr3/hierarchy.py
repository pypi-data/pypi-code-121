"""
Hierarchies are defined like so:

class Name(Type):
    singular_name = 'custom_singular_name'
    plural_name = 'custom_plural_name'
    idname = 'the_name_of_the_unique_attribute_of_this_Object'
    identifier_builder = [list_of_attributes_or_objects_that_define_uniqueness]
    factors = ['attribute1', 'attribute2']
    products = ['name_of_product']
    parents = [required_object_that_comes_before]
    children = [required_object_that_comes_after]

if an object of type O requires n parents of type P then this is equivalent to defining that instances of those behave as:
    parent-(n)->object (1 object has n parents of type P)
    it implicitly follows that:
        object--(m)-parent (each of object's parents of type P can be used by an unknown number `m` of objects of type O = many to one)
if an object of type O requires n children of type C then this is equivalent to defining that instances of those behave as:
    object-(n)->child (1 object has n children of type C)
    it implicitly follows that:
        child-[has 1]->Object (each child has maybe 1 parent of type O)

A child does not need to require a parent at instantiation

You can modify the first relation in each of the above by using:
    Multiple(parent/child, minnumber, maxnumber)
    One2One(parent/child) - makes a reciprocal one to one relationship
    Optional(parent/child) == Multiple(parent/Child, 0, 1)

"""
import inspect
import sys

import numpy as np

from weaveio.config_tables import progtemp_config
from weaveio.hierarchy import Hierarchy, Multiple, OneOf, Optional

class ArrayHolder(Hierarchy):
    is_template = True

class WavelengthHolder(ArrayHolder):
    singular_name = 'wavelength_holder'
    factors = ['wvl', 'cd1_1', 'crval1', 'naxis1']
    identifier_builder = ['cd1_1', 'crval1', 'naxis1']

class Measurement(Hierarchy):
    factors = ['value', 'error']
    indexes = ['value']


class Magnitude(Measurement):
    pass


class Author(Hierarchy):
    is_template = True


class CASU(Author):
    """
    CASU is the pipeline that will produce the L1 and Raw data files and spectra.
    The version of CASU that produces these files may change without warning and files may be duplicated.
    This CASU object breaks that potential degeneracy.
    """
    idname = 'id'


class APS(Author):
    """
    APS is the pipeline that will produce the L2 data files and model spectra.
    The version of APS that produces these files may change without warning and files may be duplicated.
    This APS object breaks that potential degeneracy.
    """
    idname = 'version'


class System(Author):
    idname = 'version'


class ArmConfig(Hierarchy):
    """
    An ArmConfig is the entire configuration of one arm of the WEAVE spectrograph.
    The ArmConfig is therefore a subset of the ProgTemp code and there are multiple ways to identify
    one:
    - resolution can be "high" or "low"
    - vph is the number of the grating [1=lowres, 2=highres, 3=highres(green)]
    - camera can be 'red' or 'blue'
    - colour can be 'red', 'blue', or 'green'
    """
    factors = ['resolution', 'vph', 'camera', 'colour', 'colour_code']
    identifier_builder = ['resolution', 'vph', 'camera']

    def __init__(self, tables=None, **kwargs):
        if not kwargs.get('do_not_create', False):
            if kwargs['vph'] == 3 and kwargs['camera'] == 'blue':
                kwargs['colour'] = 'green'
            else:
                kwargs['colour'] = kwargs['camera']
            kwargs['colour_code'] = kwargs['colour'][0].upper()
        super().__init__(tables=tables, **kwargs)

    @classmethod
    def from_progtemp_code(cls, progtemp_code):
        config = progtemp_config.loc[progtemp_code[0]]
        red = cls(resolution=str(config.resolution), vph=int(config.red_vph), camera='red')
        blue = cls(resolution=str(config.resolution), vph=int(config.blue_vph), camera='blue')
        return red, blue


class Obstemp(Hierarchy):
    """
    Whilst ProgTemp deals with "how" a target is observed, OBSTEMP deals with "when" a target is observed,
    namely setting the observational constraints required to optimally extract scientific information from the observation.
    The ProgTemp is made up of maxseeing, mintrans (transparency), minelev (elevation), minmoon, minsky and
    each combination is given a valid code, where each letter corresponds to one of those settings.
    """
    factors = [
        'maxseeing', 'mintrans', 'minelev', 'minmoon', 'minsky', 'maxairmass',
        'maxseeing_grade', 'mintrans_grade', 'minelev_grade', 'minmoon_grade', 'minsky_grade',
    ]
    idname = 'code'
    seeings = {'A': 0.7, 'B': 0.8, 'C': 0.9, 'D': 1.0, 'E': 1.1, 'F': 1.2, 'G': 1.3, 'H': 1.4, 'I': 1.5,
               'J': 1.6, 'K': 1.7, 'L': 1.8, 'M': 1.9, 'N': 2.0, 'O': 2.1, 'P': 2.2, 'Q': 2.3, 'R': 2.4,
               'S': 2.5, 'T': 2.6, 'U': 2.7, 'V': 2.8, 'W': 2.9, 'X': 3.0}
    transparencies = {'A': 0.8, 'B': 0.7, 'C': 0.6, 'D': 0.5, 'E': 0.4}
    elevs = {'A': 50.28, 'B': 45.58, 'C': 41.81, 'D': 35.68, 'E': 33.75, 'F': 25.00}
    airmasses = {'A': 1.3, 'B': 1.4, 'C': 1.5, 'D': 1.6, 'E': 1.8, 'F': 2.4}
    moons = {'A': 90, 'B': 70, 'C': 50, 'D': 30, 'E': 0}
    brightnesses = {'A': 21.7, 'B': 21.5, 'C': 21.0, 'D': 20.5, 'E': 19.6, 'F': 18.5, 'G': 17.7}

    @classmethod
    def from_header(cls, header):
        names = [f.lower() for f in cls.factors[:-1]]
        obstemp_code = list(header['OBSTEMP'])
        data = {n+'_grade': v for v, n in zip(obstemp_code, names)}
        data['maxseeing'] = cls.seeings[data['maxseeing_grade']]
        data['mintrans'] = cls.transparencies[data['mintrans_grade']]
        data['minelev'] = cls.elevs[data['minelev_grade']]
        data['maxairmass'] = cls.airmasses[data['minelev_grade']]
        data['minmoon'] = cls.moons[data['minmoon_grade']]
        data['minsky'] = cls.brightnesses[data['minsky_grade']]
        return cls(code=header['OBSTEMP'], **data)


class Survey(Hierarchy):
    """
    A Survey is one of the official Surveys of WEAVE. WL is one of them.
    """
    idname = 'name'


class WeaveTarget(Hierarchy):
    """
    A WeaveTarget is the disambiguated target to which all targets submitted by surveys belong.
    The "cname" of a weavetarget will be formed of the ra and dec of the submitted target.
    """
    idname = 'cname'


class Fibre(Hierarchy):
    """
    A WEAVE spectrograph fibre
    """
    idname = 'id'


class Subprogramme(Hierarchy):
    """
    A submitted programme of observation which was written by multiple surveys.
    """
    parents = [Multiple(Survey)]
    factors = ['name']
    idname = 'id'


class SurveyCatalogue(Hierarchy):
    """
    A catalogue which was submitted by a subprogramme.
    """
    parents = [Subprogramme]
    factors = ['name']
    idname = 'id'


class SurveyTarget(Hierarchy):
    """
    A target which was submitted by a subprogramme contained within a catalogue. This is likely
    the target you want if you not linking observations between subprogrammes.
    targname is optional for MOS observations
    """
    parents = [SurveyCatalogue, WeaveTarget]
    factors = ['targid', 'targname', 'targra', 'targdec', 'epoch', 'targuse', 'targprog',
               'targclass', 'targpmra', 'targpdec', 'targparal', 'targrio'] \
              + Magnitude.as_factors('g', 'r', 'i', 'gg', 'bp', 'rp', prefix='mag_')
    identifier_builder = ['weave_target', 'survey_catalogue', 'targid', 'targra', 'targdec', 'targuse']


class InstrumentConfiguration(Hierarchy):
    """
    The WEAVE instrument can be configured into MOS/LIFU/mIFU modes and the spectral binning in pixels.
    InstrumentConfiguration holds the mode, binning, and is linked to an ArmConfig.
    """
    factors = ['mode', 'binning']
    parents = [Multiple(ArmConfig, 2, 2)]
    identifier_builder = ['arm_configs', 'mode', 'binning']


class Progtemp(Hierarchy):
    """
    The ProgTemp code is an integral part of describing a WEAVE target.
    This parameter encodes the requested instrument configuration, OB length, exposure time,
    spectral binning, cloning requirements and probabilistic connection between these clones.
    The ProgTemp is therefore formed from instrumentconfiguration, length, and an exposure_code.
    """
    parents = [InstrumentConfiguration]
    factors = ['length', 'exposure_code', 'code']
    identifier_builder = ['instrument_configuration'] + factors

    @classmethod
    def from_progtemp_code(cls, progtemp_code):
        progtemp_code = progtemp_code.split('.')[0]
        progtemp_code_list = list(map(int, progtemp_code))
        configs = ArmConfig.from_progtemp_code(progtemp_code_list)
        mode = progtemp_config.loc[progtemp_code_list[0]]['mode']
        binning = progtemp_code_list[3]
        config = InstrumentConfiguration(arm_configs=configs, mode=mode, binning=binning)
        exposure_code = progtemp_code[2:4]
        length = progtemp_code_list[1]
        return cls(code=progtemp_code, length=length, exposure_code=exposure_code,
                   instrument_configuration=config)


class FibreTarget(Hierarchy):
    """
    A fibretarget is the combination of fibre and surveytarget which is created after submission when
    the fibres are assigned.
    This object describes where the fibre is placed and what its status is.
    """
    factors = ['fibrera', 'fibredec', 'status', 'orientation', 'nretries', 'xposition', 'yposition',
               'targx', 'targy']
    parents = [Fibre, SurveyTarget]
    identifier_builder = ['fibre', 'survey_target', 'xposition', 'yposition']


class OBSpec(Hierarchy):
    """
    When an xml observation specification is submitted to WEAVE, an OBSpec is created containing all
    the information about when and how to observe.
    When actually observing them, an "OB" is create with its own unique obid.
    """
    singular_name = 'obspec'
    factors = ['title']
    parents = [Obstemp, Progtemp, Multiple(FibreTarget, one2one=True),  # each OB has a defined number of fibre_targets
               Multiple(SurveyCatalogue), Multiple(Subprogramme), Multiple(Survey)]
    idname = 'xml'  # this is CAT-NAME in the header not CATNAME, annoyingly no hyphens allowed


class OB(Hierarchy):
    """
    An OB is an "observing block" which is essentially a realisation of an OBSpec.
    Many OBs can share the same xml OBSpec which describes how to do the observations.
    """
    idname = 'id'  # This is globally unique by obid
    factors = ['mjd']
    parents = [OBSpec]


class Exposure(Hierarchy):
    """
    An exposure is one observation of one set of targets for a given configuration.
    WEAVE is structured such that an exposure is actually two sets of data, one from each arm.
    These are called runs.
    """
    idname = 'mjd'  # globally unique
    factors = ['exptime', 'seeingb', 'seeinge', 'windspb', 'windspe', 'telhumb', 'telhume',
               'winddirb', 'winddire', 'airmass',
               'teltempb', 'teltempe', 'skybrtel', 'observer', 'obstype']
    parents = [OB, CASU, System]


    @classmethod
    def from_header(cls, ob, header):
        factors = {f: header.get(f) for f in cls.factors}
        factors['mjd'] = np.round(float(header['MJD-OBS']), 6)
        factors['obstype'] = header['obstype'].lower()
        casu = CASU(id=header.get('casuvers', header.get('casuid')))
        sys = System(version=header['sysver'])
        return cls(ob=ob, casu=casu, system=sys, **factors)


class Spectrum(Hierarchy):
    is_template = True
    plural_name = 'spectra'


class Spectrum1D(Spectrum):
    is_template = True
    parents = [WavelengthHolder]
    products = ['flux', 'ivar']


class Spectrum2D(Spectrum):
    is_template = True


class Run(Hierarchy):
    """
    A run is one observation of a set of targets for a given configuration in a specific arm (red or blue).
    A run belongs to an exposure, which always consists of one or two runs (per arm).
    """
    idname = 'id'
    parents = [Exposure, ArmConfig]
    children = [Optional('self', idname='adjunct')]


class RawSpectrum(Spectrum2D):
    """
    A 2D spectrum containing two counts arrays, this is not wavelength calibrated.
    """
    parents = [CASU, OneOf(Run, one2one=True)]
    products = ['counts1', 'counts2']
    children = [Optional('self', idname='adjunct')]
    identifier_builder = ['casu', 'run']


class Single(Hierarchy):
    is_template = True


class Stacked(Hierarchy):
    is_template = True


class Stack(Stacked):
    is_template = True


class Superstack(Stacked):
    is_template = True


class Supertarget(Stacked):
    is_template = True


class MCMCMeasurement(Measurement):
    is_template = True
    factors = Measurement.factors + ['formal_error']


class Line(Measurement):
    is_template = True
    factors = ['aon']
    factors += Measurement.as_factors('flux', 'redshift', 'sigma', 'ebmv', 'amp')
    indexes = []


class SpectralIndex(Measurement):
    is_template = True


class RedshiftMeasurement(Measurement):
    is_template = True
    factors = Measurement.factors + ['warn']



class MeanFlux(Hierarchy):
    singular_name = 'mean_flux'
    plural_name = 'mean_fluxes'
    idname = 'band'
    factors = ['value']


def _predicate(o):
    if inspect.isclass(o):
        return issubclass(o, Hierarchy)
    return False
hierarchies = [i[-1] for i in inspect.getmembers(sys.modules[__name__], _predicate)]
