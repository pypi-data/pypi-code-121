from ..test import ExperimentTest, Results
from . import spm


class HasCorrectItems(ExperimentTest):
    """Passes if a `FTM_QUANTIFICATION` resource is found and this resource
    has the expected items according to the pipeline
    [specifications](https://gitlab.com/bbrc/xnat/xnat-pipelines/-/tree/master/pet#outputs)."""

    passing = 'BBRCDEV_E02124',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FTM_QUANTIFICATION'
    expected_items = ['quantification_results.csv',
                      'static_pet.nii.gz',
                      'wstatic_pet_scaled_cgm.nii.gz',
                      'wstatic_pet_scaled_pons.nii.gz',
                      'wstatic_pet_scaled_wcbs.nii.gz',
                      'wstatic_pet_scaled_wc.nii.gz',
                      'wstatic_pet_scaled_wm.nii.gz',
                      'optimized_static_pet.nii.gz',
                      'woptimized_static_pet_scaled_cgm.nii.gz',
                      'woptimized_static_pet_scaled_pons.nii.gz',
                      'woptimized_static_pet_scaled_wcbs.nii.gz',
                      'woptimized_static_pet_scaled_wc.nii.gz',
                      'woptimized_static_pet_scaled_wm.nii.gz',
                      'pyscript_coregister.m',
                      'pyscript_coregister_icbm152.m',
                      'pyscript_newsegment.m',
                      'pyscript_normalize12.m',
                      'pyscript_realign.m',
                      'pyscript_setorigin.m',
                      'pyscript_smooth.m']

    def run(self, experiment_id):
        e = self.xnat_instance.select.experiment(experiment_id)
        label = e.label()
        self.expected_items.append('{}.log'.format(label))
        self.expected_items.append('{}.err'.format(label))

        res = e.resource(self.resource_name)
        file_list = set([e.attributes()['Name'] for e in res.files()])
        missing = set(self.expected_items).difference(file_list)

        msg = []
        result = True
        if missing:
            result = False
            msg.append('Missing items: {}.'.format(list(missing)))

        return Results(result, data=msg)


class QuantificationResultsShape(ExperimentTest):
    """`FTM_QUANTIFICATION` resources have quantification results stored as
    tabular data in a CSV-formatted file. This test attempts to read the CSV file
    and assert that its dimensions match the expected shape. Test fails if file
    content cannot be parsed as CSV or if data dimensions do not match the
    expected size (2010 rows x 6 columns). Passes otherwise."""

    passing = 'BBRCDEV_E02124',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FTM_QUANTIFICATION'
    csv_shape = (2010, 6)

    def run(self, experiment_id):
        import io
        import pandas as pd
        import pandas.errors as pd_errors

        e = self.xnat_instance.select.experiment(experiment_id)
        res = e.resource(self.resource_name)

        csv_file = res.file('quantification_results.csv')
        csv_content = (self.xnat_instance.get(csv_file._uri)).text
        try:
            df = pd.read_csv(io.StringIO(csv_content))
        except pd_errors.ParserError:
            return Results(False, data=['Invalid CSV file format.'])

        if not df.shape == self.csv_shape:
            return Results(False, data=['Invalid CSV file dimensions; expected:'
                                        '{}, current: {}'.format(self.csv_shape,
                                                                 df.shape)])
        return Results(True, data=[])


class HasCorrectFSLVersion(ExperimentTest):
    """This test checks the version of FSL used for processing the images.
    Passes if FTM_QUANTIFICATION outputs were created using the expected
    version (i.e. `6.0.1`)."""

    passing = 'BBRCDEV_E02124',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FTM_QUANTIFICATION'

    def run(self, experiment_id):

        expected_version = 'FSL Version: 6.0.1'

        e = self.xnat_instance.select.experiment(experiment_id)
        res = e.resource(self.resource_name)
        log = res.file('LOGS/{}.log'.format(e.label()))
        if not log.exists():
            msg = '{} log file not found.'.format(self.resource_name)
            return Results(False, data=[msg])

        log_data = self.xnat_instance.get(log._uri).text
        version = [line for line in log_data.splitlines()
                   if line.startswith('FSL Version')]

        if not version or version[0] != expected_version:
            return Results(False, data=['{}'.format(version[0])])

        return Results(True, data=[])


class HasCorrectSPMVersion(spm.HasCorrectSPMVersion):
    __doc__ = spm.HasCorrectSPMVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'FTM_QUANTIFICATION')

    passing = 'BBRCDEV_E02124',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FTM_QUANTIFICATION'


class HasCorrectMatlabVersion(spm.HasCorrectMatlabVersion):
    __doc__ = spm.HasCorrectMatlabVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'FTM_QUANTIFICATION')

    passing = 'BBRCDEV_E02124',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FTM_QUANTIFICATION'


class HasCorrectOSVersion(spm.HasCorrectOSVersion):
    __doc__ = spm.HasCorrectOSVersion.__doc__
    __doc__ = __doc__.replace('SPM12_SEGMENT', 'FTM_QUANTIFICATION')

    passing = 'BBRCDEV_E02124',
    failing = 'BBRCDEV_E02102',
    resource_name = 'FTM_QUANTIFICATION'
