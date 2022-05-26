from ..test import ExperimentTest, Results


class HasCorrectNumberOfItems(ExperimentTest):
    """Passes if a `BASIL` resource is found and this resource has the expected
    total number of items (i.e. 217 files)."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00381',
    CORRECT_NUMBER = 217

    def run(self, experiment_id):
        resource_name = 'BASIL'
        data = []

        e = self.xnat_instance.select.experiment(experiment_id)
        files = list(e.resource(resource_name).files())

        res = len(files) == self.CORRECT_NUMBER

        if not res:
            data.append('{} has {} items (different from {})'
                        .format(experiment_id, len(files), self.CORRECT_NUMBER))

        return Results(res, data)


class HasCorrectItems(ExperimentTest):
    """Passes if a `BASIL` resource is found and this resource
    has the expected items according to the pipeline
    [specifications](https://gitlab.com/bbrc/xnat/xnat-pipelines/-/tree/master/basil#outputs)."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00381',

    def run(self, experiment_id):
        resource_name = 'BASIL'
        unique_items = ['calib/M0.nii.gz',
                        'logfile',
                        'native_space/asl2struct.mat',
                        'native_space/asl2struct_init.mat',
                        'native_space/arrival_gm_mean.txt',
                        'native_space/arrival_wm_mean.txt',
                        'native_space/perfusion_gm_mean.txt',
                        'native_space/perfusion_wm_mean.txt',
                        'native_space/perfusion_calib_gm_mean.txt',
                        'native_space/perfusion_calib_wm_mean.txt',
                        'native_space/pvcorr/arrival_gm_mean.txt',
                        'native_space/pvcorr/arrival_wm_wm_mean.txt',
                        'native_space/pvcorr/perfusion_gm_mean.txt',
                        'native_space/pvcorr/perfusion_wm_wm_mean.txt',
                        'native_space/pvcorr/perfusion_calib_gm_mean.txt',
                        'native_space/pvcorr/perfusion_wm_calib_wm_mean.txt',
                        'native_space/mask.nii.gz',
                        'native_space/mask_pvcorr.nii.gz',
                        'native_space/gm_mask.nii.gz',
                        'native_space/gm_roi.nii.gz',
                        'native_space/wm_mask.nii.gz',
                        'native_space/wm_roi.nii.gz',
                        'native_space/pvcorr/arrival_masked.nii.gz',
                        'native_space/pvcorr/arrival_wm_masked.nii.gz',
                        'native_space/pvcorr/perfusion_masked.nii.gz',
                        'native_space/pvcorr/perfusion_wm_masked.nii.gz',
                        'native_space/pvcorr/perfusion_calib_masked.nii.gz',
                        'native_space/pvcorr/perfusion_wm_calib_masked.nii.gz',
                        'native_space/pvgm_inasl.nii.gz',
                        'native_space/pvwm_inasl.nii.gz',
                        'native_space/region_analysis/region_analysis.csv',
                        'native_space/region_analysis/region_analysis_gm.csv',
                        'native_space/region_analysis/region_analysis_wm.csv']
        common_items = ['{space}/arrival.nii.gz',
                        '{space}/arrival_var.nii.gz',
                        '{space}/perfusion.nii.gz',
                        '{space}/perfusion_calib.nii.gz',
                        '{space}/perfusion_norm.nii.gz',
                        '{space}/perfusion_var.nii.gz',
                        '{space}/perfusion_var_calib.nii.gz',
                        '{space}/perfusion_var_norm.nii.gz',
                        '{space}/pvcorr/arrival.nii.gz',
                        '{space}/pvcorr/arrival_var.nii.gz',
                        '{space}/pvcorr/arrival_wm.nii.gz',
                        '{space}/pvcorr/arrival_wm_var.nii.gz',
                        '{space}/pvcorr/perfusion.nii.gz',
                        '{space}/pvcorr/perfusion_calib.nii.gz',
                        '{space}/pvcorr/perfusion_norm.nii.gz',
                        '{space}/pvcorr/perfusion_var.nii.gz',
                        '{space}/pvcorr/perfusion_var_calib.nii.gz',
                        '{space}/pvcorr/perfusion_var_norm.nii.gz',
                        '{space}/pvcorr/perfusion_wm.nii.gz',
                        '{space}/pvcorr/perfusion_wm_calib.nii.gz',
                        '{space}/pvcorr/perfusion_wm_norm.nii.gz',
                        '{space}/pvcorr/perfusion_wm_var.nii.gz',
                        '{space}/pvcorr/perfusion_wm_var_calib.nii.gz',
                        '{space}/pvcorr/perfusion_wm_var_norm.nii.gz']

        result = True

        e = self.xnat_instance.select.experiment(experiment_id)
        res = e.resource(resource_name)

        missing = []
        for item in unique_items:
            files = res.files(item).get()
            if not files:
                missing.append(item)
        for space in ['native_space', 'std_space', 'struct_space']:
            items = [i.format(space=space) for i in common_items]
            for item in items:
                files = res.files(item).get()
                if not files:
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


class HasCorrectFSLVersion(ExperimentTest):
    """Checks the version of FSL used. Passes if BASIL outputs
    were created using the expected version (`6.0.4:ddd0a010`)."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00381',

    def run(self, experiment_id):
        resource_name = 'BASIL'
        expected_version = 'FSL 6.0.4:ddd0a010'

        e = self.xnat_instance.select.experiment(experiment_id)
        log_filename = 'LOGS/{}.log'.format(e.label())
        log_file = e.resource(resource_name).file(log_filename)

        if not log_file.exists():
            msg = '{} log file not found.'.format(resource_name)
            return Results(False, data=[msg])

        log_data = self.xnat_instance.get(log_file.attributes()['URI']).text
        version_line = [line for line in log_data.splitlines()
                        if line.strip().startswith('fsl_anat')]
        if not version_line:
            msg = 'No FSL version registered in the logs.'
            return Results(False, data=[msg])

        version = version_line[0].split('(')[-1].split(')')[0]
        if not version == expected_version:
            return Results(False, data=[version])

        return Results(True, data=[])


class HasCorrectOxfordASLVersion(ExperimentTest):
    """Checks the version of oxford_asl used. Passes if `BASIL`
    outputs were created using the expected version (`4.0.15`)."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00381',

    def run(self, experiment_id):
        resource_name = 'BASIL'
        expected_version = 'v4.0.15-dirty Fri Jul 17 12:23:03 2020'

        e = self.xnat_instance.select.experiment(experiment_id)
        log_filename = 'LOGS/{}.log'.format(e.label())
        log_file = e.resource(resource_name).file(log_filename)

        if not log_file.exists():
            msg = '{} log file not found.'.format(resource_name)
            return Results(False, data=[msg])

        log_data = self.xnat_instance.get(log_file.attributes()['URI']).text
        version_line = [line for line in log_data.splitlines()
                        if line.strip().startswith('oxford_asl')]
        if not version_line:
            msg = 'No oxford_asl version registered in the logs.'
            return Results(False, data=[msg])

        version = version_line[0].split('oxford_asl ')[-1]
        if not version.startswith(expected_version):
            return Results(False, data=[version])

        return Results(True, data=[])


class IsT1Session1(ExperimentTest):
    """Checks the type of T1w image used by the pipeline. Passes if `BASIL`
    outputs were created using a T1w scan image from the ALFA+ Session1
    scanning protocol (`T1_ALFA1`)."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E03053',
    resource_name = 'BASIL'
    expected_type = 'T1_ALFA1'

    def run(self, experiment_id):
        from ..sanity.data import HasUsableT1

        res = HasUsableT1(self.lut, self.xnat_instance).run(experiment_id)
        if not res.has_passed:
            return res
        sid = res.data[0]
        s = self.xnat_instance.select.experiment(experiment_id).scan(sid)
        scan_type = s.attrs.get('type').strip()

        result = (scan_type == self.expected_type)
        data = []
        if not result:
            data = [scan_type]
        return Results(result, data=data)


class IsT1Session3(IsT1Session1):
    __doc__ = IsT1Session1.__doc__.replace('Session1', 'Session3')
    __doc__ = __doc__.replace('T1_ALFA1', 'sT1W_3D_TFE_HR_32 iso1.2 long AT')

    passing = 'BBRCDEV_E03053',
    failing = 'BBRCDEV_E00381',
    resource_name = 'BASIL'
    expected_type = 'sT1W_3D_TFE_HR_32 iso1.2 long AT'


class IsGMPerfusionMeanConsistent(ExperimentTest):
    """Checks the calibrated perfusion mean value (with partial volume
    correction) for GM. Test passes if average cerebral blood flow is within the
    expected range, i.e. between 30-100 ml/(100g min). Test fails otherwise."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E03053',
    resource_name = 'BASIL'
    file_name = 'native_space/pvcorr/perfusion_calib_gm_mean.txt'
    range = (30, 100)

    def run(self, experiment_id):

        e = self.xnat_instance.select.experiment(experiment_id)
        f = e.resource(self.resource_name).file(self.file_name)
        try:
            value = float(self.xnat_instance.get(f._uri).text.strip())
        except ValueError:
            msg = '`{}` file not found.'.format(f._urn)
            return Results(False, data=[msg])

        result = bool(self.range[0] <= value <= self.range[1])

        return Results(result, data=[value])

    def report(self):
        report = []
        if not self.results.has_passed:
            if isinstance(self.results.data[0], str):
                report = self.results.data
            elif isinstance(self.results.data[0], float):
                report.append('Mean perfusion value ({}) is out of the '
                              'expected range.'.format(self.results.data[0]))
        return report


class IsWMPerfusionMeanConsistent(IsGMPerfusionMeanConsistent):
    __doc__ = IsGMPerfusionMeanConsistent.__doc__.replace('GM', 'WM')
    __doc__ = __doc__.replace('between 30-100', 'between 10-60')

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E03053',
    resource_name = 'BASIL'
    file_name = 'native_space/pvcorr/perfusion_wm_calib_wm_mean.txt'
    range = (10, 60)


class PerfusionSnapshot(ExperimentTest):
    """This test creates a snapshot of the calibrated brain perfusion generated
    by BASIL. Passes if the snapshot is created successfully. Fails otherwise."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00381',
    resource_name = 'BASIL'

    def run(self, experiment_id):
        import os
        import tempfile
        from nilearn import plotting

        slices = {'x': [-46, -30, -16, -4, 12, 26, 38],
                  'y': [-80, -60, -40, -20, 10, 20, 40],
                  'z': [-20, -10, 0, 10, 20, 30, 45]}

        if os.getenv('SKIP_SNAPSHOTS_TESTS') == 'True':
            return Results(experiment_id == self.passing[0],
                           data=['Skipping it. (SKIP_SNAPSHOTS_TESTS)'])
        paths = []
        try:
            bg, filepaths = self.__download_perf__(experiment_id,
                                                   tempfile.gettempdir(),
                                                   self.resource_name)
            for each in 'xyz':
                fd, path = tempfile.mkstemp(suffix='.jpg')
                os.close(fd)
                paths.append(path)
                im = plotting.plot_anat(bg,
                                        black_bg=True,
                                        display_mode=each,
                                        cut_coords=slices[each])
                im.add_overlay(filepaths[0],
                               threshold=10,
                               colorbar=True,
                               cmap='hsv',
                               vmin=20,
                               vmax=150)
                im.savefig(path)

            for item in [bg] + filepaths:
                os.remove(item)

        except Exception:
            return Results(False, data=['Snapshot creation failed.'])

        return Results(True, paths)

    def report(self):
        report = []
        if self.results.has_passed:
            for path in self.results.data:
                report.append('![snapshot]({})'.format(path))
        else:
            report = self.results.data

        return report

    def __download_perf__(self, experiment_id, destination, resource='BASIL'):
        import os.path as op

        files = ['fsl.anat/T1_to_MNI_lin.nii.gz',
                 'std_space/pvcorr/perfusion_calib.nii.gz']

        filepaths = []

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(resource)
        for each in files:
            f = r.file(each)
            fp = op.join(destination, f.attributes()['Name'])
            f.get(fp)
            filepaths.append(fp)

        bg = filepaths.pop(0)
        return bg, filepaths


class FSLANATSegmentationSnapshot(ExperimentTest):
    """This test creates a snapshot of the tissue segmentation results generated
    by BASIL (`fsl_anat`). Passes if the snapshot is created successfully.
    Fails otherwise. Does not tell anything on the segmentation quality."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00381',
    resource_name = 'BASIL'

    def run(self, experiment_id):
        import os
        import tempfile
        from nisnap import snap

        axes = 'xyz'
        rowsize = {'x': 10, 'y': 10, 'z': 6}
        opacity = 75
        slices = {'x': list(range(50, 200, 5)),
                  'y': list(range(50, 250, 5)),
                  'z': list(range(25, 125, 6))}
        # hack: adjust slice-picking settings based on type of T1 scan protocol
        res = IsT1Session1(self.lut, self.xnat_instance).run(experiment_id)
        if res.has_passed:
            slices['z'] = list(range(50, 190, 6))

        if os.getenv('SKIP_SNAPSHOTS_TESTS') == 'True':
            return Results(experiment_id == self.passing[0],
                           data=['Skipping it. (SKIP_SNAPSHOTS_TESTS)'])
        try:
            bg, filepaths = self.__download_fslanat__(experiment_id,
                                                      tempfile.gettempdir(),
                                                      self.resource_name)
            # Create snapshot with proper options
            fd, snap_fp = tempfile.mkstemp(suffix=snap.__format__)
            os.close(fd)
            snap.plot_segment(filepaths, bg=bg, opacity=opacity,
                              axes=axes, slices=slices, rowsize=rowsize,
                              savefig=snap_fp, samebox=True)
        except Exception:
            return Results(False, data=['Snapshot creation failed.'])

        return Results(True, data=[snap_fp])

    def report(self):
        report = []
        if self.results.has_passed:
            path = self.results.data[0]
            report.append('![snapshot]({})'.format(path))
        else:
            report = self.results.data

        return report

    def __download_fslanat__(self, experiment_id, destination, resource_name='BASIL'):
        import os.path as op

        files = {'fsl.anat/T1.nii.gz': 'T1.nii.gz',
                 'fsl.anat/T1_fast_pve_1.nii.gz': 'GM.nii.gz',
                 'fsl.anat/T1_fast_pve_2.nii.gz': 'WM.nii.gz',
                 'fsl.anat/T1_fast_pve_0.nii.gz': 'CSF.nii.gz'}

        filepaths = []

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(resource_name)
        for each, label in files.items():
            f = r.file(each)
            fp = op.join(destination, label)
            f.get(fp)
            filepaths.append(fp)

        bg = filepaths.pop(0)
        return bg, filepaths


class HasNormalFSLANATVolumes(ExperimentTest):
    """This test runs the quality-predicting procedure on the BASIL
    resource based on its estimated GM and WM volumes estimated by fsl_anat.
    Test passes if volumes are within boundaries, i.e. `GM` volume ranges
    between 450000 and 800000; `WM` volume ranges between 330000 and 630000).
    Test fails otherwise."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E03054',
    resource_name = 'BASIL'

    def _check(self, vols):
        boundaries = [('T1_fast_pve_1', [450000, 800000]),
                      ('T1_fast_pve_2', [330000, 630000])]
        has_passed = True

        for (col, (bmin, bmax)), subject_val in zip(boundaries, vols[1:]):
            sv = float(subject_val)
            if sv > float(bmax) or sv < float(bmin):
                has_passed = False
        return has_passed

    def run(self, experiment_id):
        import os
        import tempfile
        import nibabel as nib
        import numpy as np

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        if not r.exists():
            return Results(False, data=['Missing {} resource'
                           .format(self.resource_name)])
        vols = []
        fd, fp = tempfile.mkstemp(suffix='.nii.gz')
        os.close(fd)

        for kls in ['T1_fast_pve_0', 'T1_fast_pve_1', 'T1_fast_pve_2']:
            try:
                f = list(r.files('*{}*'.format(kls)))[0]
            except IndexError:
                return Results(False, data=['Some SPM maps are missing, check '
                                            '`HasCorrectItems` test results.'])
            f.get(fp)
            d = nib.load(fp)
            size = np.prod(d.header['pixdim'].tolist()[:4])
            v = np.sum(d.dataobj) * size
            vols.append(v)

        res = self._check(vols)
        return Results(res, data=['Volumes: {} {}'.format(vols[1], vols[2])])
