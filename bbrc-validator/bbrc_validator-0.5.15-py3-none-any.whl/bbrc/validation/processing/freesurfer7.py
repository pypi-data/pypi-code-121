from ..test import ExperimentTest, Results
from . import freesurfer
from nisnap.utils import aseg


class HasCorrectItems(freesurfer.HasCorrectItems):
    __doc__ = freesurfer.HasCorrectItems.__doc__.replace('FREESURFER6',
                                                         'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'
    hippo_items = ['lh.hippoSfVolumes-{}.v21.txt',
                   'rh.hippoSfVolumes-{}.v21.txt',
                   'lh.amygNucVolumes-{}.v21.txt',
                   'rh.amygNucVolumes-{}.v21.txt',
                   'lh.hippoAmygLabels-{}.v21.HBT.FSvoxelSpace.mgz',
                   'rh.hippoAmygLabels-{}.v21.HBT.FSvoxelSpace.mgz',
                   'lh.hippoAmygLabels-{}.v21.HBT.mgz',
                   'rh.hippoAmygLabels-{}.v21.HBT.mgz',
                   'lh.hippoAmygLabels-{}.v21.CA.FSvoxelSpace.mgz',
                   'rh.hippoAmygLabels-{}.v21.CA.FSvoxelSpace.mgz',
                   'lh.hippoAmygLabels-{}.v21.FS60.FSvoxelSpace.mgz',
                   'rh.hippoAmygLabels-{}.v21.FS60.FSvoxelSpace.mgz',
                   'lh.hippoAmygLabels-{}.v21.mgz',
                   'rh.hippoAmygLabels-{}.v21.mgz',
                   'lh.hippoAmygLabels-{}.v21.CA.mgz',
                   'rh.hippoAmygLabels-{}.v21.CA.mgz',
                   'lh.hippoAmygLabels-{}.v21.FSvoxelSpace.mgz',
                   'rh.hippoAmygLabels-{}.v21.FSvoxelSpace.mgz',
                   'lh.hippoAmygLabels-{}.v21.FS60.mgz',
                   'rh.hippoAmygLabels-{}.v21.FS60.mgz']
    monomodal_items = ['hipposubfields.lh.T1.v21.stats',
                       'hipposubfields.rh.T1.v21.stats',
                       'amygdalar-nuclei.lh.T1.v21.stats',
                       'amygdalar-nuclei.rh.T1.v21.stats',
                       'hippocampal-subfields-T1.log']
    multimodal_items = ['{}.FSspace.mgz',
                        'T1_to_{}.v21.lta',
                        'T1_to_{}.v21.QC.gif',
                        'T1_to_{}.v21.info',
                        'hipposubfields.lh.T2.v21.{}.stats',
                        'hipposubfields.rh.T2.v21.{}.stats',
                        'amygdalar-nuclei.lh.T2.v21.{}.stats',
                        'amygdalar-nuclei.rh.T2.v21.{}.stats',
                        'hippocampal-subfields-T2.{}.log']


class HasCorrectFreeSurferVersion(freesurfer.HasCorrectFreeSurferVersion):

    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'
    freesurfer_version = 'freesurfer-linux-centos7_x86_64-7.1.1-20200723-8b40551'
    __doc__ = freesurfer.HasCorrectFreeSurferVersion.__doc__.replace('FREESURFER6',
                                                                     'FREESURFER7')
    __doc__ = __doc__.split('(expected version')[0]
    __doc__ += '(expected version: %s).' % freesurfer_version


class HasCorrectOSVersion(freesurfer.HasCorrectOSVersion):

    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'
    kernel_version = '4.4.120-92.70-default'
    __doc__ = freesurfer.HasCorrectOSVersion.__doc__.replace('FREESURFER6',
                                                             'FREESURFER7')
    __doc__ = __doc__.split('(expected version')[0]
    __doc__ += '(expected version: %s).' % kernel_version


class IsT1OnlyHippocampalSegmentation(freesurfer.IsT1OnlyHippocampalSegmentation):
    __doc__ = freesurfer.IsT1OnlyHippocampalSegmentation.__doc__.replace('FREESURFER6',
                                                                         'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'
    items = ['lh.hippoSfVolumes-T1.v21.txt',
             'rh.hippoSfVolumes-T1.v21.txt',
             'lh.amygNucVolumes-T1.v21.txt',
             'rh.amygNucVolumes-T1.v21.txt',
             'lh.hippoAmygLabels-T1.v21.HBT.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1.v21.HBT.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1.v21.HBT.mgz',
             'rh.hippoAmygLabels-T1.v21.HBT.mgz',
             'lh.hippoAmygLabels-T1.v21.CA.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1.v21.CA.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1.v21.FS60.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1.v21.FS60.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1.v21.mgz',
             'rh.hippoAmygLabels-T1.v21.mgz',
             'lh.hippoAmygLabels-T1.v21.CA.mgz',
             'rh.hippoAmygLabels-T1.v21.CA.mgz',
             'lh.hippoAmygLabels-T1.v21.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1.v21.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1.v21.FS60.mgz',
             'rh.hippoAmygLabels-T1.v21.FS60.mgz',
             'hipposubfields.lh.T1.v21.stats',
             'hipposubfields.rh.T1.v21.stats',
             'amygdalar-nuclei.lh.T1.v21.stats',
             'amygdalar-nuclei.rh.T1.v21.stats']


class IsT1T2HippocampalSegmentation(freesurfer.IsT1T2HippocampalSegmentation):
    __doc__ = freesurfer.IsT1T2HippocampalSegmentation.__doc__.replace('FREESURFER6',
                                                                       'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'
    items = ['T1T2.FSspace.mgz',
             'lh.hippoSfVolumes-T1-T1T2.v21.txt',
             'rh.hippoSfVolumes-T1-T1T2.v21.txt',
             'lh.amygNucVolumes-T1-T1T2.v21.txt',
             'rh.amygNucVolumes-T1-T1T2.v21.txt',
             'lh.hippoAmygLabels-T1-T1T2.v21.HBT.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.HBT.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1T2.v21.HBT.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.HBT.mgz',
             'lh.hippoAmygLabels-T1-T1T2.v21.CA.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.CA.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1T2.v21.FS60.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.FS60.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1T2.v21.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.mgz',
             'lh.hippoAmygLabels-T1-T1T2.v21.CA.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.CA.mgz',
             'lh.hippoAmygLabels-T1-T1T2.v21.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1T2.v21.FS60.mgz',
             'rh.hippoAmygLabels-T1-T1T2.v21.FS60.mgz',
             'hipposubfields.lh.T2.v21.T1T2.stats',
             'hipposubfields.rh.T2.v21.T1T2.stats',
             'amygdalar-nuclei.lh.T2.v21.T1T2.stats',
             'amygdalar-nuclei.rh.T2.v21.T1T2.stats']


class IsT1IRHippocampalSegmentation(freesurfer.IsT1IRHippocampalSegmentation):
    __doc__ = freesurfer.IsT1IRHippocampalSegmentation.__doc__.replace('FREESURFER6',
                                                                       'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'
    items = ['T1IR.FSspace.mgz',
             'lh.hippoSfVolumes-T1-T1IR.v21.txt',
             'rh.hippoSfVolumes-T1-T1IR.v21.txt',
             'lh.amygNucVolumes-T1-T1IR.v21.txt',
             'rh.amygNucVolumes-T1-T1IR.v21.txt',
             'lh.hippoAmygLabels-T1-T1IR.v21.HBT.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.HBT.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1IR.v21.HBT.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.HBT.mgz',
             'lh.hippoAmygLabels-T1-T1IR.v21.CA.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.CA.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1IR.v21.FS60.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.FS60.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1IR.v21.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.mgz',
             'lh.hippoAmygLabels-T1-T1IR.v21.CA.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.CA.mgz',
             'lh.hippoAmygLabels-T1-T1IR.v21.FSvoxelSpace.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.FSvoxelSpace.mgz',
             'lh.hippoAmygLabels-T1-T1IR.v21.FS60.mgz',
             'rh.hippoAmygLabels-T1-T1IR.v21.FS60.mgz',
             'hipposubfields.lh.T2.v21.T1IR.stats',
             'hipposubfields.rh.T2.v21.T1IR.stats',
             'amygdalar-nuclei.lh.T2.v21.T1IR.stats',
             'amygdalar-nuclei.rh.T2.v21.T1IR.stats']


class IsT2MultispectralHippoSegRunnable(freesurfer.IsT2MultispectralHippoSegRunnable):
    __doc__ = freesurfer.IsT2MultispectralHippoSegRunnable.__doc__.replace('FREESURFER6',
                                                                           'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'


class IsIRMultispectralHippoSegRunnable(freesurfer.IsIRMultispectralHippoSegRunnable):
    __doc__ = freesurfer.IsIRMultispectralHippoSegRunnable.__doc__.replace('FREESURFER6',
                                                                           'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'


class IsFreeSurferTimewiseConsistent(freesurfer.IsFreeSurferTimewiseConsistent):
    __doc__ = freesurfer.IsFreeSurferTimewiseConsistent.__doc__.replace('FREESURFER6',
                                                                        'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02872',
    resource_name = 'FREESURFER7'


class ReconAllAsegSnapshot(freesurfer.ReconAllAsegSnapshot):
    __doc__ = freesurfer.ReconAllAsegSnapshot.__doc__.replace('FREESURFER6',
                                                              'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E00754',  # has no FreeSurfer resource
    resource_name = 'FREESURFER7'


class ReconAllAparcSnapshot(freesurfer.ReconAllAparcSnapshot):
    __doc__ = freesurfer.ReconAllAparcSnapshot.__doc__.replace('FREESURFER6',
                                                               'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E00754',  # has no FreeSurfer resource
    resource_name = 'FREESURFER7'

    axes = 'xz'
    figsize = {'x': (16, 14), 'z': (16, 10)}
    rowsize = {'x': 8, 'z': 8}
    n_slices = {'x': 40, 'z': 48}
    step = 3
    threshold = 75
    labels = aseg.cortical_labels


class AreCAVolumesConsistent(freesurfer.AreCAVolumesConsistent):
    __doc__ = freesurfer.AreCAVolumesConsistent.__doc__.replace('FREESURFER6',
                                                                'FREESURFER7')
    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E00754',
    resource_name = 'FREESURFER7'


#class HasAbnormalAsegFeatures(freesurfer.HasAbnormalAsegFeatures):
#    __doc__ = freesurfer.HasAbnormalAsegFeatures.__doc__.replace('FREESURFER6',
#                                                                 'FREESURFER7')
#    passing = 'BBRCDEV_E00270',
#    failing = 'BBRCDEV_E00754',
#    threshold = 7
#    resource_name = 'FREESURFER7'
