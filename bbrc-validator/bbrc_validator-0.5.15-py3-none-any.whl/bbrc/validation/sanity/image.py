from ..test import ExperimentTest, Results
from ..utils import __is_valid_scan__


class T1wHasValidGrayscaleRange(ExperimentTest):
    """MR images include attributes for scaling (slope and offset/intercept)
    used to generate final image intensity values once applied to stored data
    values. This Test -mostly informative- focuses on `T1W` scans to evaluate
    the _normality_ of the scaling attributes and to collect data scaling
    attributes, stored data min./max. and the cardinality of represented
    grayscale levels. Test passes if `scaling slope` parameter value is set
    between 1 and 250. Fails otherwise."""

    passing = 'BBRCDEV_E00375',
    failing = 'BBRCDEV_E00272',

    def parse_image_stats(self, nii_file):
        import nibabel
        import logging

        try:
            img = nibabel.load(nii_file)
        except nibabel.nifti1.ImageFileError as img_err:
            logging.error('Error loading NIfTI image file: %s' % img_err)
            return None

        slope = img.dataobj.slope
        inter = img.dataobj.inter
        data = img.dataobj.get_unscaled()
        n_intensities = []
        for i in range(0, int(data.shape[0])):
            n_intensities.extend(set(list(data[i].flatten())))
            n_intensities = list(set(n_intensities))

        return [float(slope), float(inter), float(data.min()),
                float(data.max()), len(n_intensities)]

    def get_scan_nifti_info(self, experiment_id, scan_id):
        import os
        import os.path as op
        import tempfile
        import logging

        e = self.xnat_instance.select.experiment(experiment_id)
        is_resource = e.scan(scan_id).resource('NIFTI').exists()
        if not is_resource:
            logging.error('Scan not available in NIFTI format (%s:%s). '
                          'Skipping.' % (experiment_id, scan_id))
            return None

        scan = self.xnat_instance.select.experiment(experiment_id).scan(scan_id)
        uri = scan._uri + '/resources/NIFTI/files'
        files = self.xnat_instance._get_json(uri)
        if len(files) < 1:
            logging.error('No NIFTI files found (%s:%s).Skipping.'
                          % (experiment_id, scan_id))
            return None

        # filter out if JSON sidecar is present due to Dicom To Nifti conversion settings!
        nifti_files = [v for v in files
                       if op.splitext(v['Name'])[1] in ['.nii', '.gz']]

        if len(nifti_files) != 1:
            logging.warning('Multiple (%i) NIFTI files found (%s:%s). Skipping.'
                            % (len(nifti_files), scan_id, experiment_id))
            return None
        else:
            nii_file = nifti_files[0]
            if op.splitext(nii_file['Name'])[1] == '.nii':
                suffix = '.nii'
            else:
                suffix = '.nii.gz'
            fd, path = tempfile.mkstemp(suffix)
            try:
                with os.fdopen(fd, 'wb') as f:
                    f.write(self.xnat_instance.get(nii_file['URI']).content)
                # do IMAGE stuff here!
                nii_info = self.parse_image_stats(path)
                nii_info.insert(0, scan_id)
            finally:
                os.remove(path)
        return nii_info

    def run(self, experiment_id):

        t1w_scan_labels = self.lut.get('T1', [])
        cols = ['ID', 'xsiType', 'xnat:imageScanData/type',
                'xnat:imageScanData/quality', 'xnat:imageScanData/frames']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=cols).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}

        # filter out unsuitable scan_data items
        valid_t1w_scans = {
            str(scan_id): scan_data for scan_id, scan_data in scans.items()
            if __is_valid_scan__(self.xnat_instance, scan_data)
            and scan_data['xnat:imagescandata/type'].strip() in t1w_scan_labels}

        if not valid_t1w_scans:
            return Results(False, data=['No valid T1W scans found. '
                                        'Not runnable.'])

        # pick one random scan
        scan_id = list(valid_t1w_scans.keys())[0]
        t1_image_info = self.get_scan_nifti_info(experiment_id, scan_id)
        if not t1_image_info:
            return Results(False,
                           data=['Unable to parse T1W scan %s image metrics. '
                                 'Not runnable.' % scan_id])

        if 1 < int(t1_image_info[1]) < 250:
            return Results(True, data=t1_image_info)
        else:
            return Results(False, data=t1_image_info)

    def report(self):
        report = []

        if len(self.results.data) > 1:
            report.append('|ScanID|Scaling Slope|Scaling Intercept|'
                          'Data min|Data max|Grayscale intensities|')
            report.append('|---|---|---|---|---|---|')
            report.append('|%s|' % '|'.join(map(str, self.results.data)))
        else:
            report = self.results.data

        return report
