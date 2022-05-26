from ..test import ExperimentTest, Results
from . import spm
from . import ftm_quantification as ftm_quant


class HasCorrectItems(ftm_quant.HasCorrectItems):
    __doc__ = ftm_quant.HasCorrectItems.__doc__
    __doc__ = __doc__.replace('FTM_QUANTIFICATION', 'FDG_QUANTIFICATION')

    passing = 'BBRCDEV_E00745',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FDG_QUANTIFICATION'
    expected_items = ['quantification_results.csv',
                      'static_pet.nii.gz',
                      'wstatic_pet_scaled_cgm.nii.gz',
                      'wstatic_pet_scaled_pons.nii.gz',
                      'wstatic_pet_scaled_wcbs.nii.gz',
                      'wstatic_pet_scaled_wc.nii.gz',
                      'wstatic_pet_scaled_wm.nii.gz',
                      'wstatic_pet_scaled_vermis.nii.gz',
                      'optimized_static_pet.nii.gz',
                      'woptimized_static_pet_scaled_cgm.nii.gz',
                      'woptimized_static_pet_scaled_pons.nii.gz',
                      'woptimized_static_pet_scaled_wcbs.nii.gz',
                      'woptimized_static_pet_scaled_wc.nii.gz',
                      'woptimized_static_pet_scaled_wm.nii.gz',
                      'woptimized_static_pet_scaled_vermis.nii.gz',
                      'pyscript_coregister.m',
                      'pyscript_coregister_icbm152.m',
                      'pyscript_newsegment.m',
                      'pyscript_normalize12.m',
                      'pyscript_realign.m',
                      'pyscript_setorigin.m',
                      'pyscript_smooth.m']


class QuantificationResultsShape(ftm_quant.QuantificationResultsShape):
    __doc__ = ftm_quant.QuantificationResultsShape.__doc__
    __doc__ = __doc__.replace('FTM_QUANTIFICATION', 'FDG_QUANTIFICATION')
    __doc__ = __doc__.replace('2010 rows', '2436 rows')

    passing = 'BBRCDEV_E00745',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FDG_QUANTIFICATION'
    csv_shape = (2436, 6)


class HasCorrectFSLVersion(ftm_quant.HasCorrectFSLVersion):
    __doc__ = ftm_quant.HasCorrectFSLVersion.__doc__
    __doc__ = __doc__.replace('FTM_QUANTIFICATION', 'FDG_QUANTIFICATION')

    passing = 'BBRCDEV_E00745',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FDG_QUANTIFICATION'


class HasCorrectSPMVersion(spm.HasCorrectSPMVersion):
    __doc__ = spm.HasCorrectSPMVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'FDG_QUANTIFICATION')

    passing = 'BBRCDEV_E00745',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FDG_QUANTIFICATION'


class HasCorrectMatlabVersion(spm.HasCorrectMatlabVersion):
    __doc__ = spm.HasCorrectMatlabVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'FDG_QUANTIFICATION')

    passing = 'BBRCDEV_E00745',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FDG_QUANTIFICATION'


class HasCorrectOSVersion(spm.HasCorrectOSVersion):
    __doc__ = spm.HasCorrectOSVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'FDG_QUANTIFICATION')

    passing = 'BBRCDEV_E00745',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FDG_QUANTIFICATION'
