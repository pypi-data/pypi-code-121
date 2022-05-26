from ..test import ExperimentTest, Results
from . import Snapshot


class HasCorrectItems(ExperimentTest):
    """Passes if a `FREESURFER7_EXTRAS` resource is found and this resource
    has the expected items according to the pipeline
    [specifications](https://gitlab.com/bbrc/xnat/xnat-pipelines/-/tree/master/freesurfer_extras#outputs)."""

    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02920',
    resource_name = 'FREESURFER7_EXTRAS'
    expected_items = ['*/mri/hypothalamic_subunits_volumes.v1.csv',
                      '*/mri/hypothalamic_subunits_seg.v1.mgz',
                      '*/mri/ThalamicNuclei.v12.T1.volumes.txt',
                      '*/mri/ThalamicNuclei.v12.T1.mgz',
                      '*/mri/ThalamicNuclei.v12.T1.FSvoxelSpace.mgz',
                      '*/mri/brainstemSsVolumes.v12.txt',
                      '*/mri/brainstemSsLabels.v12.mgz',
                      '*/mri/brainstemSsLabels.v12.FSvoxelSpace.mgz',
                      '*/stats/hypothalamic_subunits_volumes.v1.stats',
                      '*/stats/thalamic-nuclei.lh.v12.T1.stats',
                      '*/stats/thalamic-nuclei.rh.v12.T1.stats',
                      '*/stats/brainstem.v12.stats',
                      '*/scripts/thalamic-nuclei-mainFreeSurferT1.log',
                      '*/scripts/brainstem-substructures-T1.log']

    def run(self, experiment_id):
        result = True

        e = self.xnat_instance.select.experiment(experiment_id)
        res = e.resource(self.resource_name)

        missing = []
        for item in self.expected_items:
            f = res.files(item).get()
            if not f:
                missing.append(item)

        if missing:
            result = False

        return Results(result, data=missing)

    def report(self):
        report = []
        if not self.results.has_passed:
            report.append('Missing items: {}.'
                          .format(self.results.data).replace('\'', '`'))
        return report


class HasCorrectFreeSurferVersion(ExperimentTest):
    """This test checks the version of FreeSurfer used. Passes if `FREESURFER7_EXTRAS`
    outputs were created using the expected version (`{version}`)."""

    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02920',
    resource_name = 'FREESURFER7_EXTRAS'
    expected_version = 'freesurfer-linux-centos7_x86_64-7.2.0-20210720-aa8f76b'
    __doc__ = __doc__.format(version=expected_version)

    def run(self, experiment_id):
        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        log = r.file('LOGS/{}.log'.format(e.label()))
        if not log.exists():
            msg = '{} log file not found.'.format(self.resource_name)
            return Results(False, data=[msg])

        log_data = self.xnat_instance.get(log._uri).text
        version = [line for line in log_data.splitlines()
                   if line.strip().startswith('freesurfer-')]

        if not version or version[0] != self.expected_version:
            return Results(False, data=['Incorrect FreeSurfer version: '
                                        '{}'.format(version[0])])

        return Results(True, data=[])


class HasCorrectOSVersion(ExperimentTest):
    """This test checks the OS kernel version on which FreeSurfer was executed.
    Passes if OS kernel version matches the expected version (`{version}`)."""

    passing = 'BBRCDEV_E00270',
    failing = 'BBRCDEV_E02920',
    resource_name = 'FREESURFER7_EXTRAS'
    kernel_version = '4.4.120-92.70-default'
    __doc__ = __doc__.format(version=kernel_version)

    def run(self, experiment_id):
        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)

        log_files = r.files('*/scripts/*.log')
        for f in log_files:
            uri = f.attributes()['URI']
            kernel_version_line = self.xnat_instance.get(uri).text.splitlines()[7]

            if self.kernel_version not in kernel_version_line:
                msg = 'Incorrect OS version: %s' % kernel_version_line.strip()
                return Results(False, data=[msg])

        return Results(True, data=[])


class HasExpectedHypothalamicSegmentationResolution(ExperimentTest):
    """The CNN network used for the segmentation of the hypothalamic subunits
    has been trained on images at ~1mm isotropic resolution. Thus, segmentation
    model underperforms when presented with images of higher/lower resolutions.
    To address that, target input images should be resampled to 1mm isotropic
    resolution to run the hypothalamic segmentation module correctly.
    This test checks the pixel resolution of the segmentation results image.
    Passes if resolution is 1x1x1mm (isotropic), fails otherwise."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E00270',

    def run(self, experiment_id):
        import os
        import os.path as op
        import tempfile
        import nibabel as nib

        resource_name = 'FREESURFER7_EXTRAS'
        expected_res = [1.0, 1.0, 1.0]

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(resource_name)

        if not r.exists():
            msg = 'Resource {} not found.'.format(resource_name)
            return Results(False, data=[msg])
        try:
            seg_file = list(r.files('*hypothalamic*.mgz'))[0]
        except IndexError:
            msg = 'Hypothalamic segmentation results file not found.'
            return Results(False, data=[msg])

        fd, fp = tempfile.mkstemp(suffix='.mgz')
        os.close(fd)
        seg_file.get(fp)

        img = nib.load(fp)
        pixel_dims = img.header['delta']
        img_res = [round(item, 2) for item in pixel_dims]

        os.remove(fp)
        if not img_res == expected_res:
            msg = 'Segmentation results (`{}`) do not match expected image ' \
                  'resolution: {}mm.'.format(op.basename(seg_file.label()),
                                             'x'.join([str(i) for i in img_res]))
            return Results(False, data=[msg])

        return Results(True, data=[])


class HasAllBrainstemRegions(ExperimentTest):
    """This test checks if brainstem segmentation has any regions missing (as
    defined in file `brainstemSsVolumes.v12.txt`). Passes if all regions are
    segmented. Fails otherwise."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    expected_regions = ['Medulla', 'Pons', 'SCP', 'Whole_brainstem', 'Midbrain']
    filename = 'brainstemSsVolumes.v12.txt'

    def _parse_volumes_file(self, file_content):
        """Helper for parsing volume files, returns a DataFrame object."""
        import pandas as pd

        vols = [line.split(" ") for line in file_content]
        df = pd.DataFrame(vols, columns=['region', 'volume'])
        df['volume'] = pd.to_numeric(df['volume'])
        return df

    def run(self, experiment_id):

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        if not r.exists():
            msg = 'Resource {} not found.'.format(self.resource_name)
            return Results(False, data=[msg])

        try:
            f = list(r.files('*/mri/{}'.format(self.filename)))[0]
        except IndexError:
            return Results(False, data=['Volumes file missing.'])

        content = self.xnat_instance.get(f.attributes()['URI']).text.splitlines()
        df = self._parse_volumes_file(content)
        missing = list(set(self.expected_regions).difference(set(df.region)))
        if missing:
            msg = 'Missing segmented regions: {}'.format(missing)
            return Results(False, data=[msg])

        missing = list(df[df.volume == 0].region)
        if missing:
            msg = 'Missing segmented regions: {}'.format(missing)
            return Results(False, data=[msg])

        return Results(True, data=[])


class HasNormalBrainstemVolumes(ExperimentTest):
    """This test compares brainstem volumes with predefined boundaries.
    Passes if the number of outliers is less than 2. Fails otherwise."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    filename = 'brainstemSsVolumes.v12.txt'
    boundaries = {'Medulla': [3599.840867, 6446.140152],
                  'Pons': [10871.673402, 20476.806056],
                  'SCP': [180.956601, 522.486944],
                  'Midbrain': [4464.018196, 8095.534689],
                  'Whole_brainstem': [19140.270407, 34292.653656]}
    threshold = 2

    def _parse_volumes_file(self, file_content):
        """Helper for parsing volume files, returns a DataFrame object."""
        import pandas as pd

        vols = [line.split(" ") for line in file_content]
        df = pd.DataFrame(vols, columns=['region', 'volume'])
        df['volume'] = pd.to_numeric(df['volume'])
        return df

    def run(self, experiment_id):

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        if not r.exists():
            msg = 'Resource {} not found.'.format(self.resource_name)
            return Results(False, data=[msg])

        try:
            f = list(r.files('*/mri/{}'.format(self.filename)))[0]
        except IndexError:
            return Results(False, data=['Volumes file missing.'])

        content = self.xnat_instance.get(f.attributes()['URI']).text.splitlines()
        df = self._parse_volumes_file(content)

        outliers = []
        for r, vol_range in self.boundaries.items():
            value = df[df.region == r].volume.item()
            if not vol_range[0] < value < vol_range[1]:
                res = '`%s`: %s (%s - %s)' % (r, value, vol_range[0], vol_range[1])
                outliers.append(res)

        result = len(outliers) < self.threshold

        return Results(result, data=outliers)


class AreBrainstemVolumesConsistent(HasAllBrainstemRegions):
    """This test checks the consistency of brainstem regional volumes. Passes if
    SCP < Medulla < Midbrain < Pons. Fails otherwise."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    expected_order = ['SCP', 'Medulla', 'Midbrain', 'Pons', 'Whole_brainstem']
    filename = 'brainstemSsVolumes.v12.txt'

    def run(self, experiment_id):

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        if not r.exists():
            msg = 'Resource {} not found.'.format(self.resource_name)
            return Results(False, data=[msg])

        try:
            f = list(r.files('*/mri/{}'.format(self.filename)))[0]
        except IndexError:
            return Results(False, data=['Volumes file missing.'])

        content = self.xnat_instance.get(f.attributes()['URI']).text.splitlines()
        df = self._parse_volumes_file(content)

        sorted_regions = list(df.sort_values(by='volume').region)
        result = self.expected_order == sorted_regions
        data = []
        if not result:
            data = ['Brainstem volumes are not consistent.']

        return Results(result, data)


class HasAllHypothalamicRegions(HasAllBrainstemRegions):
    __doc__ = HasAllBrainstemRegions.__doc__
    __doc__ = __doc__.replace('brainstemSsVolumes.v12.txt',
                              'hypothalamic_subunits_volumes.v1.csv')
    __doc__ = __doc__.replace('brainstem',
                              'hypothalamic')

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E03052',
    resource_name = 'FREESURFER7_EXTRAS'
    expected_regions = ['left anterior-inferior', 'left anterior-superior',
                        'left posterior', 'left tubular inferior',
                        'left tubular superior', 'right anterior-inferior',
                        'right anterior-superior', 'right posterior',
                        'right tubular inferior', 'right tubular superior',
                        'whole left', 'whole right']
    filename = 'hypothalamic_subunits_volumes.v1.csv'

    def _parse_volumes_file(self, file_content):
        """Helper for parsing volume files, returns a DataFrame object."""
        import pandas as pd

        vols = [line.split(",") for line in file_content]
        df = pd.DataFrame(vols).T
        df.columns = ['region', 'volume']
        df = df.drop([0])  # exclude row with Subject label
        df['volume'] = pd.to_numeric(df['volume'])
        return df


class HasNormalHypothalamicVolumes(HasNormalBrainstemVolumes):
    __doc__ = HasNormalBrainstemVolumes.__doc__
    __doc__ = __doc__.replace('brainstem volumes', 'hypothalamic subunits volumes')
    __doc__ = __doc__.replace('less than 2', 'less than 3')

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E00270',
    resource_name = 'FREESURFER7_EXTRAS'
    filename = 'hypothalamic_subunits_volumes.v1.csv'
    boundaries = {'left anterior-inferior': [3.560, 28.696],
                  'left anterior-superior': [12.456, 30.431],
                  'left posterior': [74.704, 151.516],
                  'left tubular inferior': [95.722, 182.157],
                  'left tubular superior': [64.839, 140.903],
                  'right anterior-inferior': [2.393, 27.138],
                  'right anterior-superior': [9.454, 32.590],
                  'right posterior': [67.427, 159.386],
                  'right tubular inferior': [70.659, 170.866],
                  'right tubular superior': [66.464, 140.865]}
    threshold = 3

    def _parse_volumes_file(self, file_content):
        """Helper for parsing volume files, returns a DataFrame object."""
        import pandas as pd

        vols = [line.split(",") for line in file_content]
        df = pd.DataFrame(vols).T
        df.columns = ['region', 'volume']
        df = df.drop([0])  # exclude row with Subject label
        df['volume'] = pd.to_numeric(df['volume'])
        return df


class HasAllThalamicNucleiRegions(HasAllBrainstemRegions):
    __doc__ = HasAllBrainstemRegions.__doc__
    __doc__ = __doc__.replace('brainstemSsVolumes.v12.txt',
                              'ThalamicNuclei.v12.T1.volumes.txt')
    __doc__ = __doc__.replace('brainstem',
                              'thalamic nuclei')

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    expected_regions = ['Left-AV', 'Left-CL', 'Left-CM', 'Left-CeM', 'Left-L-Sg',
                        'Left-LD', 'Left-LGN', 'Left-LP', 'Left-MDl', 'Left-MDm',
                        'Left-MGN', 'Left-MV(Re)', 'Left-Pc', 'Left-Pf', 'Left-Pt',
                        'Left-PuA', 'Left-PuI', 'Left-PuL', 'Left-PuM', 'Left-VA',
                        'Left-VAmc', 'Left-VLa', 'Left-VLp', 'Left-VM', 'Left-VPL',
                        'Left-Whole_thalamus', 'Right-AV', 'Right-CL', 'Right-CM',
                        'Right-CeM', 'Right-L-Sg', 'Right-LD', 'Right-LGN',
                        'Right-LP', 'Right-MDl', 'Right-MDm', 'Right-MGN',
                        'Right-MV(Re)', 'Right-Pc', 'Right-Pf', 'Right-Pt',
                        'Right-PuA', 'Right-PuI', 'Right-PuL', 'Right-PuM',
                        'Right-VA', 'Right-VAmc', 'Right-VLa', 'Right-VLp',
                        'Right-VM', 'Right-VPL', 'Right-Whole_thalamus']
    filename = 'ThalamicNuclei.v12.T1.volumes.txt'


class HasNormalThalamicNucleiVolumes(HasNormalBrainstemVolumes):
    __doc__ = HasNormalBrainstemVolumes.__doc__
    __doc__ = __doc__.replace('brainstem volumes', 'thalamic nuclei volumes')
    __doc__ = __doc__.replace('less than 2', 'less than 5')

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    filename = 'ThalamicNuclei.v12.T1.volumes.txt'
    boundaries = {'Left-LGN': [173.130543, 366.658623],
                  'Right-LGN': [173.130543, 331.58192],
                  'Right-MGN': [77.409379, 184.176349],
                  'Left-MGN': [58.749783, 175.182628],
                  'Left-PuI': [151.806203, 356.172965],
                  'Left-PuM': [737.072818, 1539.530467],
                  'Left-L-Sg': [13.05317, 47.756291],
                  'Left-VPL': [587.51957, 1258.233896],
                  'Left-CM': [155.711727, 333.400143],
                  'Left-VLa': [421.980474, 816.043557],
                  'Left-PuA': [144.588392, 339.102258],
                  'Left-MDm': [514.150553, 1066.650843],
                  'Left-Pf': [31.313712, 77.060956],
                  'Left-VAmc': [19.788624, 44.228645],
                  'Left-MDl': [188.718257, 386.696317],
                  'Left-CeM': [40.618456, 108.829826],
                  'Left-VA': [265.265801, 574.027071],
                  'Left-MV(Re)': [5.058248, 20.458005],
                  'Left-VM': [13.72443, 36.988289],
                  'Left-CL': [18.687398, 66.096544],
                  'Left-PuL': [102.474971, 371.868637],
                  'Left-Pt': [4.919226, 10.229313],
                  'Left-AV': [93.793032, 212.427117],
                  'Left-Pc': [2.486212, 5.295686],
                  'Left-VLp': [551.696839, 1063.654944],
                  'Left-LP': [74.251034, 179.0692],
                  'Right-PuI': [140.587749, 336.878935],
                  'Right-PuM': [711.638415, 1461.932904],
                  'Right-L-Sg': [13.594135, 41.920573],
                  'Right-VPL': [540.326047, 1103.601881],
                  'Right-CM': [169.281044, 313.071519],
                  'Right-VLa': [430.791779, 834.400483],
                  'Right-PuA': [127.200097, 274.82332],
                  'Right-MDm': [476.017956, 992.92537],
                  'Right-Pf': [37.298789, 75.823301],
                  'Right-VAmc': [21.668694, 42.11388],
                  'Right-MDl': [168.377174, 355.003853],
                  'Right-VA': [291.918542, 568.319953],
                  'Right-MV(Re)': [5.827165, 24.405568],
                  'Right-CeM': [37.684426, 100.406222],
                  'Right-VM': [13.613521, 31.352598],
                  'Right-PuL': [106.806302, 290.273997],
                  'Right-CL': [16.969291, 63.808497],
                  'Right-VLp': [549.148934, 1083.779433],
                  'Right-Pc': [2.73451, 5.523886],
                  'Right-Pt': [5.338657, 9.701907],
                  'Right-AV': [87.910334, 210.418975],
                  'Right-LP': [79.374844, 184.276394],
                  'Left-LD': [7.513359, 55.512799],
                  'Right-LD': [12.788354, 54.137129]}
    threshold = 5


class BrainstemSnapshot(ExperimentTest, Snapshot):
    """This test creates a snapshot of the brainstem segmented by
    FREESURFER7_EXTRAS. Passes if the snapshot is created successfully.
    Fails otherwise. Does not tell anything on the segmentation quality."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    fn = 'brainstemSsLabels.v12.FSvoxelSpace.mgz'
    axes = 'y'
    rowsize = 4
    figsize = (19, 10)
    step = 1
    threshold = 0
    n_slices = {'x': 20, 'y': 12, 'z': 20}
    contours = False
    margin = 30

    def run(self, experiment_id):
        return Snapshot.run(self, experiment_id)

    def report(self):
        return Snapshot.report(self)


class HypothalamusSnapshot(ExperimentTest, Snapshot):
    """This test creates a snapshot of the hypothalamus segmented by
     FREESURFER7_EXTRAS. Passes if the snapshot is created successfully.
     Fails otherwise. Does not tell anything on the segmentation quality."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    fn = 'hypothalamic_subunits_seg.v1.mgz'
    axes = 'y'
    rowsize = 4
    figsize = (19, 10)
    step = 1
    threshold = 0
    n_slices = {'x': 20, 'y': 12, 'z': 20}
    contours = False
    margin = 30

    def run(self, experiment_id):
        return Snapshot.run(self, experiment_id)

    def report(self):
        return Snapshot.report(self)


class ThalamusNucleiSnapshot(ExperimentTest, Snapshot):
    """This test creates a snapshot of the thalamus nuclei segmented
    by FREESURFER7_EXTRAS. Passes if the snapshot is created successfully.
    Fails otherwise. Does not tell anything on the segmentation quality."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E01613',
    resource_name = 'FREESURFER7_EXTRAS'
    fn = 'ThalamicNuclei.v12.T1.FSvoxelSpace.mgz'
    axes = 'y'
    rowsize = 4
    figsize = (19, 10)
    step = 1
    threshold = 0
    n_slices = {'x': 20, 'y': 12, 'z': 20}
    contours = False
    margin = 30

    def run(self, experiment_id):
        return Snapshot.run(self, experiment_id)

    def report(self):
        return Snapshot.report(self)
