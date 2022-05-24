import os
import re
import requests
import datetime
import math

import xml.dom.minidom as md

from requests.auth import HTTPBasicAuth

from pypers.utils.utils import ls_dir

from pypers.steps.base.fetch_step_api import FetchStepAPI


class CHTM(FetchStepAPI):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using SOAP"
        ],
        "args":
        {
            "params": [
                {
                    "name": "chunk_size",
                    "type": "int",
                    "descr": "the upper limit of the archives to download. "
                             "default 0 (all)",
                    "value": 200  # no rush
                }
            ]
        }
    }

    def _process_from_local_folder(self):
        return False

    def get_connections_info(self):
        api_url = self.conn_params['url']
        auth = HTTPBasicAuth(self.conn_params['credentials']['user'],
                             self.conn_params['credentials']['password'])
        headers = {'content-type': 'application/soap+xml', 'SOAPAction': ''}

        return api_url, (headers, auth)

    def get_intervals(self):
        SOAP_ENVELOPE_SEARCH = """
        <s11:Envelope xmlns:s11='http://schemas.xmlsoap.org/soap/envelope/'><s11:Body>
          <ns1:searchModifiedIpRight xmlns:ns1='https://www.swissreg.ch/services'>
            <ns1:ipRight xmlns:ns1='https://www.swissreg.ch/services'>CH-TM</ns1:ipRight>
            <ns1:fromDateTime xmlns:ns1='https://www.swissreg.ch/services'>%(start_date)sT00:00:00</ns1:fromDateTime>
            <ns1:toDateTime xmlns:ns1='https://www.swissreg.ch/services'>%(end_date)sT23:59:59</ns1:toDateTime>
          </ns1:searchModifiedIpRight>
        </s11:Body></s11:Envelope>
        """
        # get the date of the last update
        # if no done file, set last_update to yesterday
        if not len(self.done_archives):
            last_update = (datetime.datetime.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        else:
            # expecting names like : 2018-01-07.TO.2018-01-08.1.txt
            last_update = sorted(self.done_archives)[-1].split('.')[2]

        # FIXME: make sure that the interval is max 7 days
        # cannot get updates for more than that!
        today = datetime.datetime.today().strftime('%Y-%m-%d')

        if last_update == today:
            self.logger.info("today's update has already been proccessed. exit")
            return None
        soap_envelope = SOAP_ENVELOPE_SEARCH % (
            {'start_date': last_update, 'end_date': today})
        soap_return_file = os.path.join(
            self.output_dir, '%s.TO.%s' % (last_update, today))
        self.logger.info('getting data for %s.TO.%s' % (last_update, today))
        return (soap_envelope, soap_return_file)

    def specific_api_process(self, session):
        if self.intervals is None:
            return
        response = session.post(self.api_url, data=self.intervals[0],
                                proxies=self.proxy_params, auth=self.headers[1],
                                headers=self.headers[0])

        response_dom = md.parseString(response.content)
        response_return = response_dom.getElementsByTagName(
            'searchModifiedIpRightReturn')

        # nothing to update, return
        if not len(response_return):
            return

        # get the appnum list from the soap response
        # and write it in chunks of 1000 to output files
        chunk_size = self.chunk_size
        appnum_list = response_return[0].firstChild.nodeValue.split(',')

        chunk_nb = int(math.ceil(float(len(appnum_list))/chunk_size))

        appnum_chunk_list = [
            # appnum_list[i*chunk_size:i*chunk_size+chunk_size]
            appnum_list[i*chunk_size:i*chunk_size+10]
            for i in range(chunk_nb)]

        self.logger.info('got %s updates, will divide into %s chunks' % (
            len(appnum_list), chunk_nb))
        for idx, appnum_chunk in enumerate(appnum_chunk_list):
            output_chunk_file = '%s.%s.txt' % (self.intervals[1], (idx + 1))
            with open(output_chunk_file, 'w') as fh:
                for appnum in appnum_chunk:
                    fh.write(appnum)
                    fh.write('\n')
            self.output_files.append(output_chunk_file)
