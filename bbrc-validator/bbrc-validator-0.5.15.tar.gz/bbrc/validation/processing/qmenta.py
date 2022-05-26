from ..test import ExperimentTest, Results

class HasCorrectItems(ExperimentTest):
    '''Passes if a QMENTA resource is found and this resource has the
    correct items.'''

    passing = 'BBRCDEV_E00281',
    failing = 'BBRCDEV_E00272',

    def run(self, experiment_id):
        from fnmatch import fnmatch

        expected_items = ['lesion_load_measures.pdf',
                          'report.pdf',
                          'FA_map.nii.gz',
                          'T1.nii.gz',
                          'RightCST.nii.gz',
                          'LeftCST.nii.gz',
                          'RightFornix.nii.gz',
                          'LeftFornix.nii.gz',
                          'RightSLF.nii.gz',
                          'LeftSLF.nii.gz',
                          'RightUNC.nii.gz',
                          'LeftUNC.nii.gz',
                          'RightCing.nii.gz',
                          'LeftCing.nii.gz',
                          'Fmajor.nii.gz',
                          'Fminor.nii.gz',
                          'RightIFOF.nii.gz',
                          'LeftIFOF.nii.gz',
                          'RightILF.nii.gz',
                          'LeftILF.nii.gz',
                          'lesion_load_measures.csv',
                          'RightCST.trk',
                          'LeftCST.trk',
                          'RightFornix.trk',
                          'LeftFornix.trk',
                          'RightSLF.trk',
                          'LeftSLF.trk',
                          'RightUNC.trk',
                          'LeftUNC.trk',
                          'RightCing.trk',
                          'LeftCing.trk',
                          'Fmajor.trk',
                          'Fminor.trk',
                          'RightIFOF.trk',
                          'LeftIFOF.trk',
                          'RightILF.trk',
                          'LeftILF.trk',
                          'Cl.csv',
                          'Cp.csv',
                          'Cs.csv',
                          'FA.csv',
                          'MD.csv',
                          'RD.csv',
                          'AD.csv']

        res = self.xnat_instance.select.experiment(experiment_id).resource('QMENTA_RESULTS')

        file_list = set([e.attributes()['Name'] for e in res.files()])

        for e in expected_items:
            if not [f for f in file_list if fnmatch(f, e)] :
                return Results(False, data=['QMENTA_RESULTS %s matching item not found.'%e])

        return Results(True, data=[])


class HasCorruptedLargeFiles(ExperimentTest):
    '''Are considered _large files_ these items structured after a file format
    which require of a structured file header to store any minimal piece of data.
    Specifically for QMENTA an item of any of the following types:
    [`.pdf`,`.nii.gz`,`.trk`].
    Test passes if all _large files_ found in the current QMENTA resource have a
    minimum size value of 5KBytes. Fails otherwise considering that small-sized
    files could potentially be empty or corrupted.'''

    passing = 'BBRCDEV_E00281',
    failing = 'BBRCDEV_E00397',

    def run(self, experiment_id):
        import os.path as op

        extensions = ['.pdf', '.gz', '.trk']
        min_file_size = 5000

        res = self.xnat_instance.select.experiment(experiment_id).resource('QMENTA_RESULTS')

        file_list = [f.label() for f in res.files()
                     if op.splitext(f.label())[1] in extensions
                     and int(f.size()) < min_file_size ]

        if file_list:
            return Results(False, data=['Corrupted or empty files: %s'%file_list])

        return Results(True, data=[])


class HasCorrectTabularData(ExperimentTest):
    '''QMENTA results have tabular data stored as CSV-formatted files. This test
    attempts to read these CSV files content, searches for `NaN` values in the
    dataset and asserts that its dimensions coincide with the expected shape.
    Test fails either if CSV files cannot be parsed, `NaN` values are found in
    the data or if the data dimensions do not match the expected size
    (16 rows x 5 columns). Passes otherwise.'''

    passing = 'BBRCDEV_E00281',
    failing = 'BBRCDEV_E00397',

    def run(self, experiment_id):
        import io
        import pandas as pd

        csv_shape = (16, 5)
        nan_values = []
        wrong_shaped = []

        res = self.xnat_instance.select.experiment(experiment_id).resource('QMENTA_RESULTS')

        csv_list = [f for f in res.files() if f.label().endswith('.csv')]

        for item in csv_list:
            csv_content = (self.xnat_instance.get(item._uri)).text
            df = pd.read_csv(io.StringIO(csv_content))

            if df.isnull().values.any():
                nan_values.append(item.label())

            if not df.shape == csv_shape:
                wrong_shaped.append(item.label())

        if nan_values:
            return Results(False, data=['NaN values found: %s'%nan_values])
        elif wrong_shaped :
            return Results(False, data=['Invalid data dimensions: %s' % wrong_shaped])

        return Results(True, data=[])


class HasCorrectStreamlines(ExperimentTest):
    '''QMENTA tractography results include per-region streamlines information
    stored as `Track` file format (.trk extension). This test attempts to validate
    the content of such Track files by loading them via `nibabel` package and
    naively assert that parsed file header is a valid dictionary structure as expected.
    Test fails if Track files cannot be parsed. Passes otherwise.'''

    passing = 'BBRCDEV_E00281',
    failing = 'BBRCDEV_E00397',

    def run(self, experiment_id):
        import os.path as op
        import tempfile
        import nibabel as nib

        files = []

        res = self.xnat_instance.select.experiment(experiment_id).resource('QMENTA_RESULTS')

        trk_list = [f for f in res.files() if f.label().endswith('.trk')]

        with tempfile.TemporaryDirectory() as temp_dir:
            for item in trk_list:
                temp_file = item.get(dest=op.join(temp_dir, item.attributes()['Name']))
                try :
                    trk_file = nib.streamlines.load(temp_file)
                except :
                    files.append(item.label())
                    continue
                else :
                    if not isinstance(trk_file.header,dict) :
                        files.append(item.label())
                    #if not trk_file.header['nb_streamlines'] == 2624:
                    #    files.append(item.label())

        if files:
            return Results(False, data=['Invalid track files: %s'%files])

        return Results(True, data=[])