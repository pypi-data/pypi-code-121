from ..test import ExperimentTest, ScanTest, Results
from ..utils import __is_valid_scan__


class IsEven(ExperimentTest):
    """Returns True if the experiment_id is an even number, False if odd."""

    passing = '030423270818090',
    failing = '030423270818091',

    def run(self, experiment_id):
        sid = int(experiment_id)
        res = (sid % 2 == 0)
        return Results(res)


class HasDuplicatedSequence(ScanTest):
    """Every sequence should have a unique identifier (SeriesNumber).
    Fails if another scan exists with the same name. Passes if unique.
    Returns sequences (SeriesNumber) sharing an identical `scan-type` or
    scanning procedure definition."""

    passing = 'BBRCDEV_E00007', '401'
    failing = 'BBRCDEV_E00007', '1401'

    def run(self, experiment_id, scan_id):
        cols = ['xnat:imageScanData/quality',
                'xnat:imageScanData/type',
                'xsiType']
        # get metadata for each Experiment's scan
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=cols).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}
        scan_type = scans[scan_id]['xnat:imagescandata/type']

        # filter out unsuitable scan items
        valid_scans = {str(scan): scans[scan] for scan in scans
                       if __is_valid_scan__(self.xnat_instance, scans[scan])}

        # check occurrences of scans of type 'scan_type'
        from fnmatch import fnmatch
        matching_scans = [scan for scan in valid_scans if
                          fnmatch(valid_scans[scan]['xnat:imagescandata/type'],
                                  scan_type)]

        res = (len(matching_scans) == 1)
        data = {scan_type: matching_scans} if not res else None
        return Results(res, data=[data])


class HasDuplicatedSequences(ExperimentTest):
    """Every sequence should have a unique identifier (SeriesNumber).
    Fails if multiple scans have an identical `scan-type` or scanning procedure
    definition with the same name. Passes if `scan-type`s are unique.
    Returns sequences (SeriesNumber) sharing an identical `scan-type`."""

    passing = 'BBRCDEV_E00281',
    failing = 'BBRCDEV_E00007',

    def run(self, experiment_id):

        cols = ['xnat:imageScanData/quality',
                'xnat:imageScanData/type',
                'xnat:imageScanData/frames',
                'xsiType']
        # get metadata for each Experiment's scan
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=cols).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}

        # filter out unsuitable scan items
        valid_scans = {str(scan): scans[scan] for scan in scans
                       if __is_valid_scan__(self.xnat_instance, scans[scan])}
        scan_types = [valid_scans[e]['xnat:imagescandata/type']
                      for e, _ in valid_scans.items()]

        # check occurrences of scans of type 'scan_type'
        from fnmatch import fnmatch
        n_scans = {}
        for t in scan_types:
            n_scans[t] = [s_id for s_id, s_res in valid_scans.items()
                          if fnmatch(s_res['xnat:imagescandata/type'], t)]

        res = False not in [(len(ns) == 1) for ns in n_scans.values()]
        data = {}
        if not res:
            data = dict([(k, n) for k, n in n_scans.items() if len(n) != 1])

        return Results(res, data)

    def report(self):
        r = []
        for k, v in self.results.data.items():
            r.append('%s : %s<br>' % (k, ', '.join(v)))
        return r


class HasThumbnails(ScanTest):
    """Most datasets should have snapshots available for previewing if imaging
    data is valid. Note however that snapshot generation is disabled for 'complex'
    sequences such as fMRI,DWI and DTI (known XNAT behaviour). Test skipped if
    scan in excluded list. Test passes if snapshots exist. Fails if missing."""

    passing = 'BBRCDEV_E00272', '301'
    failing = 'BBRCDEV_E00013', '301'

    def run(self, experiment_id, scan_id):

        resource_label = 'SNAPSHOTS'
        excluded_scans = self.lut.get('DWI', []) + self.lut.get('RS', [])

        cols = ['ID', 'xnat:imageScanData/type']
        # check scan type/description against excluded list
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=cols).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}

        if scans[scan_id]['xnat:imagescandata/type'] in excluded_scans:
            msg = 'No thumbnails for `%s` scans (known bug). Skipping scan %s.'\
                  % (scans[scan_id]['xnat:imagescandata/type'], scan_id)
            return Results(None, data=[msg])

        # get resources' metadata for given scan
        scan = self.xnat_instance.select.experiment(experiment_id).scan(scan_id)
        uri = scan._uri + '/resources'
        resources = {e['xnat_abstractresource_id']: e
                     for e in self.xnat_instance._get_json(uri)}

        # filter suitable resources based on SNAPSHOTS resource content & label
        matching_resources = [resources[res_id] for res_id in resources
                              if resources[res_id]['content'] == resource_label
                              and resources[res_id]['label'] == resource_label
                              and resources[res_id]['file_count']
                              and int(resources[res_id]['file_count']) > 0]

        res = (len(matching_resources) >= 1)
        return Results(res)


class HasNifti(ScanTest):
    """Datasets are automatically converted to NIfTI (depending on project
    configuration). Test passes if the given scan has an existing NIfTI resource.
    Fails if NIfTI resource is missing."""

    passing = 'BBRCDEV_E00007', '301'
    failing = 'BBRCDEV_E00021', '101'

    def run(self, experiment_id, scan_id):

        resource_label = 'NIFTI'
        resource_content = 'NIFTI_RAW'

        # get resources' metadata for given scan
        scan = self.xnat_instance.select.experiment(experiment_id).scan(scan_id)
        uri = scan._uri + '/resources'
        resources = {e['xnat_abstractresource_id']: e
                     for e in self.xnat_instance._get_json(uri)}

        # filter suitable resources based on NIFTI resource content & label
        matching_resources = [resources[res_id] for res_id in resources
                              if resources[res_id]['content'] == resource_content
                              and resources[res_id]['label'] == resource_label
                              and resources[res_id]['file_count']
                              and int(resources[res_id]['file_count']) > 0]

        res = (len(matching_resources) >= 1)
        return Results(res)


class HasUncompressedPixelData(ScanTest):
    """Passes if the Pixel Data portion of the DICOM dataset is uncompressed.
    Fails otherwise."""

    passing = 'BBRCDEV_E00272', '301'
    failing = 'BBRCDEV_E00013', '301'

    def run(self, experiment_id, scan_id):

        from pydicom.uid import UncompressedPixelTransferSyntaxes

        cols = ['ID', 'label', 'project', 'subject_ID', 'subject_label']
        labels = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                      columns=cols).data[0]
        project_id = labels['project']

        # compose the URL for the XNAT dicomdump service
        uri = '/data/services/dicomdump'
        options = {'src': '/archive/projects/%s/experiments/%s/scans/%s' %
                          (project_id, experiment_id, scan_id),
                   'field': 'TransferSyntaxUID',
                   'format': 'csv'}

        from pyxnat.core.jsonutil import csv_to_json
        transfer_syntaxes = csv_to_json(
            str(self.xnat_instance.get(uri, params=options).text))

        # Transfer Syntax UID tag MUST be unique and mandatorily present
        # (DICOM standard compliance)
        if len(transfer_syntaxes) != 1:
            return Results(None, {'info': 'Transfer Syntax UID tag MUST '
                                          'be unique and mandatorily present'})

        tsyntax = transfer_syntaxes[0]
        res = bool(tsyntax['value'] in UncompressedPixelTransferSyntaxes)
        return Results(res)


class IsClassicDICOM(ScanTest):
    """Every dataset should be uploaded to XNAT using the classic DICOM format.
    Passes if the scan is stored in classic DICOM. Fails if stored in
    enhanced DICOM."""

    passing = 'BBRCDEV_E00272', '301'
    failing = 'BBRCDEV_E00007', '301'

    def run(self, experiment_id, scan_id):

        enhanced_mr_image_sops = \
            {'1.2.840.10008.5.1.4.1.1.4.1': 'Enhanced MR Image Storage',
             '1.2.840.10008.5.1.4.1.1.4.3': 'Enhanced MR Color Image Storage',
             '1.2.840.10008.5.1.4.1.1.4.4': 'Legacy Converted Enhanced MR Image Storage'}

        cols = ['ID', 'label', 'project', 'subject_ID']
        labels = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                      columns=cols).data[0]
        project_id = labels['project']

        # compose the URL for the XNAT dicomdump service
        uri = '/data/services/dicomdump'
        options = {'src': '/archive/projects/%s/experiments/%s/scans/%s' %
                          (project_id, experiment_id, scan_id),
                   'field': 'MediaStorageSOPClassUID',
                   'format': 'csv'}

        from pyxnat.core.jsonutil import csv_to_json
        sopclass_tags = csv_to_json(
            str(self.xnat_instance.get(uri, params=options).text))

        # SOPClass UID tag MUST be unique and mandatorily present
        # (DICOM standard compliance)
        if len(sopclass_tags) != 1:
            import logging as log
            log.error('Wrong SOPClassUID(s): %s' % sopclass_tags)
            return Results(False, data=['Unknown SOPClassUID %s' %
                                        sopclass_tags])
        sopclass_uid = sopclass_tags[0]
        res = bool(sopclass_uid['value'] not in enhanced_mr_image_sops.keys())
        return Results(res)


class HasPhilipsPrivateTags(ScanTest):
    """Passes if the dataset has Philips private tags stored in the DICOM
    header. Fails otherwise."""

    passing = 'BBRCDEV_E00014', '1501'
    failing = 'BBRCDEV_E00010', '1301'

    def run(self, experiment_id, scan_id):
        # Threshold based on observation to determine whether an study
        # has all Private groups info or it was emptied
        empty_groups_min_tag_length = (40, 80)

        cols = ['ID', 'label', 'project', 'subject_ID']
        labels = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                      columns=cols).data[0]
        project_id = labels['project']

        # compose the URL for the XNAT dicomdump service
        uri = '/data/services/dicomdump'
        options = {'src': '/archive/projects/%s/experiments/%s/scans/%s' %
                          (project_id, experiment_id, scan_id),
                   'format': 'csv'}

        from pyxnat.core.jsonutil import csv_to_json

        ans = self.xnat_instance.get(uri, params=options).text
        dicomdump_list = csv_to_json(str(ans).encode('utf-8'))

        philips_private_2001 = [item for item in dicomdump_list
                                if '(2001,' in str(item['tag1'])]
        philips_private_2005 = [item for item in dicomdump_list
                                if '(2005,' in str(item['tag1'])]

        private_groups_tag_length = (len(philips_private_2001),
                                     len(philips_private_2005))
        res = (private_groups_tag_length > empty_groups_min_tag_length)
        return Results(res)


class HasRescaleParameters(ScanTest):
    """Passes if the scan has `Rescale Intercept` and `Rescale Slope` parameters
    in the headers of its first DICOM file stored either as public or private
    DICOM fields. Fails otherwise."""

    passing = 'BBRCDEV_E00754', '501'
    failing = 'BBRCDEV_E00013', '301'

    def get_rescale_tags(self, dcmfile):
        import logging as log
        import pydicom

        inter = None
        slope = None

        ds = pydicom.dcmread(dcmfile)

        if 0x00281052 in ds and 0x00281053 in ds:
            inter = ds[0x00281052]
            slope = ds[0x00281053]
        elif 'Philips MR Imaging DD 005' in ds.private_creators(0x2005):
            philips_005_blk = ds.private_block(0x2005,
                                               'Philips MR Imaging DD 005')

            if 0x09 in philips_005_blk and 0x0A in philips_005_blk:
                inter = philips_005_blk[0x09]
                slope = philips_005_blk[0x0A]
            else:
                log.warning('No Rescale information found')
        else:
            log.warning('No Philips private group 2005 found')

        return inter, slope

    def run(self, experiment_id, scan_id):
        import tempfile
        import os

        data = []

        exp = self.xnat_instance.select.experiment(experiment_id)
        resource = exp.scan(scan_id).resource('DICOM')
        if not resource.exists():
            return Results(False, data=['No DICOM data available'])

        file = list(resource.files())[0]
        fd, fp = tempfile.mkstemp(suffix='.dcm')
        os.close(fd)
        file.get(fp)

        inter, slope = self.get_rescale_tags(fp)
        os.remove(fp)

        passed = bool(inter and slope)
        if passed:
            data = (str(inter.tag), str(slope.tag))

        return Results(passed, data=data)


class HasRescaleParametersInScans(ExperimentTest):
    """DICOM rescaling parameters specify the linear transformation from pixels
    in their stored representation to their intensity values for proper data
    usage. This test passes if all imaging session scans have rescale parameters
    available in the DICOM metainformation headers. Fails otherwise."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00013',

    def run(self, experiment_id):
        passed = True
        failed = []
        data = {}

        columns = ['xnat:imageScanData/type', 'xnat:imageScanData/quality']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=columns).data
        # filter out unsuitable scan_data items
        valid_scans = {str(s['xnat:imagescandata/id']): s for s in scans
                       if __is_valid_scan__(self.xnat_instance, s)}

        if not valid_scans:
            return Results(False, data=['No valid scans found.'])

        for scan_id in valid_scans.keys():
            r = HasRescaleParameters(self.lut, self.xnat_instance)\
                .run(experiment_id, scan_id)
            if not r.has_passed:
                passed = False
                failed.append(scan_id)
            else:
                data[scan_id] = r.data

        if not passed:
            data = failed

        return Results(passed, data=data)

    def report(self):
        report = []
        if not self.results.has_passed:
            report.append('Scans without rescale parameters: {}<br>'
                          .format(', '.join([str(s) for s in self.results.data])))
        else:
            rescale_tuples = set(self.results.data.values())
            for t in rescale_tuples:
                report_str = 'Intercept: {}, Slope: {}'.format(t[0], t[1])
                if len(rescale_tuples) > 1:
                    report_str += ' (scans: {})<br>'.format(', '.join(
                        [str(k) for k, v in self.results.data.items() if v == t]))
                report.append(report_str)

        return report


class HasBvecBval(ScanTest):
    """Diffusion-weighted datasets should have a BVEC and a BVAL pair of files
    generated by the conversion to NIfTI. Test passes if the dataset has such
    files with non-empty BVEC and BVAL values. Fails otherwise."""

    passing = 'BBRCDEV_E00014', '1501'
    failing = 'BBRCDEV_E00015', '1301'

    def get_bvec_bval_data(self, uris):
        """Helper that given a set or URIs of bvev,bval files return diffusion
        BVEC and BVAL files content as numpy n-dimensional array types."""

        import re
        import numpy as np

        bvecbval_data = {}
        for k, v in uris.items():
            content = self.xnat_instance.get(v).text
            # parse tab-separated string items as a list
            str_matrix = [re.split(r'\s+', s.rstrip(r'\s'))
                          for s in content.splitlines()]
            # convert into a numpy array
            ndarray_item = np.asarray(str_matrix)
            # cast numpy array values into floats (from string)
            ndarray_item = ndarray_item.astype(float)

            bvecbval_data[k] = ndarray_item

        return bvecbval_data

    def run(self, experiment_id, scan_id):
        import os.path as op

        resource_label = 'NIFTI'
        valid_extensions = ['.bvec', '.bval']
        data = None

        # pick a threshold based on observation to determine whether a
        # bvec/bval file size (Bytes) represents a valid file
        bvecbval_min_filesize = 50

        # get resources' files info for given scan
        uri = '/data/experiments/%s/scans/%s/resources/%s/files' % \
              (experiment_id, scan_id, resource_label)
        files_list = self.xnat_instance._get_json(uri)

        # exclude from valid BVEC/BVAL file candidates those without
        # a proper extension AND smaller than 50Byte size
        bvecbval_files_info = {op.splitext(current['Name'])[1]: current['URI']
                               for current in files_list
                               if op.splitext(current['Name'])[1] in valid_extensions
                               and int(current['Size']) > bvecbval_min_filesize}

        # check that the number of vectors in bvec file match the values in bval
        try:
            bvec_bval_content = self.get_bvec_bval_data(bvecbval_files_info)
        except ValueError as e:
            import logging as log
            log.error('%s' % e)
            data = ['Exception: %s' % e]
            bvec_bval_content = {}
        sizes = [item.shape[1] for item in bvec_bval_content.values()]

        # list should contain exactly a pair of file items (bvec and bval)
        res = len(bvecbval_files_info) == 2 and len(set(sizes)) == 1 and \
            set(valid_extensions).issubset(set(bvecbval_files_info.keys()))
        return Results(res, data=data)


class HasBvecBvalInDWIScans(ExperimentTest):
    """Diffusion-weighted datasets should have a BVEC and a BVAL pair of files
    generated by the conversion to NIfTI. Test passes if the dataset has such
    files with non-empty BVEC and BVAL values or simply no DWI/DTI scans included.
    Fails otherwise."""

    passing = 'BBRCDEV_E00014',
    failing = 'BBRCDEV_E00007',

    def run(self, experiment_id):
        dwi_scan_labels = self.lut.get('DWI', [])

        failed = []
        exp_res = True
        cols = ['ID', 'xsiType', 'project',
                'xnat:imageScanData/type',
                'xnat:imageScanData/quality']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=cols).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}
        # filter out unsuitable scan_data items
        valid_scans = {
            str(scan_id): scan_data for scan_id, scan_data in scans.items()
            if __is_valid_scan__(self.xnat_instance, scan_data)
            and scan_data['xnat:imagescandata/type'].strip() in dwi_scan_labels}

        for e in valid_scans:
            res = HasBvecBval(self.lut, self.xnat_instance).run(experiment_id, e)
            if not res.has_passed:
                exp_res = False
                failed.append(e)

        return Results(exp_res, data={'failed': failed, 'dwi': valid_scans})

    def report(self):
        report = []
        if not self.results.has_passed:
            report.append('DWI scans without BVEC/BVAL: %s<br>' %
                          ', '.join([str(e) for e in self.results.data['failed']]))

        report.append('Found DWI scans: %s' %
                      ', '.join([str(e) for e in self.results.data['dwi']]))
        return report


class IsStudyDescriptionCorrect(ExperimentTest):
    """Every scan should have its Study Description field matching the project's
    ID. This test passes only if all scans match the project's name.
    Fails otherwise."""

    passing = 'BBRCDEV_E00014',
    failing = 'BBRCDEV_E00381',

    def aliases(self, project):
        uri = '/data/projects'
        options = {'columns': 'alias', 'format': 'csv'}
        data = self.xnat_instance.get(uri, params=options).text
        from pyxnat.core.jsonutil import csv_to_json
        data = csv_to_json(str(data))

        # parse the results
        return [item['alias'] for item in data
                if item['alias'] and item['ID'] == project]

    def run(self, experiment_id):
        cols = ['xnat:imageSessionData/project',
                'xnat:imageSessionData/session_type']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=cols).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}

        failed = []
        for k, v in scans.items():
            project = str(v['session_project'])
            session_type = v['session_type']
            if project != session_type:
                # attempt to check if StudyDescription matches a project alias
                aliases = self.aliases(project)
                if not aliases or session_type not in aliases:
                    failed.append(session_type)

        res = len(failed) == 0
        return Results(res, data=list(set(failed)))

    def report(self):
        report = []
        if self.results.data:
            report.append('Incorrect ExamName found: %s' % ', '.join(self.results.data))
        return report


class HasCorrectSequences(ExperimentTest):
    """Every protocol has a given list of sequences with specific number of
    frames per sequence. This check includes a series of controls (see
    `xnat-monitor`). Fails if a major sequence is missing or has a wrong number
    of frames. Passes if the major sequences are present with the right number
    of frames. Returns a summary of the performed controls."""

    passing = 'BBRCDEV_E00380',
    failing = 'BBRCDEV_E00381',

    def run(self, experiment_id):

        def resolve_aliases(seq_list, aliases, logs=[]):
            new_list = []
            transtab = {}
            for e in seq_list:
                has_alias = False
                for k, v in aliases.items():
                    if e in v:
                        new_list.append(k)
                        logs.append('%s is found as %s<br>' % (k, e))
                        transtab[k] = e
                        has_alias = True
                if not has_alias:
                    new_list.append(e)
                    transtab[e] = e
            return new_list, transtab

        def resolve_mutexes(seq_list, obligatory_items, mutexes, logs=[]):

            for s in set(seq_list):
                for mutex_item1, mutex_item2 in mutexes.items():
                    if s == mutex_item1:
                        obligatory_items.pop(mutex_item2)
                        logs.append('{} is mutually exclusive with '
                                    '{}<br>'.format(mutex_item2, s))
                    elif s == mutex_item2:
                        obligatory_items.pop(mutex_item1)
                        logs.append('{} is mutually exclusive with '
                                    '{}<br>'.format(mutex_item1, s))

            return obligatory_items

        import json
        import bbrc
        import pandas as pd
        import os.path as op
        import logging as log

        fp = op.join(op.dirname(bbrc.__file__), 'data', 'validation_rules.json')
        with open(fp, 'r') as f:
            rules = json.load(f)

        e = self.xnat_instance.select.experiment(experiment_id)
        project_id = e.attrs.get('project')
        # Ad-hoc exception added for DEVELOPMENT ENVIRONMENT test cases validation
        if project_id == 'testenv' and 'devxnat' in self.xnat_instance._server:
            columns = ['ID', 'xnat:imagesessiondata/session_type']
            scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                                   columns=columns).data
            scans = {s['xnat:imagescandata/id']: s for s in scans}
            project_id = list(scans.items())[0][1]['session_type']
            project_id = project_id.replace('+', '_PLUS')

        log.info('*** %s' % project_id)

        # Sequences part
        seqdata = []
        cols = ['xnat:imageScanData/type', 'xnat:imageScanData/frames']
        d = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                           columns=cols).data
        d = {s['xnat:imagescandata/id']: s for s in d}

        for scan_id, scan in d.items():
            row = [experiment_id]
            keys = ['xnat:imagescandata/id',
                    'xnat:imagescandata/type',
                    'xnat:imagescandata/frames']
            for k in keys:
                row.append(scan[k].rstrip(' '))  # Remove strange trailing spaces

            scan = e.scan(scan_id)
            uri = scan._uri + '/resources'
            sc = {e['xnat_abstractresource_id']: e
                  for e in self.xnat_instance._get_json(uri)}
            dcm_resources = {each['content']: each
                             for each in sc.values()
                             if each['format'] == 'DICOM'}
            if len(dcm_resources) == 1:
                row.append(list(dcm_resources.values())[0]['file_count'])
                seqdata.append(row)
            elif len(dcm_resources) == 2 and 'RAW' in dcm_resources.keys():
                row.append(dcm_resources['RAW']['file_count'])
                seqdata.append(row)

        result = 0  # 0:OK, 1:Warning, 2:Error
        logs = []
        cols = ['xnatId', 'ID', 'type', 'frames', 'file_count']
        df = pd.DataFrame(seqdata, columns=cols)

        # Checks emptiness before starting anything
        headers = ['ID', 'type', 'frames', 'file_count']
        df2 = df[df['xnatId'] == experiment_id][headers]
        session_seqlist = df2['type'].tolist()  # List of session sequences

        if df2.empty:
            logs.append('%s scan data not found' % experiment_id)
            return Results(False, data=['Scan data not found'])

        # Dropping mock sequences: could probably use utils.__is_valid_scan__
        for index, row in df2.iterrows():
            if row['ID'].startswith('0-') or 'OT' in row['ID']:
                logs.append('Ignoring sequence %s<br>' % row['ID'])
                session_seqlist.remove(row['type'])
                df2.drop(index, inplace=True)

        # If the project does not have predefined rules, set default (empty) rules
        pr = rules.get(project_id, {'obligatory': {},
                                    'aliases': {},
                                    'mutually_exclusive': {},
                                    'warning_if_missing': {},
                                    'silently_identified': {}})
        if project_id not in rules:
            msg = 'No found validation results for %s.' % project_id
            log.error(msg)
            return Results(None, data=[msg])

        # Resolving aliases, transtab is a translation table
        session_seqlist, trans_table = resolve_aliases(session_seqlist,
                                                       pr['aliases'],
                                                       logs)

        # Resolving mutually exclusive sequence items
        pr['obligatory'] = resolve_mutexes(session_seqlist, pr['obligatory'],
                                           pr['mutually_exclusive'], logs)
        # Checking obligatory sequences
        for k, v in pr['obligatory'].items():
            if session_seqlist.count(k) < 1:
                continue

            key = 'file_count'
            if k in trans_table and 'CHESS' not in trans_table[k]:
                key = 'frames'

            n_frames = df2[df2['type'] == trans_table[k]][key].to_list()
            if session_seqlist.count(k) == 1:
                if n_frames[0] != str(v):
                    msg = '*** %s is unique but has wrong file_count '\
                        '(%s instead of %s) ***<br>' % (k, n_frames, v)
                    logs.append(msg)
                    result = 2
            if session_seqlist.count(k) > 1:
                occ = df2[df2['type'] == trans_table[k]]['ID'].tolist()
                for i, s in enumerate(occ):
                    if n_frames[i] != str(v):
                        msg = '*** %s (scanID: %s) has wrong file_count (%s ' \
                              'instead of %s) ***<br>' % (k, s, n_frames[i], v)
                        logs.append(msg)
                        result = 2
                logs.append('%s multiple occurrences (%s)<br>' % (k, occ))
                result = max(result, 1)

        logs.append('<br> ===== Missing ========<br>')
        for k, v in pr['obligatory'].items():
            if k not in session_seqlist:
                logs.append('*** %s is obligatory and missing ***<br>' % k)
                result = max(result, 2)
        for k in pr['warning_if_missing']:
            if k not in session_seqlist:
                logs.append('%s missing<br>' % k)
                result = max(result, 1)

        logs.append('<br> ========= Not identified ==========<br>')

        seq = list(pr['obligatory'].keys())
        seq.extend(pr['warning_if_missing'])
        seq.extend(pr['silently_identified'])
        for k, v in pr['aliases'].items():
            seq.extend(v)
        for each in set(session_seqlist).difference(seq):
            logs.append('%s not identified<br>' % each)

        logs.append('<br> ========= Silently identified ==========<br>')
        for each in session_seqlist:
            if each in pr['silently_identified']:
                logs.append('%s silently identified<br>' % each)

        res = result != 2
        return Results(res, data=logs)


class HasCorrectSequenceAttributes(ExperimentTest):
    """Every relevant scanning protocol has a set of DICOM metadata attributes
    describing -among other things- the acquisition protocol parameters used and
    the imaging data itself. This check validates a subset of DICOM attributes
    against predefined accepted values for each relevant scanning sequence in
    the dataset. Fails if any relevant sequence has an unexpected value for a
    DICOM metadata attributes. Passes if all the sequence-specific DICOM metadata
    attributes are present and with tolerable values."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00007',

    def run(self, experiment_id):

        import json
        import bbrc
        import os.path as op
        import logging as log
        import numpy as np

        alfa_protocols = ['B0_ALFA1', 'T1_ALFA1', 'T2_ALFA1', 'FLAIR_ALFA1',
                          'DWI_ALFA1', 'RS_ALFA1_SENSE']
        protocol_attributes = {}
        for seq in alfa_protocols:
            fp = op.join(op.dirname(bbrc.__file__), 'data',
                         'protocol_validation', '%s.json' % seq)
            with open(fp, 'r') as f:
                protocol_attributes[seq] = json.load(f)

        cols = ['ID', 'xsiType', 'xnat:imageSessionData/project',
                'xnat:imageScanData/type', 'xnat:imageScanData/quality']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=cols).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}
        project_id = str(list(scans.items())[0][1]['session_project'])

        matched_scans = {}
        for sid, sdata in scans.items():
            stype = str(sdata['xnat:imagescandata/type']).\
                strip().replace(" ", "_")
            dtype = self.xnat_instance.select.\
                experiment(experiment_id).scan(sid).datatype()

            if stype in protocol_attributes.keys() \
                    and not str(sid).startswith('0') \
                    and sdata['xnat:imagescandata/quality'] == 'usable' \
                    and dtype == 'xnat:mrScanData':
                matched_scans[str(sid)] = stype

        if not matched_scans:
            msg = 'Session %s (%s) has no scans matching any of the ' \
                  'relevant scanning protocols' % (experiment_id, project_id)
            log.warning(msg)
            return Results(False, data='Unknown scanning protocols')

        validation_data = {}
        for scan_id in matched_scans:
            uri = '/REST/services/dicomdump'
            options = {
                'format': 'csv',
                'src': '/archive/projects/%s/experiments/%s/scans/%s' %
                       (project_id, experiment_id, scan_id),
                'field': ['00189087', '00200105', '00081090', '00080008',
                          '0008103E', '00080070', '00181020', '00181000',
                          '00180015', '00180023', '00180050', '00180080',
                          '00180081', '00180083', '00180087', '00180088',
                          '00180089', '00180095', '00181310', '00181312',
                          '00181314', '00185100', '00189073', '00280010',
                          '00280011', '00280030']
            }

            from pyxnat.core.jsonutil import csv_to_json
            dicomdump = csv_to_json(
                str(self.xnat_instance.get(uri, params=options).text))

            dicom_attributes = {
                str(item['desc']).replace(" ", "").replace("&rsquo;s", "s"):
                str(item['value']) for item in dicomdump}

            scan_validation_results = {}
            for tag, value in protocol_attributes[matched_scans[scan_id]].items():
                result = False
                if tag in dicom_attributes.keys():
                    if isinstance(value, str):
                        if tag == 'SeriesDescription':
                            # exception: In some cases SeriesDescription value
                            # should be preprocessed to match the protocol name
                            result = bool(value == dicom_attributes[tag].
                                          strip().replace(" ", "_"))
                        else:
                            result = bool(value == dicom_attributes[tag])
                    elif isinstance(value, int):
                        # exception: PixelBandwith diverges greatly at T1W,RS,
                        # ... Tolerance factor of +/- 1%
                        if tag == 'PixelBandwidth':
                            import math
                            tolerance = int(math.ceil(0.01 * value))
                            result = bool(np.isclose(int(dicom_attributes[tag]),
                                                     value, atol=tolerance))
                        else:
                            result = bool(int(dicom_attributes[tag]) == value)
                    elif isinstance(value, float):
                        # exception: RepetitionTime diverges frequently.
                        # Tolerance factor of +/- 1 (absolute)
                        if tag == 'RepetitionTime':
                            result = bool(np.isclose(float(dicom_attributes[tag]),
                                                     value, atol=1))
                        # exception: AcquisitionDuration diverges (particularly
                        # in FLAIR!). Tolerance factor of +/- 5 (absolute)
                        elif tag == 'AcquisitionDuration':
                            result = bool(np.isclose(float(dicom_attributes[tag]),
                                                     value, atol=5))
                        else:
                            # note: tolerance added for the float typed
                            # values of +/- 0.05 (absolute)
                            result = bool(np.isclose(float(dicom_attributes[tag]),
                                                     value, atol=0.05))
                    elif isinstance(value, list):
                        # exception: Diffusion b-value for DWI scans can have
                        # several values (depending on the current slice/file)
                        if tag == 'Diffusionb-value':
                            result = round(float(dicom_attributes[tag]),
                                           3) in value
                        # exception: PixelSpacing values diverge slightly (+/- 0.001)
                        elif tag == 'PixelSpacing':
                            result = all(np.isclose(
                                np.asarray(
                                    dicom_attributes[tag].split('\\')).astype(np.float),
                                np.asarray(value).astype(np.float),
                                atol=0.001))
                        # exception: SoftwareVersions can either be 5.1.9 or 5.4.0
                        elif tag == 'SoftwareVersion(s)':
                            result = bool(dicom_attributes[tag].split('\\') in value)
                        else:
                            result = bool(dicom_attributes[tag].split('\\') == value)
                else:
                    log.error('Scan %s (%s) has no %s DICOM tag' %
                              (scan_id, experiment_id, tag))

                scan_validation_results[tag] = result

            # Populate useful resulting data if Test failed
            if not all(scan_validation_results.values()):
                for k, v in scan_validation_results.items():
                    if not v:
                        if k in dicom_attributes.keys():
                            validation_data[scan_id] = (k, dicom_attributes[k])
                        else:
                            validation_data[scan_id] = (k, "DICOM tag not found")

        validation_result = bool(len(validation_data) == 0)
        return Results(validation_result, data=validation_data)

    def report(self):
        report = []
        if not self.results.has_passed:
            if isinstance(self.results.data, dict):
                report.append('Relevant scans with invalid DICOM attributes:<br>')
                report.append('<br>'.join(['%s: %s (%s)' % (k, v[0], v[1])
                                           for k, v in self.results.data.items()]))
            else:
                report.append(self.results.data)

        return report


class HasUsableT1(ExperimentTest):
    """This test determines if session has a usable T1-weighted (`T1`) scan
    suited for further processing. This test passes either if there is
    one unique and valid sequence labelled as T1 or if, in case of multiple
    matches, only one of them is labelled as `usable`. Fails otherwise."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00483',

    def run(self, experiment_id):
        t1w_scan_labels = self.lut.get('T1', [])

        cols = ['xnat:mrScanData/type',
                'xnat:mrScanData/quality',
                'xnat:mrScanData/frames']
        scans = self.xnat_instance.array.mrscans(experiment_id=experiment_id,
                                                 columns=cols).data
        scans = {s['xnat:mrscandata/id']: s for s in scans}

        # filter out unsuitable scan_data items
        valid_t1w_scans = {
            str(scan_id): scan_data for scan_id, scan_data in scans.items()
            if __is_valid_scan__(self.xnat_instance, scan_data)
            and scan_data['xnat:mrscandata/type'].strip() in t1w_scan_labels}

        if not valid_t1w_scans:
            return Results(False, data=['No valid T1 scans found.'])

        pref = HasPreferredT1(self.lut, self.xnat_instance).run(experiment_id)
        if not pref.has_passed:
            msg = 'Multiple T1 scans but unable to determine a preferred one.'
            return Results(False, data=[msg])

        scan_id = list(pref.data)[0]

        # built-in checks
        required = [HasNifti, HasUncompressedPixelData, IsClassicDICOM]

        for each in required:
            c = each(self.lut, self.xnat_instance).run(experiment_id, scan_id)
            if not c.has_passed:
                msg = 'Test %s failed.' % each.__name__
                return Results(False, data=[msg])

        return Results(True, data=[scan_id])

    def report(self):
        if self.results.has_passed:
            report = ['Usable T1: %s' % list(self.results.data)[0]]
        else:
            report = [list(self.results.data)[0]]
        return report


class HasPreferredT1(ExperimentTest):
    """Sessions may have multiple versions of T1 images (captured by
    HasDuplicatedSequence). In those cases, and in order to identify which one
    may have the best quality and be selected for further processing, it is
    possible to rely on the possibly associated reconstructions along other axes
    e.g. AXIAL and CORONAL). It is assumed that reconstructed versions are
    generated for the preferred version of the T1 scan only.
    This test passes either if there is one unique and valid T1 sequence or if,
    in case of multiple matches, only one of them has suitable associated
    reconstructions. Note that in those cases, the Test will proactively label
    all scans without reconstructions as `questionable`, excluding them for any
    processing stage (corrective measure)."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00483',

    def valid_t1w_scans(self, experiment_id):
        """Returns a dictionary of 'valid' T1 scans for a given experiment_id."""
        t1w_scan_labels = self.lut.get('T1', [])

        options = ['xnat:imagescandata/quality', 'xnat:imagescandata/frames',
                   'xsiType', 'xnat:imagescandata/type']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=options).data
        valid_t1w_scans = {
            str(scan['xnat:imagescandata/id']): scan for scan in scans
            if __is_valid_scan__(self.xnat_instance, scan)
            and scan['xnat:imagescandata/type'].strip() in t1w_scan_labels
        }
        return valid_t1w_scans

    def reconstructed_scans(self, experiment_id, scan_id):
        """Given an experiment_id and a scan_id, returns a set of existing
        matching scan IDs."""

        options = ['xnat:imagescandata/quality', 'xnat:imagescandata/frames',
                   'xsiType', 'xnat:imagescandata/type']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=options).data
        series = [scan for scan in scans
                  if len(scan['xnat:imagescandata/id']) == len(scan_id)
                  and scan['xnat:imagescandata/id'][:-1] == scan_id[:-1]]
        return series

    def has_reconstructed_scans(self, scans):
        """Given a set of scan IDs, returns a boolean if these refer to a
        collection of reconstructed scans."""

        seq = {}
        for each in ['alfa1', 'coronal', 'axial']:
            seq[each] = []
            for v in scans:
                if each in v['xnat:imagescandata/type'].lower():
                    seq[each].append(v['ID'])
        return len(seq['alfa1']) * len(seq['coronal']) * len(seq['axial']) == 1

    def set_scan_quality_label(self, experiment_id, scan_id, label):
        """Set the quality label for a given experiment/scan."""

        import logging as log
        assert(label in ['usable', 'questionable', 'unusable'])
        uri = 'data/experiments/%s/scans/%s' % (experiment_id, scan_id)

        data = {'xsiType': 'xnat:mrScanData',
                'xnat:mrscandata/quality': label}
        r = self.xnat_instance.put(uri, data=data)
        log.warning('Setting scan %s (%s) quality to `%s`.' % (scan_id,
                                                               experiment_id,
                                                               label))
        return r

    def __is_reconstructed__(self, experiment_id):
        valid_t1w_scans = self.valid_t1w_scans(experiment_id)
        is_reconstructed = {}
        for scan_id in valid_t1w_scans.keys():
            reconstructed = self.reconstructed_scans(experiment_id, scan_id)
            is_reconstructed[scan_id] = self.has_reconstructed_scans(reconstructed)

        return is_reconstructed

    def preferred_t1(self, experiment_id):
        """Returns the scan_id of the preferred T1 given an experiment_id."""

        valid_t1w_scans = self.valid_t1w_scans(experiment_id)

        if not valid_t1w_scans:
            return None
        elif len(valid_t1w_scans.keys()) == 1:
            return list(valid_t1w_scans.keys())[0]

        is_reconstructed = self.__is_reconstructed__(experiment_id)
        has_unique = list(is_reconstructed.values()).count(True) == 1
        if has_unique:
            return list(is_reconstructed.keys())[0]
        else:
            return None

    def run(self, experiment_id):
        valid_t1w_scans = self.valid_t1w_scans(experiment_id)

        if not valid_t1w_scans:
            return Results(False, data=['No valid T1 scans found.'])
        elif len(valid_t1w_scans.keys()) == 1:
            return Results(True, data=list(valid_t1w_scans.keys()))

        is_reconstructed = self.__is_reconstructed__(experiment_id)
        has_unique = list(is_reconstructed.values()).count(True) == 1

        reconstructed = [e for e, v in is_reconstructed.items()
                         if v is True]
        not_reconstructed = [e for e, v in is_reconstructed.items()
                             if v is False]

        preferred = self.preferred_t1(experiment_id)

        if preferred is not None:
            # apply corrective measure!
            for scan in not_reconstructed:
                self.set_scan_quality_label(experiment_id, scan, 'questionable')

        return Results(has_unique, data=reconstructed)

    def report(self):
        if self.results.has_passed:
            report = ['Preferred T1: %s' % list(self.results.data)[0]]
        else:
            if not self.results.data:
                report = ['No T1 scans found with reconstructed versions']
            else:
                reconstructed = list(self.results.data)[0]
                if not isinstance(reconstructed, str):
                    report = ['Following T1 scans were found with reconstructed '
                              'versions: %s' % ', '.join(reconstructed)]
                else:
                    report = [list(self.results.data)[0]]
        return report


class IsFreeSurferRunnable(ExperimentTest):
    """This test validates that the given MRSession fulfills the requirements
    for running FreeSurfer. Fails if no MRSession scans are suited for running
    FreeSurfer (see result/report data); passes otherwise."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00483',
    tests = [HasUsableT1]

    def run(self, experiment_id):

        for test in self.tests:
            res = test(self.lut, self.xnat_instance).run(experiment_id)
            if not res.has_passed:
                return Results(False, data=['%s failed: %s Not runnable.'
                                            % (test.__name__, res.data[0])])

        return Results(True, data=[])


class IsPhilipsVersion519(ExperimentTest):
    """The scanner software version used for generating an MRI dataset is
    registered in the DICOM metaheader as `SoftwareVersion(s)`. This test passes
    if an MRI Session was acquired using version 5.1.9 of the manufacturers
    software. Fails otherwise. If no SoftwareVersion(s) attribute is found in
    the DICOM metaheader, the test is skipped."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00401',
    mri_philips_version = '5.1.9'

    def run(self, experiment_id):
        cols = ['ID', 'label', 'project', 'subject_ID']
        labels = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                      columns=cols).data[0]
        project = str(labels['project'])

        uri = '/REST/services/dicomdump'
        options = {
            'format': 'csv',
            'src': '/archive/projects/%s/experiments/%s' % (project, experiment_id),
            'field': '00181020'
        }
        from pyxnat.core.jsonutil import csv_to_json
        tag = csv_to_json(str(self.xnat_instance.get(uri, params=options).text))
        if not tag:
            return Results(None, ['Software Versions (0018,1020) tag is not present'])
        tag_value = str(tag[0]['value']).split('\\')

        result = False
        data = ['Unexpected version: %s' % tag_value]
        if tag_value[0] == self.mri_philips_version:
            result = True
            data = []
        return Results(result, data)


class IsPhilipsVersion540(IsPhilipsVersion519):
    __doc__ = IsPhilipsVersion519.__doc__
    __doc__ = __doc__.replace('5.1.9', '5.4.0')

    passing = 'BBRCDEV_E00401',
    failing = 'BBRCDEV_E00272',
    mri_philips_version = '5.4.0'


class IsPhilipsVersion561(IsPhilipsVersion519):
    __doc__ = IsPhilipsVersion519.__doc__
    __doc__ = __doc__.replace('5.1.9', '5.6.1')

    passing = 'BBRCDEV_E02949',
    failing = 'BBRCDEV_E00401',
    mri_philips_version = '5.6.1'


class IsAccessionNumberUnique(ExperimentTest):
    """The AccessionNumber (AN) is a supposedly unique code that contains project,
    session/visit and study date information. This test passes if an MRI Session
    has its AN consistently unique across the current XNAT instance. Fails
    otherwise. If the MRI Session project is in the excluded projects list, the
    test is skipped."""

    passing = 'BBRCDEV_E00403',
    failing = 'BBRCDEV_E00405',

    def get_all_projects(self, connection):
        """Query XNAT REST interface for full project list. Returns a dict of
        project IDs and metainformation"""

        # compose the URL for the REST call
        uri = '/data/projects?accessible=true'

        # do the HTTP query
        projects = connection._get_json(uri)

        # parse the results
        project_dict = {}
        for project in projects:
            project_dict[project['id']] = project

        return project_dict

    def run(self, experiment_id):
        # Exclude testing/external projects which are not relevant
        excluded_projects = ['UCLM', 'HUGM', 'UPF_IR', 'PHILIPS', 'TEST_MRI',
                             'VOLUNTARIOS', 'jh_sandbox', 'GE-AIBL', 'BLSA']
        all_projects = self.get_all_projects(self.xnat_instance).keys()
        projects = [e for e in all_projects
                    if e not in excluded_projects
                    and not e.startswith('_')]

        cols = ['ID', 'label', 'project', 'subject_ID']
        labels = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                      columns=cols).data[0]

        project_id = str(labels['project'])
        session_label = str(labels['label'])

        # XNAT does not allow having distinct experiments with same label in a
        # contiguous Project container exclude current project from the list of
        # projects to check for
        if project_id not in projects:
            msg = 'Project excluded for AccessionNumber consistency checks.'
            return Results(None, data=[msg])
        else:
            projects.remove(project_id)

        matchings = {}
        for project in projects:
            seslist = self.xnat_instance.array.experiments(project_id=project,
                                                           columns=cols).data
            pmatches = [e['ID'] for e in seslist
                        if str(session_label) == e['label']]
            if pmatches:
                matchings[project] = pmatches[0]

        data = []
        if matchings:
            msg = 'AccessionNumber (%s) is not unique, matchings: %s'\
                  % (session_label, matchings)
            data = [msg]

        return Results(bool(len(data) == 0), data)


class HasValidAccessionNumber(ExperimentTest):
    """This test passes if an MRI Session AccessionNumber (AN) can be parsed and
    its project, session/visit and date information is valid and consistent.
    Fails otherwise. If the MRI Session project is in the excluded projects
    list, the test is skipped."""

    passing = 'BBRCDEV_E00403',
    failing = 'BBRCDEV_E00404',

    def parse_accession_number(self, an_code):

        if len(an_code) == 15:
            p_code = an_code[0:2]
            v_code = an_code[2:4]
            subject = an_code[4:6] + an_code[12:15]
            date = an_code[6:12]
        elif len(an_code) == 16:
            p_code = an_code[0:2]
            v_code = an_code[2:5]
            subject = an_code[5:7] + an_code[13:16]
            date = an_code[7:13]
        else:
            return None

        return p_code, v_code, subject, date

    def run(self, experiment_id):

        import json
        import bbrc
        import os.path as op
        from datetime import datetime as dt

        fp = op.join(op.dirname(bbrc.__file__), 'data', 'an_codes.json')
        with open(fp, 'r') as f:
            codes = json.load(f)
        cols = ['ID', 'label', 'project', 'subject_ID', 'subject_label']
        labels = self.xnat_instance.array.experiments(experiment_id=experiment_id,
                                                      columns=cols).data[0]

        session_id = str(labels['label'])
        subject_label = str(labels['subject_label'])
        project_id = str(labels['project'])
        # Handle name exception for ALFA_PLUS study sub-projects
        if project_id.startswith('ALFA_PLUS'):
            project_id = 'ALFA_PLUS'

        parsed = self.parse_accession_number(session_id)
        if not parsed:
            msg = 'AccessionNumber %s cannot be parsed' % session_id
            return Results(False, data=[msg])
        pr_code, vi_code, subject, date = parsed

        # A) check if project & visit prefix codes are CORRECT
        if pr_code not in codes.keys():
            msg = 'Invalid AccessionNumber prefix ' \
                  '(project code \'%s\')' % pr_code
            return Results(False, data=[msg])
        else:
            if codes[pr_code]['project'] != project_id:
                msg = 'Project code (%s) not matching current project' \
                      % codes[pr_code]['project']
                return Results(False, data=[msg])
            else:
                if vi_code not in codes[pr_code]['visit_codes'].keys():
                    msg = 'Invalid AccessionNumber prefix ' \
                          '(visit code \'%s\')' % vi_code
                    return Results(False, data=[msg])

        # B) check if date code is CORRECT
        cols = ['ID', 'label', 'date']
        session_data = self.xnat_instance.array.experiments(project_id=str(labels['project']),
                                                            columns=cols).data
        session_data = {e['ID']: e for e in session_data}
        session_date = dt.strptime(session_data[experiment_id]['date'],
                                   '%Y-%m-%d')
        try:
            an_date = dt.strptime(date, '%d%m%y')
        except ValueError:
            return Results(False, data=['Invalid AccessionNumber prefix '
                                        '(date \'%s\')' % date])

        if an_date != session_date:
            return Results(False, data=['Date (%s) not matching current '
                                        'acquisition date' % dt.date(an_date)])

        # C) check if subject is CORRECT
        if subject != subject_label:
            return Results(False, data=['Subject (%s) not matching current '
                                        'subject for %s' % (subject, session_id)])

        return Results(True, data=[])


class HasUsableDWI(ExperimentTest):
    """This test determines if session has a usable Diffusion-weighted (`DWI`)
    scan suited for further processing. This test passes either if there is
    one unique and valid DWI sequence or if, in case of multiple matches,
    only one of them is labelled as `usable`. Fails otherwise."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00007',
    scan_type = 'DWI'
    required_tests = [HasBvecBval, HasNifti, IsClassicDICOM,
                      HasPhilipsPrivateTags, HasUncompressedPixelData]

    def run(self, experiment_id):
        scan_labels = self.lut.get(self.scan_type, [])

        columns = ['xsiType',
                   'xnat:mrScanData/type',
                   'xnat:mrScanData/quality',
                   'xnat:mrScanData/frames']

        data = self.xnat_instance.array.mrscans(experiment_id=experiment_id,
                                                columns=columns).data
        scans = {s['xnat:mrscandata/id']: s for s in data}

        # filter out unsuitable scan_data items
        valid_scans = {
            str(scan_id): scan_data for scan_id, scan_data in scans.items()
            if __is_valid_scan__(self.xnat_instance, scan_data)
            and scan_data['xnat:mrscandata/type'].strip() in scan_labels}

        if not valid_scans:
            return Results(False,
                           data=['No valid %s scans found' % self.scan_type])
        elif len(valid_scans) > 1:
            return Results(False,
                           data=['Multiple %s scans.' % self.scan_type])

        scan_id = list(valid_scans.keys())[0]

        # built-in checks
        for each in self.required_tests:
            c = each(self.lut, self.xnat_instance).run(experiment_id, scan_id)
            if not c.has_passed:
                msg = 'Test %s failed.' % each.__name__
                return Results(False, data=[msg])

        return Results(True, data=[scan_id])

    def report(self):
        if self.results.has_passed:
            report = ['Usable %s: %s' % (self.scan_type,
                                         list(self.results.data)[0])]
        else:
            report = [list(self.results.data)[0]]
        return report


class HasUsableReversedDWI(HasUsableDWI):
    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00007',
    scan_type = 'rDWI'
    required_tests = [HasNifti, IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion',
                                           'reversed phase-encoding Diffusion')
    __doc__ = __doc__.replace('DWI', 'rDWI')


class IsDtifitRunnable(IsFreeSurferRunnable):
    """This test validates that the given MRSession fulfills the requirements
    for running FSL dtifit application. Fails if no MRSession scans are suited
    for running dtifit (see result/report data), passes otherwise."""

    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00007',
    tests = [HasUsableDWI, HasUsableReversedDWI]


class HasUsableT2(HasUsableDWI):
    passing = 'BBRCDEV_E00272',
    failing = 'BBRCDEV_E00007',
    scan_type = 'T2'
    required_tests = [HasNifti, IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion',
                                           'T2')
    __doc__ = __doc__.replace('DWI', 'T2')


class IsT2T1CoregistrationRunnable(IsFreeSurferRunnable):
    """This test validates that the given MRSession fulfills the requirements
    to run a multimodal pipeline for the coregistration of T2 scan image into T1
    image space. Fails if no MRSession scans are suited for running
    `T2T1Coregistraton` pipeline, passes otherwise."""

    passing = 'BBRCDEV_E01613',
    failing = 'BBRCDEV_E00385',
    tests = [HasUsableT1, HasUsableT2]


class HasUsableIR(HasUsableDWI):
    passing = 'BBRCDEV_E02443',
    failing = 'BBRCDEV_E00281',
    scan_type = 'IR'
    required_tests = [HasNifti, IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion-weighted',
                                           'Inversion Recovery')
    __doc__ = __doc__.replace('DWI', 'IR')


class IsASHSRunnable(IsFreeSurferRunnable):
    """This test validates that the given MRSession fulfills the requirements
    to run `ASHS`, a multimodal pipeline for the segmentation of hippocampal
    subfields that uses a T1w and a Inversion Recovery (IR) set of scan images.
    Fails if no MRSession scans are suited for running `ASHS` pipeline; passes
    otherwise."""

    passing = 'BBRCDEV_E02443',
    failing = 'BBRCDEV_E00007',
    tests = [HasUsableT1, HasUsableIR]


class HasValidDcm2niixVersion(ExperimentTest):
    """Image data is automatically converted to NIfTI format (from DICOM) once
    a session is archived into XNAT. Converting data to NIfTI eases the usage
    and further processing of the images. Tool `dcm2niix` is used to
    automatically convert (via pipeline) all imaging scans to NIfTI file format.
    This test checks if the conversion procedure registered the version of
    `dcm2niix` used in the logs. Test passes if version tag is found in the
    `DICOM2NIFTI` resource log files and if it matches the expected version,
    `v1.0.20180328`. Fails otherwise."""

    passing = 'BBRCDEV_E02832',
    failing = 'BBRCDEV_E00021',

    def run(self, experiment_id):
        baseline_version = 'v1.0.20180328 (OpenJPEG build) GCC4.8.4 (64-bit Linux)'
        has_passed = False
        data = []

        res = self.xnat_instance.select.experiment(experiment_id).\
            resource('DICOM2NIFTI')
        if not list(res.files('*.log')):
            msg = 'No log file found in resource `DICOM2NIFTI`.'
            return Results(False, data=[msg])

        log = list(res.files('*.log'))[0]
        log_content = self.xnat_instance.get(log.attributes()['URI']).text
        vlist = [line.split('dcm2niiX version', 1)[1].split('\\n', 1)[0].strip()
                 for line in log_content.splitlines()
                 if 'dcm2niiX version' in line]

        dcm2niix_version = list(set(vlist))
        has_passed = bool([baseline_version] == dcm2niix_version)
        if not dcm2niix_version:
            data = ['No `dcm2niix` version information found.']
        elif has_passed:
            data = dcm2niix_version
        else:
            data = ['Unexpected `dcm2niix` version: '
                    '{}'.format(dcm2niix_version[0])]

        return Results(has_passed, data)


class IsAcquisitionDateConsistent(ExperimentTest):
    """A session is composed of a set of scans (images) acquired at specific
    timepoints, usually (but not mandatorily) all on the same day. This test
    checks whether the date of an imaging session is consistent across its scans,
    comparing the session `date` attribute (XNAT) with the `AcquisitionDate`
    field from the headers of the first DICOM file in each scan. This test passes
    if dates match between session and scans. Fails otherwise."""

    passing = 'BBRCDEV_E02803',
    failing = 'BBRCDEV_E00745',

    def run(self, experiment_id):
        import dateparser
        data = dict()

        e = self.xnat_instance.select.experiment(experiment_id)
        session_date = e.attrs.get('date')
        data['session_date'] = session_date

        columns = ['xnat:imageScanData/type', 'xnat:imageScanData/quality']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=columns).data
        # filter out unsuitable scan_data items
        valid_scans = {str(s['xnat:imagescandata/id']): s for s in scans
                       if __is_valid_scan__(self.xnat_instance, s)}

        if not valid_scans:
            return Results(False, ['No valid scans found.'])

        wrong = dict()
        no_dicom = []
        for scan_id in valid_scans.keys():
            resource = self.xnat_instance.select.experiment(experiment_id).\
                scan(scan_id).resource('DICOM')
            if not resource.exists():
                no_dicom.append(scan_id)
                continue

            scan_date = str(dateparser.parse(resource.scandate()).date())
            if session_date != scan_date:
                wrong[scan_id] = scan_date

        if len(no_dicom) == len(valid_scans):
            return Results(False, ['No `DICOM` resources found.'])

        if wrong:
            has_passed = False
            for key, value in sorted(wrong.items()):
                data.setdefault(value, []).append(key)
        else:
            has_passed = True

        return Results(has_passed, data)

    def report(self):
        report = []

        if not self.results.has_passed:
            if isinstance(self.results.data, list):
                report = self.results.data
            elif isinstance(self.results.data, dict):
                sess_date = self.results.data.pop('session_date')
                report.append('Session date: {}; Conflicting scans: {}'
                              .format(sess_date, self.results.data))
        return report


class IsInsertDateConsistent(ExperimentTest):
    """Every time an imaging session is successfully archived, XNAT registers
    the completion of the archiving event with a timestamp (referred to as the
    session `insert date`). Such event includes the transfer, storage and
    sorting of received images. This test passes if two conditions are met:
    (a) `insert date` should be close enough (less than 3 hours) to the date of
    the `most recent modification` of each first DICOM file in all session scans
    (b) insert date should succeed all these last modification dates.
    Any modification date found posterior to the insert date would reflect
    improper intervention on the data. Fails if any of the two conditions above
    aren't fulfilled."""

    passing = 'BBRCDEV_E02803',
    failing = 'BBRCDEV_E00002',

    def datetime_tz_aware(self, dt, tz='Europe/Amsterdam'):
        import pytz

        tz_info = pytz.timezone(tz)
        return dt.astimezone(tz_info)

    def run(self, experiment_id):
        from datetime import timedelta
        import dateparser

        has_passed = False
        data = dict()

        e = self.xnat_instance.select.experiment(experiment_id)
        insert_date = e.attrs.get('insert_date')
        session_date = dateparser.parse(insert_date)
        data['session_date'] = session_date.strftime("%Y-%m-%d %H:%M")

        columns = ['xnat:imageScanData/type', 'xnat:imageScanData/quality']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=columns).data
        # filter out unsuitable scan_data items
        valid_scans = {str(s['xnat:imagescandata/id']): s for s in scans
                       if __is_valid_scan__(self.xnat_instance, s)}

        if not valid_scans:
            return Results(False, ['No valid scans found.'])

        wrong = dict()
        no_dicom = []
        for scan_id in valid_scans.keys():
            resource = self.xnat_instance.select.\
                experiment(experiment_id).scan(scan_id).resource('DICOM')
            if not resource.exists():
                no_dicom.append(scan_id)
                continue

            mod_date = dateparser.parse(resource.files()[0].last_modified())
            session_dt_tz = self.datetime_tz_aware(session_date)
            scan_dt_tz = self.datetime_tz_aware(mod_date)
            if scan_dt_tz > session_dt_tz \
                    and abs(session_dt_tz - scan_dt_tz) > timedelta(hours=3):
                wrong[scan_id] = mod_date.strftime("%Y-%m-%d %H:%M")

        if len(no_dicom) == len(valid_scans):
            return Results(False, ['No `DICOM` resources found.'])

        if wrong:
            has_passed = False
            for key, value in sorted(wrong.items()):
                data.setdefault(value, []).append(key)
        else:
            has_passed = True

        return Results(has_passed, data)

    def report(self):
        report = []

        if not self.results.has_passed:
            if isinstance(self.results.data, list):
                report = self.results.data
            elif isinstance(self.results.data, dict):
                insert_date = self.results.data.pop('session_date')
                report.append('Session insert date: {}; Modified scans files: '
                              '{}'.format(insert_date, self.results.data))
        return report


class HasUsableFLAIR(HasUsableDWI):
    passing = 'BBRCDEV_E02939',
    failing = 'BBRCDEV_E02872',
    scan_type = 'FLAIR'
    required_tests = [HasNifti, IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion-weighted',
                                           'Fluid-Attenuated Inversion Recovery')
    __doc__ = __doc__.replace('DWI', 'FLAIR')


class IsBAMOSRunnable(IsFreeSurferRunnable):
    """This test checks that a given MRSession fulfills the requirements to run
    `BAMOS` (Sudre et al., IEEE TMI, 2015), a multimodal pipeline for the
    segmentation of white matter lesions. `BAMOS` works with T1s and FLAIRs.
    This test passes if the right scans can be found, fails otherwise."""

    passing = 'BBRCDEV_E02939',
    failing = 'BBRCDEV_E02872',
    tests = [HasUsableT1, HasUsableFLAIR]


class HasUsableASL(HasUsableDWI):
    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00013',
    scan_type = 'ASL'
    required_tests = [HasNifti, IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion-weighted',
                                           '(pseudo-continuous) '
                                           'Arterial Spin Labeling')
    __doc__ = __doc__.replace('DWI', 'ASL')


class HasUsableM0(HasUsableDWI):
    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00013',
    scan_type = 'M0'
    required_tests = [HasNifti, IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion-weighted',
                                           'Equilibrium Magnetization')
    __doc__ = __doc__.replace('DWI', 'M0')


class IsBASILRunnable(IsFreeSurferRunnable):
    """This test checks that a given MRSession fulfills the requirements to run
    `BASIL` (_Bayesian Inference for Arterial Spin Labeling MRI_), a multimodal
    pipeline for the quantification of cerebral perfusion on ASL data. `BASIL`
    requires a T1 image, an ASL image and a M0 calibration image to run. This
    test passes if the right scan images can be found, fails otherwise."""

    passing = 'BBRCDEV_E00276',
    failing = 'BBRCDEV_E00013',
    tests = [HasUsableT1, HasUsableASL, HasUsableM0]


class HasUsableRS(HasUsableDWI):
    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E00013',
    scan_type = 'RS'
    required_tests = [IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion-weighted',
                                           'Resting State fMRI')
    __doc__ = __doc__.replace('DWI', 'RS-fMRI')


class HasUsableSEap(HasUsableDWI):
    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E00013',
    scan_type = 'SEap'
    required_tests = [IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion-weighted',
                                           'Spin-echo fMRI with AP '
                                           'phase-encoding')
    __doc__ = __doc__.replace('DWI', 'SE-fMRI-AP')


class HasUsableSEpa(HasUsableDWI):
    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E00013',
    scan_type = 'SEpa'
    required_tests = [IsClassicDICOM, HasUncompressedPixelData]
    __doc__ = HasUsableDWI.__doc__.replace('Diffusion-weighted',
                                           'Spin-echo fMRI with PA '
                                           'phase-encoding')
    __doc__ = __doc__.replace('DWI', 'SE-fMRI-PA')


class IsFMRIPrepRunnable(IsFreeSurferRunnable):
    """This test checks that a given MRSession fulfills the requirements to run
    `fMRIPrep`, a multimodal pipeline that prepares Resting State fMRI data for
    a variety of posterior analyses. `FMRIPREP` requires a T1w image, a Resting
    State fMRI image and a couple of Spin-echo scans with reversed phase-encoding
    polarity to run. This test passes if the right scan images can be found,
    fails otherwise."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E00013',
    tests = [HasUsableT1, HasUsableRS, HasUsableSEap, HasUsableSEpa]