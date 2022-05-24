import os
import shutil
import datetime
from requests.auth import HTTPBasicAuth
from pypers.steps.base.fetch_step_http import FetchStepHttpAuth


class Designs(FetchStepHttpAuth):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using RSS API"
        ],
    }
    endpoints = {
        'getBibliografischeDaten_eingetragen_XML': 'gsm_bib_eing_xml_',
        'getBilder_eingetragen_JPG_GIF': 'gsm_bib_eing_'}

    def weeks_for_year(self, year):
        currnet_day = 31
        last_week = datetime.date(year, 12, currnet_day)
        while last_week.isocalendar()[1] == 1:
            currnet_day -= 1
            last_week = datetime.date(year, 12, currnet_day)
        return last_week.isocalendar()[1]

    def specific_http_auth_process(self, session):
        self.auth = HTTPBasicAuth(
            self.conn_params['credentials']['Username'],
            self.conn_params['credentials']['Password'])
        self.login_url = self.conn_params['login']
        weeks_interval = []

        current_year = datetime.datetime.today().strftime('%Y')
        current_week = datetime.datetime.today().strftime('%W')
        for week in range(int(current_week) - 7, int(current_week) + 1):
            if week <= 0:
                week_tmp = week + self.weeks_for_year(int(current_year) - 1)
                year_tmp = str(int(current_year) - 1)
                weeks_interval.append('%s%02d' % (year_tmp, week_tmp))

            else:
                weeks_interval.append('%s%02d' % (current_year, week))

        for endpoint in self.endpoints.keys():
            for week in weeks_interval:
                url = "%s/%s/%s" % (self.login_url, endpoint, week)
                archive_name = "%s%s.zip" % (self.endpoints[endpoint], week)
                if archive_name in self.done_archives:
                    continue
                archive_dest = os.path.join(self.output_dir, archive_name)
                self.log.info("Downloading %s to %s" % (url, archive_dest))
                with open(archive_dest, 'wb') as f:
                    r = session.get(url, stream=True, auth=self.auth,
                                    proxies=self.proxy_params)
                    shutil.copyfileobj(r.raw, f)
                self.output_files.append(archive_dest)

