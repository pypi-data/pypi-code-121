import os
import datetime

import json
from pypers.steps.base.fetch_step_api import FetchStepAPI


class ISTM(FetchStepAPI):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using REST API"
        ],
        "args":
        {
            "params": [
                {
                    "name": "api",
                    "type": "str",
                    "descr": "the api end-point"
                },
            ]
        }
    }

    def get_intervals(self):
        # get the date of the last update
        # expecting names like : 2018-01-07.TO.2018-01-08.json
        if not self.done_archives:
            last_update = datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')

        else:
            last_update = os.path.splitext((sorted(self.done_archives)[-1]))[0]
            last_update = last_update.split('.TO.')[-1]
            # last_update = '20091231'
            last_update = datetime.datetime.strptime(last_update, '%Y-%m-%d')

        today = datetime.datetime.today()
        days_diff = (today - last_update).days

        intervals = []
        # get updates day by day
        for delta in range(days_diff):
            fetch_day = last_update + datetime.timedelta(days=delta + 1)
            fetch_nday = last_update + datetime.timedelta(days=delta + 2)
            intervals.append({
                'start': fetch_day.strftime('%Y-%m-%d'),
                'end': fetch_nday.strftime('%Y-%m-%d')})
            if self.limit and len(intervals) == self.limit:
                break
        return intervals

    def specific_api_process(self, session):
        for interval in self.intervals:
            marks_interval = []
            marks_file = os.path.join(
                self.output_dir, '%(start)s.TO.%(end)s.json' % interval)
            page = 1
            while True:
                interval['page'] = page

                marks = self.get_updates(session, self.api_url % interval,
                                         proxies=self.proxy_params)
                marks_json = json.loads(marks)

                # done for this interval => write file
                if not len(marks_json):
                    if len(marks_interval):
                        with open(marks_file, 'w') as fh:
                            fh.write(json.dumps(marks_interval, indent=4))
                        self.output_files.append(marks_file)
                    break

                # goto next page
                marks_interval += marks_json
                page = page + 1

