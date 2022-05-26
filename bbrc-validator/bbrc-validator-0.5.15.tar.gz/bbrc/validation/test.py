from datetime import datetime
import logging as log


class Results(object):
    def __init__(self, has_passed, data=None, elapsedtime=None):
        self.has_passed = has_passed
        if data is not None:
            self.data = data
            if elapsedtime is not None:
                self.elapsedtime = elapsedtime

    def to_dict(self):
        j = {}
        for each in ['has_passed', 'data']:
            if hasattr(self, each):
                j[each] = getattr(self, each)
        return j


class Test(object):
    ''' Description of the test '''
    passing = 'PASSING_INSTANCE_ID'
    failing = 'FAILING_INSTANCE_ID'

    def __init__(self, lut, xnat_instance=None):
        self.lut = lut
        self.xnat_instance = xnat_instance

    def __run__(self, *args, **kwargs):
        startTime = datetime.now()
        res = self.run(*args, **kwargs)
        # Estimates elapsed time
        seconds = datetime.now() - startTime
        m, s = divmod(seconds.total_seconds(), 60)
        h, m = divmod(m, 60)
        elapsedtime = "%d:%02d:%02d" % (h, m, s)
        if not hasattr(res, 'data'):
            res.data = {}
        res.elapsedtime = elapsedtime
        return res

    def run(self, **kwargs):
        raise NotImplementedError

    def report(self):
        data = self.results.data
        # data.pop('elapsedtime')
        log.info('report %s' % str([str(data)]))
        report = data
        return report


class ExperimentTest(Test):
    ''' Description of the test '''
    passing = 'PASSING_EXPERIMENT_ID'
    failing = 'FAILING_EXPERIMENT_ID'

    def run_over_project(self, project_id):
        columns = ['ID', 'label']
        experiments = self.xnat_instance.array.experiments(project_id=project_id,
                                                           columns=columns).data
        occurrences = {sid['ID']: self.run(sid['ID']) for sid in experiments}
        return occurrences


class ScanTest(Test):
    ''' Description of the test '''
    passing = ('EXPERIMENT_ID', 'PASSING_SCANID')
    failing = ('EXPERIMENT_ID', 'FAILING_SCANID')

    def run_over_experiment(self, experiment_id):
        from .utils import __is_valid_scan__
        startTime = datetime.now()
        # get metadata for ALL scans' resources
        columns = ['ID', 'xsiType', 'xnat:imageScanData/type',
                   'xnat:imageScanData/quality', 'xnat:imageScanData/frames']
        scans = self.xnat_instance.array.scans(experiment_id=experiment_id,
                                               columns=columns).data
        scans = {s['xnat:imagescandata/id']: s for s in scans}

        # filter out unsuitable scan_data items
        valid_scans = {str(scan): scans[scan] for scan in scans
                       if __is_valid_scan__(self.xnat_instance, scans[scan])}

        import fnmatch
        # check occurrences of scans of type '*'
        matching_scans = [scan for scan in valid_scans if
             fnmatch.fnmatch(valid_scans[scan]['xnat:imagescandata/type'], '*')]

        # get MRScan metadata for each of the MRExperiments found
        occurrences = [(scan_id, self.run(experiment_id, scan_id))
                       for scan_id in matching_scans]

        # Estimates elapsed time
        seconds = datetime.now() - startTime
        m, s = divmod(seconds.total_seconds(), 60)
        h, m = divmod(m, 60)
        elapsedtime = "%d:%02d:%02d" % (h, m, s)

        has_passed = True
        is_skipped = True
        for each in [e[1].has_passed for e in occurrences]:
            if each == False:
                has_passed = False
                is_skipped = False
            elif each == True:
                is_skipped = False
        if is_skipped:
            has_passed = None

        dt = {False: 'FAILED',
              None: 'SKIPPED'}

        failed = []
        if not is_skipped:
            failed = ["%s: %s\n"%(e[0], dt[e[1].has_passed]) \
                for e in occurrences if e[1].has_passed != True]

        results = Results(has_passed, failed, elapsedtime=elapsedtime)
        return results
