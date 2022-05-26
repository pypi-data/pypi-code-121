from ..test import ExperimentTest, Results


class HasCorrectItems(ExperimentTest):
    """Passes if a CAT12_SEGMENT resource is found and such resource contains
    the main expected items."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00272',

    def run(self, experiment_id):
        from fnmatch import fnmatch

        expected_items = ['rp1*.nii.gz',
                          'rp2*.nii.gz',
                          'p0*.nii.gz',
                          'p1*.nii.gz',
                          'p2*.nii.gz',
                          'p3*.nii.gz',
                          'y_*.nii.gz',
                          'iy_*.nii.gz',
                          'catlog_*.txt',
                          'cat_*.mat',
                          'cat_*.xml',
                          'catreport_*.pdf',
                          'catreportj_*.jpg',
                          'pyscript.m']

        e = self.xnat_instance.select.experiment(experiment_id)
        res = e.resource('CAT12_SEGMENT')

        file_list = set([e.attributes()['Name'] for e in res.files()])
        missing = []
        for e in expected_items:
            if not [f for f in file_list if fnmatch(f, e)]:
                missing.append(e)

        if missing:
            return Results(False, data=missing)

        return Results(True, data=[])

    def report(self):
        report = []
        if self.results.data:
            item = ('Missing items: %s.' % self.results.data).replace('\'', '`')
            report.append(item)
        return report


class HasCorrectCATVersion(ExperimentTest):
    """This test checks the version of `CAT` used. Passes if CAT12_SEGMENT
    outputs were created using the expected version (i.e. `CAT12.6 Release: 1450`)."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00272',

    def run(self, experiment_id):

        expected_cat_version = 'CAT version: CAT12.6 Release: 1450'

        data = self.xnat_instance.array.mrsessions(experiment_id=experiment_id,
                                                   columns=['label']).data
        columns = ['label', 'project', 'xnat:mrsessiondata/subject_id']
        exp_label, project, subject_id = [data[0][e] for e in columns]

        res = self.xnat_instance.select.project(project).subject(subject_id)\
            .experiment(experiment_id).resource('CAT12_SEGMENT')
        log = res.file('LOGS/%s.log' % exp_label)

        if not log.exists():
            return Results(False, data=['CAT12Segment log file not found.'])

        log_data = self.xnat_instance.get(log.attributes()['URI']).text
        cat_version = [line for line in log_data.splitlines()
                       if line.startswith('CAT version:')]

        if not cat_version or cat_version[0] != expected_cat_version:
            return Results(False, data=['Incorrect CAT version: %s' % cat_version])

        return Results(True, data=[])


class HasCorrectSPMVersion(ExperimentTest):
    """This test checks the version of `SPM` used by CAT toolbox. Passes
    if CAT12_SEGMENT outputs were created using the expected SPM version
    (i.e. `SPM12 Release: 7487`)."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00272',

    def run(self, experiment_id):

        expected_spm_version = 'SPM version: SPM12 Release: 7487'

        data = self.xnat_instance.array.mrsessions(experiment_id=experiment_id,
                                                   columns=['label']).data
        elements = ['label', 'project', 'xnat:mrsessiondata/subject_id']
        exp_label, project, subject_id = [data[0][e] for e in elements]

        res = self.xnat_instance.select.project(project).subject(subject_id)\
            .experiment(experiment_id).resource('CAT12_SEGMENT')
        log = res.file('LOGS/%s.log' % exp_label)

        if not log.exists():
            return Results(False, data=['CAT12Segment log file not found.'])

        log_data = self.xnat_instance.get(log.attributes()['URI']).text
        spm_version = [line for line in log_data.splitlines() if line.startswith('SPM version:')]

        if not spm_version or spm_version[0] != expected_spm_version:
            return Results(False, data=['Incorrect SPM version: %s' % spm_version])

        return Results(True, data=[])


class HasCorrectMatlabVersion(ExperimentTest):
    """This test checks the version of `MATLAB` used by CAT toolbox. Passes
    if CAT12_SEGMENT outputs were created using the expected version
    (i.e. `9.5.0 (R2018b)`)."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00272',

    def run(self, experiment_id):
        from fnmatch import fnmatch

        expected_matlab_version = 'MATLAB Version: 9.5.0* (R2018b)*'

        data = self.xnat_instance.array.mrsessions(experiment_id=experiment_id,
                                                   columns=['label']).data
        elements = ['label', 'project', 'xnat:mrsessiondata/subject_id']
        exp_label, project, subject_id = [data[0][e] for e in elements]

        res = self.xnat_instance.select.project(project).subject(subject_id)\
            .experiment(experiment_id).resource('CAT12_SEGMENT')
        log = res.file('LOGS/%s.log' % exp_label)

        if not log.exists():
            return Results(False, data=['CAT12Segment log file not found.'])

        log_data = self.xnat_instance.get(log.attributes()['URI']).text

        matlab_version = [line for line in log_data.splitlines()
                          if line.startswith('MATLAB Version')]
        if not matlab_version or not fnmatch(matlab_version[0], expected_matlab_version):
            return Results(False, data=['Incorrect Matlab version: %s'
                                        % matlab_version])

        return Results(True, data=[])


class HasCorrectOSVersion(ExperimentTest):
    """This test checks the OS version on which CAT12_SEGMENT was executed.
    Passes if OS version matches the expected version (i.e. `Linux 4.4.120`);
    fails otherwise."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00375',

    def run(self, experiment_id):
        from fnmatch import fnmatch

        expected_kernel_version = 'Operating System: Linux 4.4.120*'

        data = self.xnat_instance.array.mrsessions(experiment_id=experiment_id,
                                                   columns=['label']).data
        elements = ['label', 'project', 'xnat:mrsessiondata/subject_id']
        exp_label, project, subject_id = [data[0][e] for e in elements]

        res = self.xnat_instance.select.project(project).subject(subject_id)\
            .experiment(experiment_id).resource('CAT12_SEGMENT')
        log = res.file('LOGS/%s.log' % exp_label)

        if not log.exists():
            return Results(False, data=['CAT12Segment log file not found.'])

        log_data = self.xnat_instance.get(log.attributes()['URI']).text
        kernel_version = [line for line in log_data.splitlines()
                          if line.startswith('Operating System:')]

        if not kernel_version or \
                not fnmatch(kernel_version[0], expected_kernel_version):
            return Results(False, data=['Incorrect OS version: %s'
                                        % kernel_version])

        return Results(True, data=[])


class CAT12SegmentIQRScore(ExperimentTest):
    """This test checks the `Image Quality Rating` (IQR) score calculated by
    `CAT12 Segment`. This score is a weighted average of multiple data quality
    metrics (i.e. image resolution, noise and bias). Tests passes if `CAT12 Segment`
    IQR score is higher than a given threshold (i.e. 75%); fails otherwise."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E01613',

    def run(self, experiment_id):

        data = self.xnat_instance.array.mrsessions(experiment_id=experiment_id,
                                                   columns=['label']).data
        elements = ['label', 'project', 'xnat:mrsessiondata/subject_id']
        exp_label, project, subject_id = [data[0][e] for e in elements]

        res = self.xnat_instance.select.project(project).subject(subject_id) \
            .experiment(experiment_id).resource('CAT12_SEGMENT')
        log = res.file('LOGS/%s.log' % exp_label)
        if not log.exists():
            return Results(False, data=['CAT12Segment log file not found.'])
        log_data = self.xnat_instance.get(log.attributes()['URI']).text

        iqr = [line for line in log_data.splitlines()
               if line.startswith('Image Quality Rating (IQR)')]

        score_str = iqr[0].split(':')[1].strip()
        score = float(score_str.split('%')[0])
        return Results(bool(score > 75.0), data=['%s' % score_str])


class CAT12SegmentExecutionTime(ExperimentTest):
    """This test checks the execution time of `CAT12 Segment` command. Test
    passes if execution timespan is within an _acceptable_ range of time
    (i.e. 20 to 60 minutes); fails otherwise."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E01613',

    def run(self, experiment_id):
        import dateparser
        import datetime
        from fnmatch import fnmatch

        data = self.xnat_instance.array.mrsessions(experiment_id=experiment_id,
                                                   columns=['label']).data
        exp_label, project, subject_id = [data[0][e] for e in
                                          ['label', 'project',
                                           'xnat:mrsessiondata/subject_id']]

        res = self.xnat_instance.select.project(project).subject(subject_id) \
            .experiment(experiment_id).resource('CAT12_SEGMENT')
        log = res.file('LOGS/%s.log' % exp_label)
        if not log.exists():
            return Results(False, data=['CAT12Segment log file not found.'])
        log_data = self.xnat_instance.get(log.attributes()['URI']).text

        tags = ['* - Running \'CAT12: Segmentation\'',
                '* - Done    \'CAT12: Segmentation\'']
        dates = []
        for tag in tags:
            for line in log_data.splitlines():
                if fnmatch(line, tag):
                    dt = line.split(' - ')[0]
                    dates.append(dateparser.parse(dt))
                    break

        if len(dates) != 2:
            return Results(False, data=['Invalid CAT12_Segment log file.'])

        result = False
        tdelta = max(dates) - min(dates)
        if datetime.timedelta(minutes=20) < tdelta < datetime.timedelta(minutes=60):
            result = True

        return Results(result, data=['%s' % tdelta])


class CAT12SegmentSnapshot(ExperimentTest):
    """This test creates an snapshot of the results generated by CAT12_SEGMENT.
    Passes if the snapshot is created successfully. Fails otherwise. Does not
    tell anything on the segmentation quality."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E01613',

    def run(self, experiment_id):
        import os.path as op
        import os
        import tempfile
        from ..sanity import data

        # if os.getenv('SKIP_SNAPSHOTS_TESTS') == 'True':
        #     return Results(experiment_id == self.passing[0],
        #         data=['Skipping it. (SKIP_SNAPSHOTS_TESTS)'])

        p = data.HasPreferredT1(self.lut, self.xnat_instance)
        scan_id = p.preferred_t1(experiment_id)

        e = self.xnat_instance.select.experiment(experiment_id)
        resources_files = list(e.scan(scan_id).resource('NIFTI').files())

        if len(resources_files) == 0:
            return Results(False, data=['T1 not found.'])

        for f in resources_files:
            if f.label().endswith('.nii.gz'):
                break

        fd, t1_fp = tempfile.mkstemp(suffix='.nii.gz')
        os.close(fd)
        f.get(dest=t1_fp)

        resources_files = list(e.resource('CAT12_SEGMENT').files())

        if len(resources_files) == 0:
            return Results(False, data=['CAT12 results not found.'])

        for f in resources_files:
            if op.basename(f.label()).startswith('p1'):
                break

        if not op.basename(f.label()).startswith('p1'):
            return Results(False, data=['p1 map (CAT) not found.'])

        fd, c1_fp = tempfile.mkstemp(suffix='.nii.gz')
        os.close(fd)
        f.get(dest=c1_fp)

        from . import probamap_snapshot
        paths = probamap_snapshot(t1_fp, c1_fp)

        os.remove(t1_fp)
        os.remove(c1_fp)
        return Results(True, data=paths)

    def report(self):
        report = []

        for path in self.results.data:
            report.append('![snapshot](%s)' % path)
        return report


# class HasNormalCAT12Volumes(ExperimentTest):
