import os
import datetime
import codecs

import xml.dom.minidom as md

from pypers.steps.base.fetch_step_api import FetchStepAPI


class NZ(FetchStepAPI):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using REST API"
        ],
        "args":
        {
            "params": [
                {
                    "name": "token",
                    "type": "str",
                    "descr": "the api token"
                },
                {
                    "name": "api",
                    "type": "str",
                    "descr": "the api end-point"
                },
                {
                    "name": "id_tagname",
                    "type": "str",
                    "descr": "the tag name for record identifier. "
                             "ex: AppplicationNumber or RegistrationNumber"
                },
            ]
        }
    }

    def get_connections_info(self):
        api_url = os.path.join(self.conn_params['url'], self.api)
        headers = {'Authorization': 'Bearer %s' % self.conn_params['token']}
        return api_url, headers

    def get_intervals(self):
        # get the date of the last update
        if self.done_archives:
            last_update = os.path.splitext((sorted(self.done_archives)[-1]))[0]
            last_update = last_update[last_update.index('-')+1:]
        else:
            last_update = '20091231'
        last_update = datetime.datetime.strptime(last_update, '%Y%m%d')
        today = datetime.datetime.today()

        days_diff = (today - last_update).days

        intervals = []
        # get updates day by day
        for delta in range(days_diff):
            fetch_day = last_update + datetime.timedelta(days=delta+1)
            date_range = '%s-%s' % (fetch_day.strftime('%Y%m%d'),
                                    fetch_day.strftime('%Y%m%d'))
            intervals.append(date_range)
            if self.limit and len(intervals) == self.limit:
                break
        return intervals

    def get_url_postprocess(self, updates_xml):
        updates_dom = md.parseString(updates_xml)

        # this will throw an exception if the response
        # was a <TransactionError>
        updates_dom.getElementsByTagName(
            'FromDate')[0].firstChild.nodeValue.lower()
        return updates_dom

    def specific_api_process(self, session):
        for interval in self.intervals:
            updates_dom = self.get_updates(session, self.api_url % interval,
                                           proxies=self.proxy_params,
                                           headers=self.headers,
                                           postprocess=self.get_url_postprocess)
            errors = updates_dom.getElementsByTagNameNS('*',
                                                        'TransactionError')

            if len(errors) > 0:
                self.logger.info('%s: could not get the updates at the moment.'
                                 'Stop here!' % interval)
                break

            appnums = updates_dom.getElementsByTagNameNS('*',
                                                         self.id_tagname)
            self.logger.info('%s: %d applications found' % (
                interval, len(appnums)))

            archive_dest = os.path.join(self.output_dir,
                                        '%s.xml' % interval)

            with codecs.open(archive_dest, 'w', 'utf-8') as fh:
                fh.write(updates_dom.toprettyxml())
            self.output_files.append(archive_dest)
