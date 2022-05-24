import os
import re
import requests
import codecs
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract CHTM marks information from api
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    # a file with application numbers that have changed
    def unpack_archive(self, archive, dest):
        self.logger.debug('processing file %s' % archive)

        with open(archive, 'r') as fh:
            appnum_list = [line.rstrip() for line in fh.readlines()]
        self.logger.debug('found %s applications to retrieve' % len(appnum_list))

        SOAP_ENVELOPE_GET = """
        <s11:Envelope xmlns:s11='http://schemas.xmlsoap.org/soap/envelope/'><s11:Body>
          <ns1:getIpRightXML xmlns:ns1='https://www.swissreg.ch/services'>
            <ns1:ipRight xmlns:ns1='https://www.swissreg.ch/services'>CH-TM</ns1:ipRight>
            <ns1:keys xmlns:ns1='https://www.swissreg.ch/services'>%(appnum_list)s</ns1:keys>
          </ns1:getIpRightXML>
        </s11:Body></s11:Envelope>"""
        proxy_params, auth = self.get_connection_params('from_api')
        headers = {'content-type': 'application/soap+xml', 'SOAPAction': ''}

        soap_envelope = SOAP_ENVELOPE_GET % (
            {'appnum_list': ','.join(appnum_list)})

        with requests.session() as session:
            response = session.post(self.conn_params['url'],
                                    data=soap_envelope,
                                    proxies=proxy_params,
                                    auth=auth, headers=headers)
            # get the soap response and store it in a file
            response_dom = md.parseString(response.content)
            response_xml = response_dom.getElementsByTagName(
                'getIpRightXMLReturn')[0].firstChild.nodeValue

        response_file = os.path.join(self.extraction_dir, 'response.xml')
        with codecs.open(response_file, 'wb', 'utf-8') as fh:
            fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            fh.write(response_xml)

        self.process_xml_data(response_file, dest)

    # one xml file containing multi xml documents
    def process_xml_data(self, response_file, dest):
        context = ET.iterparse(response_file, events=('end', ))
        for event, elem in context:
            tag = elem.tag

            if not tag == 'transac':
                continue
            appnum = elem.find('marinfo').find('basappn').text
            # sanitize
            appnum = appnum.replace('/', '')

            # saving xml file
            # ---------------
            appxml_file = os.path.join(dest, '%s.xml' % appnum)

            with codecs.open(appxml_file, 'w', 'utf-8') as fh:
                fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                fh.write(ET.tostring(elem).decode("utf-8"))

            self.add_xml_file(appnum, appxml_file)

            img_uri = ''
            imgtag = elem.find('marinfo').find('marpicn')
            if imgtag is not None and imgtag.text:
                self.add_img_url(appnum, imgtag.text)

        # done with the file of files
        os.remove(response_file)

    def collect_files(self, dest):
        pass

    def process(self):
        pass
