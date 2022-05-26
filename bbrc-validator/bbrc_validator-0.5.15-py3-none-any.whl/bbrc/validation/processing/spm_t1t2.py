from ..test import ExperimentTest, Results
from . import spm


class HasCorrectNumberOfItems(spm.HasCorrectNumberOfItems):
    __doc__ = spm.HasCorrectNumberOfItems.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')
    __doc__ = __doc__.replace('16', '25')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT_T1T2'
    correct_number = 25


class HasCorrectItems(spm.HasCorrectItems):
    __doc__ = spm.HasCorrectItems.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT_T1T2'
    expected_items = ['rc1*.nii.gz',
                      'rc2*.nii.gz',
                      'c1*.nii.gz',
                      'c2*.nii.gz',
                      'c3*.nii.gz',
                      'c4*.nii.gz',
                      'c5*.nii.gz',
                      'fixed_c1*.nii.gz',
                      'fixed_c2*.nii.gz',
                      'fixed_c3*.nii.gz',
                      'fixed_c5*.nii.gz',
                      'fixed_rc1*.nii.gz',
                      'fixed_rc2*.nii.gz',
                      'fixed_rc3*.nii.gz',
                      'y_*.nii.gz',
                      'iy_*.nii.gz',
                      '*_seg8.mat',
                      'pyscript_setorigin_t1.m',
                      'pyscript_setorigin_t2.m',
                      'pyscript_multichannelnewsegment.m']


class HasCorrectSPMVersion(spm.HasCorrectSPMVersion):
    __doc__ = spm.HasCorrectSPMVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')
    __doc__ = __doc__.replace('SPM12 Release 7219', 'SPM12 Release 7487')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT_T1T2'
    expected_version = 'SPM version: SPM12 Release: 7487'


class HasCorrectMatlabVersion(spm.HasCorrectMatlabVersion):
    __doc__ = spm.HasCorrectMatlabVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E00272',
    resource_name = 'SPM12_SEGMENT_T1T2'


class HasCorrectOSVersion(spm.HasCorrectOSVersion):
    __doc__ = spm.HasCorrectOSVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT_T1T2'


class SPM12SegmentSnapshot(spm.SPM12SegmentSnapshot):
    __doc__ = spm.SPM12SegmentSnapshot.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT_T1T2'


class HasNormalSPM12Volumes(spm.HasNormalSPM12Volumes):
    __doc__ = spm.HasNormalSPM12Volumes.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT_T1T2'
    file_prefixes = ['fixed_c1', 'fixed_c2', 'fixed_c3']


class SPM12SegmentExecutionTime(spm.SPM12SegmentExecutionTime):
    __doc__ = spm.SPM12SegmentExecutionTime.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2')

    passing = 'BBRCDEV_E02989',
    failing = 'BBRCDEV_E00272',
    resource_name = 'SPM12_SEGMENT_T1T2'


class SPM12SegmentMultichannelHoles(ExperimentTest):
    """SPM segmentation in multi-channel mode might misclassify as c5 tissue
    some c2 regions such as the `pallidum` and the `dentate nucleus` (known
    issue), appearing those as _holes_ in the c1+c2 maps. This test estimates
    the size of such _holes_ when present, failing if its size > 30000 and
    passing otherwise. In addition, test generates a modified version of the
    original c2 map with those misclassified c5 areas labeled as c2.
    A snapshot composition is included to inspect this modified map visually
    (original c2 segmentation in green and detected _holes_ in red)."""

    passing = 'BBRCDEV_E03055',
    failing = 'BBRCDEV_E03059',
    resource_name = 'SPM12_SEGMENT_T1T2'

    def run(self, experiment_id):
        import os
        import os.path as op
        import tempfile
        import nibabel as nib
        import numpy as np
        from nilearn import image

        e = self.xnat_instance.select.experiment(experiment_id)
        if not e.resource(self.resource_name).exists():
            msg = 'Resource {} not found.'.format(self.resource_name)
            return Results(False, data=[msg])
        r = e.resource(self.resource_name)

        filepaths = []
        for each in ['c2', 'fixed_c2']:
            f, fp = tempfile.mkstemp(suffix='.nii.gz')
            os.close(f)
            try:
                c = list(r.files('{}*.nii.gz'.format(each)))[0]
            except IndexError:
                return Results(False, data=['Some SPM maps are missing, check '
                                            '`HasCorrectItems` test results.'])

            c.get(fp)
            filepaths.append(fp)

        c2 = np.asarray(nib.load(filepaths[0]).dataobj)
        fixed = np.asarray(nib.load(filepaths[1]).dataobj)

        holes = fixed - c2
        holes[holes < 0.0] = 0
        size = len(holes[holes > 0.01])

        diff_img = op.join(op.dirname(filepaths[0]),
                           '{}_diff_c2.nii.gz'.format(experiment_id))
        image.new_img_like(filepaths[0], holes).to_filename(diff_img)

        from . import holes_snapshot
        snapshots = holes_snapshot(filepaths[1], diff_img)
        os.remove(diff_img)
        for fp in filepaths:
            os.remove(fp)

        res = size < 30000  # Fixme : with some threshold value
        return Results(res, data={'size': '{}'.format(size),
                                  'snapshots': snapshots})

    def report(self):
        report = []
        if isinstance(self.results.data, dict):
            report.append('Size: {}'.format(self.results.data['size']))
            for path in self.results.data['snapshots']:
                report.append('![snapshot]({})'.format(path))
        else:
            report = self.results.data
        return report


class SPM12SegmentMultichannelClusters(ExperimentTest):
    """SPM segmentation in multi-channel mode might misclassify as c1/c2/c3
    tissue clusters of voxels located outside the brain, i.e. the neck, nape or
    the brain stem areas (known issue). This test estimates the size of such
    missegmented _clusters_ in GM/WM classes when present, failing if its size
    > 20000 and passing otherwise. In addition, test generates a snapshot
    composition of the cleansed version of the original maps (where those
    misclassified regions were labeled as c5) to inspect visually the changes
    applied. Modified c1+c2 segmentations shown in green and cleansed voxel
    _clusters_ in red."""

    passing = 'BBRCDEV_E03055',
    failing = 'BBRCDEV_E03058',
    resource_name = 'SPM12_SEGMENT_T1T2'

    def run(self, experiment_id):
        import os
        import os.path as op
        import tempfile
        import nibabel as nib
        import numpy as np
        from nilearn import image

        e = self.xnat_instance.select.experiment(experiment_id)
        if not e.resource(self.resource_name).exists():
            msg = 'Resource {} not found.'.format(self.resource_name)
            return Results(False, data=[msg])
        r = e.resource(self.resource_name)

        filepaths = []
        for each in ['c1', 'c2', 'fixed_c1', 'fixed_c2']:
            f, fp = tempfile.mkstemp(suffix='.nii.gz')
            os.close(f)
            try:
                c = list(r.files('{}*.nii.gz'.format(each)))[0]
            except IndexError:
                return Results(False, data=['Some SPM maps are missing, check '
                                            '`HasCorrectItems` test results.'])

            c.get(fp)
            filepaths.append(fp)

        c1 = np.asarray(nib.load(filepaths[0]).dataobj)
        c2 = np.asarray(nib.load(filepaths[1]).dataobj)
        c = c1 + c2
        fixed_c1 = np.asarray(nib.load(filepaths[2]).dataobj)
        fixed_c2 = np.asarray(nib.load(filepaths[3]).dataobj)
        fixed = fixed_c1 + fixed_c2

        misseg = c - fixed
        misseg[misseg < 0.0] = 0
        size = len(misseg[misseg > 0.01])

        diff_fp = op.join(op.dirname(filepaths[0]),
                          '{}_diff.nii.gz'.format(experiment_id))
        image.new_img_like(filepaths[0], misseg).to_filename(diff_fp)
        c1c2_fp = op.join(op.dirname(filepaths[0]),
                          '{}_c1c2.nii.gz'.format(experiment_id))
        image.new_img_like(filepaths[0], c).to_filename(c1c2_fp)

        from . import holes_snapshot
        snapshots = holes_snapshot(c1c2_fp, diff_fp)
        for fp in filepaths + [c1c2_fp, diff_fp]:
            os.remove(fp)

        res = size < 20000  # Fixme : with some threshold value
        return Results(res, data={'size': '{}'.format(size),
                                  'snapshots': snapshots})

    def report(self):
        report = []
        if isinstance(self.results.data, dict):
            report.append('Size: {}'.format(self.results.data['size']))
            for path in self.results.data['snapshots']:
                report.append('![snapshot]({})'.format(path))
        else:
            report = self.results.data
        return report