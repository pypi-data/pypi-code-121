import inspect
import sys
import os
import pandas as pd
from pathlib import Path

from weaveio.hierarchy import Multiple, Hierarchy, OneOf, Optional
from weaveio.opr3.hierarchy import Spectrum, Author, APS, Measurement, \
    Single, FibreTarget, Exposure, Stack, OB, Superstack, \
    OBSpec, Supertarget, WeaveTarget, _predicate, MCMCMeasurement, Line, SpectralIndex, RedshiftMeasurement, Spectrum1D, ArrayHolder
from weaveio.opr3.l1 import L1Spectrum, L1SingleSpectrum, L1StackSpectrum, L1SupertargetSpectrum, L1SuperstackSpectrum, L1StackedSpectrum

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
gandalf_lines = pd.read_csv(HERE / 'expected_lines.csv', sep=' ')
gandalf_indices = pd.read_csv(HERE / 'expected_line_indices.csv', sep=' ')
# gandalf_lines['name'] = gandalf_lines['name'].str.replace('[', '').str.replace(']', '').str.lower()
gandalf_line_names = (gandalf_lines['name'] + '_' + gandalf_lines['lambda'].apply(lambda x: f'{x:.2f}')).values.tolist()
gandalf_index_names = gandalf_indices['name'].values.tolist()


class L2(Hierarchy):
    is_template = True


class IngestedSpectrum(Spectrum1D):
    """
    An ingested spectrum is one which is a slightly modified version of an L1 spectrum
    """
    parents = [L1Spectrum, APS]
    identifier_builder = ['l1_spectrum', 'aps']
    products = ['flux', 'error', 'wvl']


class IvarIngestedSpectrum(IngestedSpectrum):
    products = ['flux', 'ivar', 'wvl']


class CombinedIngestedSpectrum(IngestedSpectrum):
    parents = [Multiple(L1Spectrum, 1, 3), APS]
    identifier_builder = ['l1_spectra', 'aps']


class IvarCombinedIngestedSpectrum(CombinedIngestedSpectrum):
    products = ['flux', 'ivar', 'wvl']


class MaskedCombinedIngestedSpectrum(CombinedIngestedSpectrum):
    products = ['flux', 'error', 'logwvl', 'goodpix']


class ModelSpectrum(Spectrum1D):
    is_template = True
    parents = [OneOf(IngestedSpectrum, one2one=True)]
    identifier_builder = ['ingested_spectrum']
    products = ['flux']


class CombinedModelSpectrum(ModelSpectrum):
    parents = [OneOf(CombinedIngestedSpectrum, one2one=True)]
    identifier_builder = ['combined_ingested_spectrum']


# This allows us to use 'clean' to talk about the clean model or clean spectrum
# IngestedSpectrum->ModelSpectrum->CleanModelSpectrum
# IngestedSpectrum->CleanIngestedSpectrum

class GandalfSpectrum(Spectrum1D):
    is_template = True


class GandalfModelSpectrum(CombinedModelSpectrum, GandalfSpectrum):
    pass

class GandalfEmissionModelSpectrum(GandalfModelSpectrum, GandalfSpectrum):
    parents = [OneOf(GandalfModelSpectrum, one2one=True)]
    identifier_builder = ['gandalf_model_spectrum']

class GandalfCleanModelSpectrum(GandalfModelSpectrum, GandalfSpectrum):
    parents = [OneOf(GandalfModelSpectrum, one2one=True)]
    identifier_builder = ['gandalf_model_spectrum']

class GandalfCleanIngestedSpectrum(GandalfModelSpectrum, GandalfSpectrum):
    parents = [OneOf(CombinedIngestedSpectrum, one2one=True)]
    identifier_builder = ['combined_ingested_spectrum']


class Fit(Hierarchy):
    """
    A fit is the result of applying fitting_software to an ingested spectrum
    In the case of combined spectra being available, there is only one ingested spectrum input
    otherwise, there are more.
    """
    is_template = True
    parents = [Multiple(ModelSpectrum, 0, 3, one2one=True), Optional(CombinedModelSpectrum, one2one=True)]


class RedshiftArray(ArrayHolder):
    factors = ['value', 'start', 'end', 'step']
    identifier_builder = ['start', 'end', 'step']


class Template(Fit):
    parents = [Multiple(ModelSpectrum, 1, 3, one2one=True), Optional(CombinedModelSpectrum, one2one=True)]
    children = [OneOf(RedshiftArray, one2one=True)]
    factors = ['chi2_array', 'name']
    identifier_builder = ['model_spectra', 'combined_model_spectrum', 'name']


class Redrock(Fit):
    factors = ['class', 'subclass', 'snr', 'chi2', 'deltachi2', 'ncoeff', 'coeff',
               'npixels', 'srvy_class', 'z', 'zerr', 'zwarn']
    parents = [Multiple(ModelSpectrum, 1, 3, one2one=True), Optional(CombinedModelSpectrum, one2one=True)]
    template_names = ['galaxy', 'qso', 'star_a', 'star_b', 'star_cv', 'star_f', 'star_g', 'star_k', 'star_m', 'star_wd']
    parents += [OneOf(Template, idname=x, one2one=True) for x in template_names]
    identifier_builder = ['model_spectra', 'combined_model_spectrum']


class RVSpecfit(Fit):
    singular_name = 'rvspecfit'
    parents = [Multiple(ModelSpectrum, 1, 3, one2one=True), Optional(CombinedModelSpectrum, one2one=True)]
    factors = Fit.factors + ['skewness', 'kurtosis', 'vsini', 'snr', 'chi2_tot']
    factors += Measurement.as_factors('vrad', 'logg', 'teff', 'feh', 'alpha')
    identifier_builder = ['model_spectra', 'combined_model_spectrum']


class Ferre(Fit):
    parents = [Multiple(ModelSpectrum, 1, 3, one2one=True), Optional(CombinedModelSpectrum, one2one=True)]
    factors = Fit.factors + ['snr', 'chi2_tot', 'flag']
    factors += Measurement.as_factors('micro', 'logg', 'teff', 'feh', 'alpha', 'elem')
    identifier_builder = ['model_spectra', 'combined_model_spectrum']


class Gandalf(Fit):
    plural_name = 'gandalfs'
    parents = [OneOf(GandalfModelSpectrum, one2one=True)]
    factors = Fit.factors + ['fwhm_flag']
    factors += Line.as_factors(*gandalf_line_names) + SpectralIndex.as_factors(*gandalf_index_names)
    identifier_builder = ['gandalf_model_spectrum']


class PPXF(Fit):
    parents = [OneOf(CombinedModelSpectrum, one2one=True)]
    factors = Fit.factors + MCMCMeasurement.as_factors('v', 'sigma', 'h3', 'h4', 'h5', 'h6') + Measurement.as_factors('zcorr')
    identifier_builder = ['combined_model_spectrum']


class L2Product(L2):
    is_template = True
    parents = [Multiple(L1Spectrum, 2, 3), APS,
               OneOf(Redrock, one2one=True), Optional(RVSpecfit, one2one=True),
               Optional(Ferre, one2one=True), Optional(PPXF, one2one=True), Optional(Gandalf, one2one=True)]


# L2 data products are formed from 2 or more L1 data products from different arms (red, blue, or green)
# L2 singles can only be formed from 2 single L1 data products
# Since an OB has a fixed instrument configuration, L2 stacks can only be formed from 2 L1 stacks
# However, APS tries to create the widest and deepest data possible, so L2 superstacks are not limit in their L1 spectra provenance

class L2Single(L2Product, Single):
    """
    An L2 data product resulting from two or sometimes three single L1 spectra.
    The L2 data products contain information generated by APS namely redshifts, emission line properties and model spectra.

    """
    singular_name = 'l2single'
    parents = L2Product.parents[1:] + [Multiple(L1SingleSpectrum, 2, 2, constrain=(FibreTarget, Exposure))]
    identifier_builder = ['l1single_spectra', 'fibre_target', 'exposure']


class L2Stack(L2Product, Stack):
    """
    An L2 data product resulting from two or sometimes three stacked/single L1 spectra.
    The L2 data products contain information generated by APS namely redshifts, emission line properties and model spectra.
    """
    singular_name = 'l2stack'
    parents = L2Product.parents[1:] + [Multiple(L1StackSpectrum, 2, 2, constrain=(FibreTarget, OB))]
    identifier_builder = ['l1stack_spectra', 'fibre_target', 'ob']


class L2Superstack(L2Product, Superstack):
    """
    An L2 data product resulting from two or sometimes three super-stacked/stacked/single L1 spectra.
    The L2 data products contain information generated by APS namely redshifts, emission line properties and model spectra.
    """
    singular_name = 'l2superstack'
    parents = L2Product.parents[1:] + [Multiple(L1StackedSpectrum, 2, 3, constrain=(FibreTarget, OBSpec))]
    identifier_builder = ['l1stacked_spectra', 'fibre_target', 'obspec']


class L2Supertarget(L2Product, Supertarget):
    """
    An L2 data product resulting from two or sometimes three supertarget L1 spectra.
    The L2 data products contain information generated by APS namely redshifts, emission line properties and model spectra.
    """
    singular_name = 'l2supertarget'
    parents = L2Product.parents[1:] + [Multiple(L1SupertargetSpectrum, 2, 3, constrain=(WeaveTarget,))]
    identifier_builder = ['l1supertarget_spectra', 'weave_target']


hierarchies = [i[-1] for i in inspect.getmembers(sys.modules[__name__], _predicate)]
