from ..test import ExperimentTest, Results
from ..sanity import data
import json
import os
from nisnap.utils import aseg
from . import Snapshot


class HasCorrectItems(ExperimentTest):
    """Passes if a FREESURFER6 resource and the expected files according to a
    given list (see report) are found. Unknown items are reported unless
    identified as hippocampal subfields (or related), "touch" or log files.
    Fails if some expected files are found missing and returns a list."""

    passing = 'BBRCDEV_E00365',
    failing = 'BBRCDEV_E00251',
    resource_name = 'FREESURFER6'
    hippo_items = ['lh.hippoSfLabels-{}.v10.mgz',
                   'rh.hippoSfLabels-{}.v10.mgz',
                   'lh.hippoSfLabels-{}.v10.FSvoxelSpace.mgz',
                   'rh.hippoSfLabels-{}.v10.FSvoxelSpace.mgz',
                   'lh.hippoSfVolumes-{}.v10.txt',
                   'rh.hippoSfVolumes-{}.v10.txt']
    monomodal_items = ['hippocampal-subfields-T1.log']
    multimodal_items = ['{}.FSspace.mgz',
                        'T1_to_{}.v10.lta',
                        'T1_to_{}.v10.QC.gif',
                        'T1_to_{}.v10.info']

    def run(self, experiment_id):
        import os.path as op
        import bbrc

        fn = '%s_items.json' % self.resource_name.lower()

        fp = op.join(op.dirname(bbrc.__file__), 'data', fn)
        with open(fp, 'r') as f:
            fsitems = json.load(f)

        x = self.xnat_instance
        r = x.select.experiment(experiment_id).resource(self.resource_name)
        attrs = x._get_json(r._uri + '/files')
        filenames = set([e['Name'] for e in attrs])

        common = filenames.intersection(fsitems)
        res = len(common) == len(fsitems)
        url = 'https://gitlab.com/bbrc/xnat/bbrc-validator/blob/master/data/%s'
        url = url % fn

        missing = set(fsitems).difference(filenames)
        missing = ', '.join(missing) if len(missing) > 0 else 'None'
        unknown = set(filenames).difference(fsitems)

        # Are there any hippocampus segmentations?
        found_hippo = []
        ignored = 0
        for each in ['T1', 'T1-T1T2', 'T1-T1IR']:
            is_found = True
            hi = set([i.format(each) for i in self.hippo_items])
            if each == 'T1':
                hi = hi.union(self.monomodal_items)
            elif each in ['T1-T1T2', 'T1-T1IR']:
                hi = hi.union([e.format(each[-4:]) for e in self.multimodal_items])
            is_found = len(hi.difference(filenames)) == 0
            if is_found:
                found_hippo.append(each)

            # removing any hippocampus-related files
            items = [i.format(each) for i in self.hippo_items]
            ignored = ignored + len(unknown.intersection(items))
            unknown = unknown.difference(hi)

        # Are there any temporary files? Remove them from unknown
        tmp = [e['Name'] for e in attrs if '/tmp/' in e['path']
               or 'LOGS' in e['path'] or 'touch' in e['path']]
        tmp = set(tmp).difference(set(fsitems))
        ignored = ignored + len(tmp)
        unknown = unknown.difference(tmp)

        unknown = ', '.join(unknown) if len(unknown) > 0 else 'None'
        msg = '%s has %s items, %s in common with the [full list](%s) '\
            '(ignored: %s) (missing: %s) (unknown: %s) (found hippo: %s)'\
            % (experiment_id, len(attrs), len(common), url, ignored, missing,
               unknown, ', '.join(['**%s**' % e for e in found_hippo]))

        return Results(res, data=[msg])


class HasCorrectFreeSurferVersion(ExperimentTest):
    """This test checks the version of FreeSurfer used. Passes if FREESURFER6
    outputs were created using the expected version"""

    passing = 'BBRCDEV_E00365',
    failing = 'BBRCDEV_E00251',
    resource_name = 'FREESURFER6'
    freesurfer_version = 'freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0-2beb96c'
    __doc__ = __doc__ + ' (expected version: %s).' % freesurfer_version

    def run(self, experiment_id):
        filename = 'build-stamp.txt'
        x = self.xnat_instance
        r = x.select.experiment(experiment_id).resource(self.resource_name)
        data = x._get_json(r._uri + '/files')
        uris = [e['URI'] for e in data if e['Name'] == filename]

        if len(uris) < 1:
            msg = 'FreeSurfer version file (%s) not found.' % filename
            return Results(False, data=[])

        for uri in uris:
            buildstamp_log = x.get(uri).text.strip()
            if buildstamp_log != self.freesurfer_version:
                msg = 'Incorrect FreeSurfer version: %s' % buildstamp_log
                return Results(False, data=[msg])
        return Results(True, data=[])


class HasCorrectOSVersion(ExperimentTest):
    """This test checks the OS kernel version on which FreeSurfer was executed.
    Passes if OS kernel version matches the expected version"""

    passing = 'BBRCDEV_E00013',
    failing = 'BBRCDEV_E00365',
    resource_name = 'FREESURFER6'
    kernel_version = '4.4.120-92.70-default'
    __doc__ = __doc__ + ' (expected version: %s).' % kernel_version

    def run(self, experiment_id):

        filename = 'recon-all.env'
        x = self.xnat_instance
        r = x.select.experiment(experiment_id).resource(self.resource_name)
        data = x._get_json(r._uri + '/files')
        uris = [e['URI'] for e in data if e['Name'] == filename]

        if len(uris) < 1:
            msg = 'OS environment file (%s) not found.' % filename
            return Results(False, data=[msg])

        for uri in uris:
            kernel_version_line = x.get(uri).text.splitlines()[6]
            if self.kernel_version not in kernel_version_line:
                msg = 'Incorrect OS version: %s' % kernel_version_line.strip()
                return Results(False, data=[msg])
        return Results(True, data=[])


class IsT1OnlyHippocampalSegmentation(ExperimentTest):
    """This test asserts that FREESURFER6 resource contains valid T1w-only (mode A)
    hippocampal segmentation outputs. Passes if expected T1w-only output files
    generated by FreeSurfer hippocampal segmentation procedure are found;
    fails otherwise."""

    passing = 'BBRCDEV_E00365',
    failing = 'BBRCDEV_E00015',
    resource_name = 'FREESURFER6'
    items = ['lh.hippoSfLabels-T1.v10.mgz',
             'rh.hippoSfLabels-T1.v10.mgz',
             'lh.hippoSfLabels-T1.v10.FSvoxelSpace.mgz',
             'rh.hippoSfLabels-T1.v10.FSvoxelSpace.mgz',
             'lh.hippoSfVolumes-T1.v10.txt',
             'rh.hippoSfVolumes-T1.v10.txt']

    def run(self, experiment_id):

        result = False

        x = self.xnat_instance
        r = x.select.experiment(experiment_id).resource(self.resource_name)
        data = x._get_json(r._uri + '/files')

        full_items = set([e['Name'] for e in data])
        common_items = full_items.intersection(self.items)

        uri = [e['URI'] for e in data
               if 'hippocampal-subfields-T1.log' == str(e['Name'])]

        if len(uri) != 1:
            msg = 'T1-only hippocampal segmentation log file '\
                '(hippocampal-subfields-T1.log) not found.'
            return Results(False, data=[msg])

        logfile = x.get(uri[0]).text

        is_t1only = [l for l in logfile.splitlines()
                     if l.startswith('#@# Hippocampal Subfields processing (T1)')
                     or l.startswith('#@# Hippocampal Subfields processing (T1 only)')]
        if is_t1only and len(common_items) == len(self.items):
            result = True

        msg = []
        if not result:
            missing_items = [e for e in self.items if e not in full_items]
            if missing_items:
                m = 'T1-only hippocampal segmentation results missing files: %s'\
                    % ', '.join(missing_items)
                msg.append(m)

        return Results(result, data=msg)


class IsT1T2HippocampalSegmentation(ExperimentTest):
    """This test asserts that FREESURFER6 resource contains T1w+T2w multispectral
    (mode B) hippocampal segmentation outputs. Passes if expected T1w+T2w output
    files generated by FreeSurfer hippocampal segmentation procedure are found;
    fails otherwise."""

    passing = 'BBRCDEV_E00015',
    failing = 'BBRCDEV_E00365',
    resource_name = 'FREESURFER6'
    items = ['T1T2.FSspace.mgz',
             'lh.hippoSfLabels-T1-T1T2.v10.mgz',
             'rh.hippoSfLabels-T1-T1T2.v10.mgz',
             'lh.hippoSfLabels-T1-T1T2.v10.FSvoxelSpace.mgz',
             'rh.hippoSfLabels-T1-T1T2.v10.FSvoxelSpace.mgz',
             'lh.hippoSfVolumes-T1-T1T2.v10.txt',
             'rh.hippoSfVolumes-T1-T1T2.v10.txt']

    def run(self, experiment_id):

        result = False

        x = self.xnat_instance
        r = x.select.experiment(experiment_id).resource(self.resource_name)
        data = x._get_json(r._uri + '/files')

        full_items = set([e['Name'] for e in data])
        common_items = full_items.intersection(self.items)

        result = len(common_items) == len(self.items)

        msg = []
        if not result:
            missing_items = [e for e in self.items if e not in full_items]
            if missing_items:
                m = 'Missing files: %s'\
                    % ', '.join(missing_items)
                msg.append(m)

        return Results(result, data=msg)


class IsT1IRHippocampalSegmentation(IsT1T2HippocampalSegmentation):
    """This test asserts that FREESURFER6 resource contains T1w+IR multispectral
    (mode B) hippocampal segmentation outputs. Passes if expected T1w+IR output
    files generated by FreeSurfer hippocampal segmentation procedure are found;
    fails otherwise."""
    __doc__ = IsT1T2HippocampalSegmentation.__doc__.replace('T2w','IR')

    passing = 'BBRCDEV_E00399',
    failing = 'BBRCDEV_E00365',
    resource_name = 'FREESURFER6'
    items = ['T1IR.FSspace.mgz',
             'lh.hippoSfLabels-T1-T1IR.v10.mgz',
             'rh.hippoSfLabels-T1-T1IR.v10.mgz',
             'lh.hippoSfLabels-T1-T1IR.v10.FSvoxelSpace.mgz',
             'rh.hippoSfLabels-T1-T1IR.v10.FSvoxelSpace.mgz',
             'lh.hippoSfVolumes-T1-T1IR.v10.txt',
             'rh.hippoSfVolumes-T1-T1IR.v10.txt']


class IsT2MultispectralHippoSegRunnable(ExperimentTest):
    """This test checks that the given MRSession can run FreeSurfer's hippocampal
    segmentation in multispectral mode (mode B) by using an additional T2w scan.
    Fails if no T2w scans are available for running the hippocampal segmentation
    in multispectral mode; passes otherwise."""

    passing = 'BBRCDEV_E00399',
    failing = 'BBRCDEV_E00365',
    resource_name = 'FREESURFER6'
    test_name = 'HasUsableT2'

    def run(self, experiment_id):
        x = HasCorrectItems(self.lut, self.xnat_instance)
        x.resource_name = self.resource_name
        res = x.run(experiment_id)

        if not res.has_passed:
            msg = 'Invalid FreeSurfer baseline results. Not runnable.'
            return Results(False, data=[msg])

        test = eval('data.{}'.format(self.test_name))
        res = test(self.lut, self.xnat_instance).run(experiment_id)
        if not res.has_passed:
            msg = '{} Not runnable.'.format(res.data[0])
            return Results(False, data=[msg])

        return Results(True, data=[])


class IsIRMultispectralHippoSegRunnable(IsT2MultispectralHippoSegRunnable):
    __doc__ = IsT2MultispectralHippoSegRunnable.__doc__.replace('T2w', 'IR')

    passing = 'BBRCDEV_E00399',
    failing = 'BBRCDEV_E00365',
    resource_name = 'FREESURFER6'
    test_name = 'HasUsableIR'


class IsFreeSurferTimewiseConsistent(ExperimentTest):
    """Processing outputs should *always* be posterior to their input data.
    This Test checks that FreeSurfer outputs are chronologically consistent
    with (i.e. newer than) the date of insertion of the MRSession in XNAT and
    the date of creation of the NIFTI converted image files."""

    passing = 'BBRCDEV_E00013',
    failing = 'BBRCDEV_E00281',
    resource_name = 'FREESURFER6'

    def get_niifiles_modification_date(self, exp_id):
        from datetime import datetime

        e = self.xnat_instance.select.experiment(exp_id)
        uri = e._uri + '/scans/*/resources/NIFTI/files'
        files = self.xnat_instance._get_json(uri)
        headers = self.xnat_instance._get_head(files[0]['URI'])
        modified_date = headers['Last-Modified']
        return datetime.strptime(modified_date, '%a, %d %b %Y %H:%M:%S %Z')

    def get_mrsession_insert_date(self, exp_id):
        from datetime import datetime
        x = self.xnat_instance
        insert_dates = x.array.experiments(experiment_id=exp_id,
                                           columns=['insert_date']).data
        insert_date_str = insert_dates[0]['insert_date']
        return datetime.strptime(insert_date_str, '%Y-%m-%d %H:%M:%S.%f')

    def get_reconall_end_dates(self, exp_id):
        from fnmatch import fnmatch

        uri = '/data/experiments/%s/resources/%s/files'\
              % (exp_id, self.resource_name)
        file_list = self.xnat_instance._get_json(uri)

        uri = [elem['URI'] for elem in file_list
               if elem['Name'] == 'recon-all.log']
        if len(uri) != 1:
            return None

        reconall_log_content = self.xnat_instance.get(uri[0]).text
        text = 'recon-all -s * finished without error *'
        end_dates = [self.parse_reconall_end_date(line)
                     for line in reconall_log_content.splitlines()
                     if fnmatch(line, text)]

        return end_dates

    def parse_reconall_end_date(self, line):
        import dateparser

        date_text = line.split('finished without error at ')[1].strip()
        # exclude unneeded week-day abbreviation to avoid spanish issue with
        # 'mar' (Martes/Marzo)
        date_text = date_text[4:]
        date = dateparser.parse(date_text)

        # FIX: return an offset-naive datetime to enable comparing with others
        return date.replace(tzinfo=None)

    def run(self, experiment_id):
        insert_date = self.get_mrsession_insert_date(experiment_id)
        nifti_date = self.get_niifiles_modification_date(experiment_id)
        fs_dates = self.get_reconall_end_dates(experiment_id)

        if not fs_dates:
            msg = 'FreeSurfer recon-all.log file not found. Skipping.'
            return Results(False, data=[msg])

        if nifti_date > fs_dates[0]:
            msg = 'NIFTI files were generated (%s) *AFTER* running '\
                  'FreeSurfer recon-all (%s).' % (nifti_date, fs_dates[0])
            return Results(False, [msg])
        if insert_date > fs_dates[0]:
            msg = 'XNAT MRSession was inserted (%s) *AFTER* running '\
                  'FreeSurfer recon-all (%s).' % (insert_date, fs_dates[0])
            return Results(False, [msg])

        return Results(True, data=[])


class ReconAllAsegSnapshot(ExperimentTest, Snapshot):
    """This test creates a snapshot of the results generated by FREESURFER6
    focusing on central subcortical structures. Passes if the snapshot is
    created successfully. Fails otherwise. Does not tell anything on the
    segmentation quality."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00754',  # has no FreeSurfer6 resource
    resource_name = 'FREESURFER6'
    axes = 'x'
    figsize = {'x': (23, 15)}
    rowsize = {'x': 8}
    n_slices = {'x': 48}
    labels = aseg.basal_ganglia_labels
    step = 1
    threshold = 75

    def run(self, experiment_id):
        return Snapshot.run(self, experiment_id)

    def report(self):
        return Snapshot.report(self)


class ReconAllAparcSnapshot(ExperimentTest, Snapshot):
    """This test creates a snapshot of the results generated by FREESURFER6
    focusing on cortical areas and others (CSF, corpus callosum). Passes if the
    snapshot is created successfully. Fails otherwise. Does not tell anything on
    the segmentation quality."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00754',  # has no FreeSurfer6 resource
    resource_name = 'FREESURFER6'

    axes = 'xz'
    figsize = {'x': (16, 14), 'z': (16, 10)}
    rowsize = {'x': 5, 'z': 5}
    n_slices = {'x': 20, 'z': 24}
    labels = aseg.cortical_labels
    step = 3
    threshold = 75

    def run(self, experiment_id):
        return Snapshot.run(self, experiment_id)

    def report(self):
        return Snapshot.report(self)


class AreCAVolumesConsistent(ExperimentTest):
    """Checks that CA1, CA2 and CA3 (_Cornu Ammonis_ areas) display the
    expected order in volumes in the resulting segmentation.
    consistent in size. Passes if `CA1` > `CA4` > `CA3` and fails otherwise."""

    passing = 'BBRCDEV_E00013',
    failing = 'BBRCDEV_E00281',
    resource_name = 'FREESURFER6'

    def run(self, experiment_id):
        import operator
        import pandas as pd

        regions = ['CA3', 'CA4', 'CA1']

        res = []
        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        if not r.exists():
            msg = 'No %s resource found.' % self.resource_name
            return Results(False, data=[msg])

        for mode in ['T1', 'T1-T1T2', 'T1-T1IR']:
            ca_vols = r.hippoSfVolumes(mode=mode)
            ca_vols['value'] = pd.to_numeric(ca_vols['value'])

            for s in ['left', 'right']:
                q = ca_vols.query('side == "%s"' % s)[['region', 'value']]
                pt = pd.pivot_table(q, index='region', values='value')
                ca = pt.to_dict()
                if len(ca.items()) == 0:
                    continue

                # filter out non-CA regions dataframe and
                # merge FS7 CA partial volumes (head + body)
                ca2 = dict.fromkeys(regions, 0)
                for k, v in ca['value'].items():
                    if k[:3] in regions:
                        ca2[k[:3]] += v

                sorted_ca_vols = [s[0] for s in sorted(ca2.items(),
                                                       key=operator.itemgetter(1))]
                if sorted_ca_vols != regions:
                    msg = '%s-%s: %s' % (mode, s,
                                         ' < '.join(sorted_ca_vols))
                    res.append(msg)

        if res:
            return Results(False, data=['Inconsistent CA volume sizes (%s)'
                                        % ",".join(res)])
        else:
            return Results(True, data=[])


class HasAbnormalAsegFeatures(ExperimentTest):
    """Checks whether FreeSurfer-generated `aseg` features are within target
    intervals defined by 99th-percentiles of a sample distribution (estimated
    on all results from ALFA_OPCIONAL and ALFA_PLUS projects). Features include
    raw volumes and standard deviation of intensity values measured over each
    region's mask. Passes if less than 5 regions show abnormal values (counting
    both volumes and std). Fails otherwise."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E02443',
    resource_name = 'FREESURFER6'
    threshold = 5

    def run(self, experiment_id):

        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        if not r.exists():
            msg = 'No %s resource found.' % self.resource_name
            return Results(False, data=[msg])

        import pandas as pd
        aseg = r.aseg()
        aseg['value'] = pd.to_numeric(aseg['value'])
        import bbrc
        import os.path as op

        fn = 'ALFA_OPCIONAL_PLUS_%s_99th_percentiles.xls' % self.resource_name
        fp = op.join(op.dirname(bbrc.__file__), 'data', fn)
        converters = {'Volume_mm3_low': float,
                      'Volume_mm3_high': float,
                      'normStdDev_low': float,
                      'normStdDev_high': float}
        perc = pd.read_excel(fp, converters=converters).set_index('region')

        outliers = []
        for region, row in perc.iterrows():
            q = 'region == "%s" & measurement == "Volume_mm3"' % region
            vol = aseg.query(q)['value'].tolist()[0]
            q = 'region == "%s" & measurement == "normStdDev"' % region
            std = aseg.query(q)['value'].tolist()[0]

            if row['Volume_mm3_low'] > vol or\
                    row['Volume_mm3_high'] < vol:
                outliers.append('%s_volume' % region)
            if row['normStdDev_low'] > std or\
                    row['normStdDev_high'] < std:
                outliers.append('%s_std' % region)

        msg = 'Regions out of target interval: %s (%s)'\
              % (outliers, len(outliers))
        return Results(len(outliers) < self.threshold, data=[msg])
