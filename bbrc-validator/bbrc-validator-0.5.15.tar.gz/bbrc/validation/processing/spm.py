from ..test import ExperimentTest, Results
import os


class HasCorrectNumberOfItems(ExperimentTest):
    """Passes if a SPM12_SEGMENT resource is found and this resource
    has the correct number of items (i.e. 16)."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00272',
    resource_name = 'SPM12_SEGMENT'
    correct_number = 16

    def run(self, experiment_id):
        e = self.xnat_instance.select.experiment(experiment_id)
        files = list(e.resource(self.resource_name).files())

        res = len(files) == self.correct_number
        if not res:
            import logging as log
            msg = '{} has {} items (different from {})'\
                  .format(experiment_id, len(files), self.correct_number)
            log.error(msg)

        return Results(res, data=[e.attributes()['Name'] for e in files])


class HasCorrectItems(ExperimentTest):
    """Passes if a SPM12_SEGMENT resource is found and such resource
    contains the main expected items."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00272',
    resource_name = 'SPM12_SEGMENT'
    expected_items = ['rc1*.nii.gz',
                      'rc2*.nii.gz',
                      'c1*.nii.gz',
                      'c2*.nii.gz',
                      'c3*.nii.gz',
                      'c4*.nii.gz',
                      'c5*.nii.gz',
                      'y_*.nii.gz',
                      'iy_*.nii.gz',
                      '*_seg8.mat',
                      'pyscript_setorigin.m',
                      'pyscript_newsegment.m']

    def run(self, experiment_id):
        from fnmatch import fnmatch

        e = self.xnat_instance.select.experiment(experiment_id)
        res = e.resource(self.resource_name)

        file_list = set([e.attributes()['Name'] for e in res.files()])

        missing = []
        for e in self.expected_items:
            if not [f for f in file_list if fnmatch(f, e)]:
                missing.append(e)

        msg = []
        result = True
        if missing:
            result = False
            msg.append('Missing {} items: {}.'.format(self.resource_name,
                                                      missing))

        return Results(result, data=msg)


class HasCorrectSPMVersion(ExperimentTest):
    """This test checks the version of SPM used. Passes if SPM12_SEGMENT outputs
    were created using the expected version (i.e. `SPM12 Release 7219`)."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00251',
    resource_name = 'SPM12_SEGMENT'
    expected_version = 'SPM version: SPM12 Release: 7219'

    def run(self, experiment_id):

        data = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                    columns=['label']).data
        columns = ['label', 'project', 'subject_ID']
        exp_label, proj, subj_id = [data[0][e] for e in columns]

        s = self.xnat_instance.select.project(proj).subject(subj_id)
        res = s.experiment(experiment_id).resource(self.resource_name)
        log = res.file('LOGS/{}.log'.format(exp_label))
        if not log.exists():
            return Results(False, data=['{} log file not found.'
                                        .format(self.resource_name)])

        log_data = self.xnat_instance.get(log.attributes()['URI']).text
        spm_version = [line for line in log_data.splitlines()
                       if line.startswith('SPM version:')]

        if not spm_version:
            return Results(False, data=['No SPM version '
                                        'registered in the logs.'])
        elif list(set(spm_version)) != [self.expected_version]:
            return Results(False, data=list(set(spm_version)))

        return Results(True, [])


class HasCorrectMatlabVersion(ExperimentTest):
    """This test checks the version of Matlab used by SPM toolbox. Passes if
    MCR version matches `7.10.0.499` and Matlab version matches `R2010a`;
    fails otherwise."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00251',
    resource_name = 'SPM12_SEGMENT'

    def run(self, experiment_id):
        expected_version = 'MATLAB Version 7.10.0.499 (R2010a)'
        result = True
        msg = []

        data = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                    columns=['label']).data
        columns = ['label', 'project', 'subject_ID']
        exp_label, proj, subj_id = [data[0][e] for e in columns]

        s = self.xnat_instance.select.project(proj).subject(subj_id)
        res = s.experiment(experiment_id).resource(self.resource_name)
        log = res.file('LOGS/{}.log'.format(exp_label))

        if not log.exists():
            return Results(False, data=['{} log file not found.'
                                        .format(self.resource_name)])

        log_data = self.xnat_instance.get(log.attributes()['URI']).text
        matlab_version = [line for line in log_data.splitlines()
                          if line.startswith('MATLAB Version')]

        if not matlab_version or matlab_version[0] != expected_version:
            result = False
            msg.append('Incorrect Matlab version: {}'.format(matlab_version))

        return Results(result, data=msg)


class HasCorrectOSVersion(ExperimentTest):
    """This test checks the OS version on which SPM12_SEGMENT was executed.
    Passes if OS version matches the expected kernel version (`4.4.120-92.70`);
    fails otherwise."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00251',
    resource_name = 'SPM12_SEGMENT'

    def run(self, experiment_id):
        expected_version = 'Operating System: Linux 4.4.120-92.70-default'
        result = True
        msg = []

        data = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                    columns=['label']).data
        columns = ['label', 'project', 'subject_ID']
        exp_label, proj, subj_id = [data[0][e] for e in columns]

        s = self.xnat_instance.select.project(proj).subject(subj_id)
        res = s.experiment(experiment_id).resource(self.resource_name)
        log = res.file('LOGS/{}.log'.format(exp_label))

        if not log.exists():
            return Results(False, data=['{} log file not found.'
                                        .format(self.resource_name)])

        log_data = self.xnat_instance.get(log.attributes()['URI']).text
        kernel_info = [line for line in log_data.splitlines()
                       if line.startswith('Operating System:')]
        if not kernel_info:
            result = False
            msg.append('No OS information found.')

        kernel_version = kernel_info.pop()
        if not kernel_version.startswith(expected_version):
            result = False
            msg.append('Incorrect OS version: {}.'.format(kernel_version))

        return Results(result, data=msg)


class SPM12SegmentSnapshot(ExperimentTest):
    """This test creates a snapshot of the results generated by SPM12_SEGMENT.
    Passes if the snapshot is created successfully. Fails otherwise. Does not
    tell anything on the segmentation quality."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00754',
    resource_name = 'SPM12_SEGMENT'

    def run(self, experiment_id):
        from . import __download_data__
        from nisnap import snap
        import tempfile

        axes = 'xyz'
        slices = {'x': list(range(130, 210, 4)),
                  'y': list(range(80, 200, 6)),
                  'z': list(range(50, 190, 6))}
        rowsize = {'x': 10, 'y': 10, 'z': 8}
        figsize = {'x': (18, 4), 'y': (18, 4), 'z': (18, 5)}

        if os.getenv('SKIP_SNAPSHOTS_TESTS') == 'True':
            return Results(experiment_id == self.passing[0],
                           data=['Skipping it. (SKIP_SNAPSHOTS_TESTS)'])

        try:
            bg, filepaths = __download_data__(self.xnat_instance,
                                              experiment_id,
                                              self.resource_name)

            # Create snapshot with proper options
            fd, snap_fp = tempfile.mkstemp(suffix=snap.__format__)
            os.close(fd)
            snap.plot_segment(filepaths, axes=axes, bg=bg, opacity=70,
                              slices=slices, animated=False, savefig=snap_fp,
                              figsize=figsize, rowsize=rowsize,
                              contours=False, samebox=True)

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


class HasNormalSPM12Volumes(ExperimentTest):
    """This test runs the quality-predicting procedure on the SPM12_SEGMENT
    resource based on its estimated GM and WM volumes estimated by SPM12.
    Test passes if volumes are within boundaries, i.e. `GM` volume ranges
    between 480000 and 900000; `WM` volume ranges between 300000 and 600000).
    Test fails otherwise."""

    passing = 'BBRCDEV_E00559',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT'
    file_prefixes = ['c1', 'c2', 'c3']

    def check(self, vols):
        boundaries = [('c1', [480000, 900000]),
                      ('c2', [300000, 600000])]
        has_passed = True

        for (col, (bmin, bmax)), subject_val in zip(boundaries, vols[:2]):
            sv = float(subject_val)
            if sv > float(bmax) or sv < float(bmin):
                has_passed = False
        return has_passed

    def run(self, experiment_id):
        import tempfile
        import nibabel as nib
        import numpy as np
        import os

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        if not r.exists():
            return Results(False, data=['Missing {} resource'
                                        .format(self.resource_name)])
        vols = []
        fd, fp = tempfile.mkstemp(suffix='.nii.gz')
        os.close(fd)

        for kls in self.file_prefixes:
            try:
                f = [each for each in r.files() if each.id().startswith(kls)][0]
            except IndexError:
                return Results(False, data=['Some SPM maps are missing, check '
                                            '`HasCorrectItems` test results.'])
            f.get(fp)
            d = nib.load(fp)
            size = np.prod(d.header['pixdim'].tolist()[:4])
            v = np.sum(d.dataobj) * size
            vols.append(v)

        os.remove(fp)
        res = self.check(vols)
        return Results(res, data=['Volumes: {} {}'.format(vols[0], vols[1])])


class SPM12SegmentExecutionTime(ExperimentTest):
    """This test checks the execution time of `SPM12_SEGMENT` in the log files.
    The test passes if execution timespan is within an acceptable range of time
    (i.e. 5 to 30 minutes); fails otherwise."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E01613',
    resource_name = 'SPM12_SEGMENT'

    def run(self, experiment_id):
        import re
        import dateparser
        from datetime import timedelta

        e = self.xnat_instance.select.experiment(experiment_id)
        log_urn = '/LOGS/{}.log'.format(e.label())
        log_file = e.resource(self.resource_name).file(log_urn)
        if not log_file.exists():
            return Results(False, data=['No {} log files found.'
                                        .format(self.resource_name)])

        log_data = self.xnat_instance.get(log_file._uri).content.decode('utf-8')

        start_end_tags = ['SPM12: spm_preproc_run',
                          'Completed                               :']
        dates = []
        for tag in start_end_tags:
            for line in log_data.splitlines():
                if line.startswith(tag):
                    time, _, date = re.split(r'\s+', line)[-3:]
                    dates.append(dateparser.parse(date + ' ' + time))
                    break

        if len(dates) != 2:
            return Results(False, data=['Invalid {} log file.'
                                        .format(self.resource_name)])

        result = False
        tdelta = max(dates) - min(dates)
        if timedelta(minutes=5) < tdelta < timedelta(minutes=30):
            result = True

        return Results(result, data=['{}'.format(tdelta)])
