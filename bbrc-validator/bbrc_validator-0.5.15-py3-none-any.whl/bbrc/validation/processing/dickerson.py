from ..test import ExperimentTest, Results


class HasCorrectItems(ExperimentTest):
    """Passes if a `DICKERSON` resource is found and this resource has the
    expected items according to the pipeline
    [specifications](https://gitlab.com/bbrc/xnat/xnat-pipelines/-/tree/master/dickerson#outputs)."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E02920',
    resource_name = 'DICKERSON'
    expected_items = ['ad/{h}.adsig.label',
                      'ad/{h}.ag.label',
                      'ad/{h}.ifs.label',
                      'ad/{h}.itg.label',
                      'ad/{h}.mtl.label',
                      'ad/{h}.precun.label',
                      'ad/{h}.sfg.label',
                      'ad/{h}.smg.label',
                      'ad/{h}.spl.label',
                      'ad/{h}.tpole.label',
                      'aging/{h}.ag.label',
                      'aging/{h}.calcarine.label',
                      'aging/{h}.cfusi.label',
                      'aging/{h}.cinsula.label',
                      'aging/{h}.cmfg.label',
                      'aging/{h}.cuneus.label',
                      'aging/{h}.ifg.label',
                      'aging/{h}.loccip.label',
                      'aging/{h}.msfg.label',
                      'aging/{h}.precent.label',
                      'aging/{h}.smg.label']

    def run(self, experiment_id):
        result = True

        e = self.xnat_instance.select.experiment(experiment_id)
        res = e.resource(self.resource_name)

        missing = []
        for item in self.expected_items:
            for hemis in ['lh', 'rh']:
                f = res.files(item.format(h=hemis)).get()
                if not f:
                    missing.append(item.format(h=hemis))

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
    """This test checks the version of FreeSurfer used. Passes if `DICKERSON`
    outputs were created using the expected version (`{version}`)."""

    passing = 'BBRCDEV_E02823',
    failing = 'BBRCDEV_E02920',
    resource_name = 'DICKERSON'
    expected_version = 'freesurfer 7.1.1'
    __doc__ = __doc__.format(version=expected_version)

    def run(self, experiment_id):
        e = self.xnat_instance.select.experiment(experiment_id)
        r = e.resource(self.resource_name)
        log = r.file('LOGS/{}.log'.format(e.label()))
        if not log.exists():
            msg = '{} log file not found.'.format(self.resource_name)
            return Results(False, data=[msg])

        log_data = self.xnat_instance.get(log._uri).text
        version = [line[16:] for line in log_data.splitlines()
                   if line.strip().startswith('mri_label2label freesurfer')]

        if not version or version[0] != self.expected_version:
            return Results(False, data=['Incorrect FreeSurfer version: '
                                        '{}'.format(version[0])])

        return Results(True, data=[])



