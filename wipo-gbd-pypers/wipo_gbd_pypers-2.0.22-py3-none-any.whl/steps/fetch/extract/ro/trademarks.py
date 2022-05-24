import os
from pypers.utils import download
import re
from pypers.steps.base.extract_step import ExtractStep
import concurrent.futures
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.utils import xmldom


class Trademarks(ExtractStep):
    """
       Extract ROTM archives
       """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
    }

    def do_download(self, uri, dest=None):
        # needed for imgs download
        proxy_params = {
            'http':  self.meta['pipeline']['input'].get('http_proxy', None),
            'https': self.meta['pipeline']['input'].get('https_proxy', None)
        }
        try:
            rh = download.download(
                uri, wait_secs=.2,
                http_proxy=proxy_params['http'],
                https_proxy=proxy_params['https'])
            if dest is None:
                return rh.read()
            with open(dest, 'wb') as fh:
                fh.write(rh.read())
            rh.close()
            return dest
        except Exception as e:
            self.logger.error("Downloading problem in %s: %s" % (uri, e))
            return None

    def update_xml(self, _file, img_url, rep_url, applicant_url):
        dest = os.path.dirname(_file)
        appnum = os.path.basename(_file).replace('.xml', '')
        img = None
        main_dom = md.parse(_file)
        if img_url:
            img_details = self.do_download(
                img_url, os.path.join(dest, '%s.gif' % appnum))
            main_dom = xmldom.set_nodevalue(
                'MarkImageURI', os.path.basename(img_details), dom=main_dom)
            img = img_details
        tmp = {
            'Applicant': applicant_url,
            'Representative': rep_url
        }
        for key in tmp.keys():
            if tmp[key] is not None:
                row_data = self.do_download(tmp[key]).decode('UTF-8')
                row_data = row_data.replace(
                    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '')
                dom_deaitls = md.parseString(row_data)
                details = dom_deaitls.getElementsByTagName(key)
                details = details[0]
                details_main_dom = main_dom.getElementsByTagName(
                    '%sDetails' % key)
                details_main_dom[0].appendChild(details)
        xmldom.save_xml(main_dom, _file, newl='\n', addindent='  ' )
        return img

    def file_walker(self, r, d, files, xml_files, img_map):
        regex = re.compile(r'.*-RO(.*).xml')
        url_base = 'http://bd.osim.ro/trademark/data/%s'
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {}
            for _file in files:
                appnum = "RO%s" % (regex.match(_file).group(1))
                dest = os.path.join(self.dest_dir[0], "%s.xml" % appnum)
                url = url_base % appnum
                future_to_url[executor.submit(self.do_download, url, dest)] = dest
                os.remove(os.path.join(r, _file))
            for future in concurrent.futures.as_completed(future_to_url):
                dest = future_to_url[future]
                xml_files.append(dest)

    def get_raw_data(self):
        return self.get_xmls_files_from_list(file_walker=self.file_walker)

    def process_xml_data(self, *args, **kwargs):
        xml_files = args[0][0]
        future_to_url = {}
        xml_count = 0
        img_count = 0
        extraction_data = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            for xml_file in xml_files:
                context = ET.iterparse(xml_file, events=('end', ))
                rep_url = None
                applicatnt_url = None
                img_url = None
                ns = '*'
                for event, elem in context:
                    if elem.tag[0] == "{":
                        ns, tag = elem.tag[1:].split("}")
                    else:
                        tag = elem.tag
                    if tag == 'MarkImageURI':
                        img_url = elem.text
                    elif tag == 'RepresentativeDetails':
                        rep_url = elem.find(
                            '{%(ns)s}RepresentativeKey/{%(ns)s}URI' % {'ns': ns}).text
                    elif tag == 'ApplicantDetails':
                        applicatnt_url = elem.find(
                            '{%(ns)s}ApplicantKey/{%(ns)s}URI' % {'ns': ns}).text
                future_to_url[executor.submit(
                    self.update_xml, xml_file,
                    img_url, rep_url, applicatnt_url)] = xml_file
            for future in concurrent.futures.as_completed(future_to_url):
                dest = future_to_url[future]
                appnum = os.path.basename(dest).replace('.xml', '')

                img_uri = future.result()
                xml_count += 1
                sub_output = {}
                sub_output['appnum'] = appnum
                sub_output['xml'] = os.path.relpath(dest,
                                                    self.dest_dir[0])
                if img_uri:
                    sub_output['img'] = os.path.relpath(img_uri,
                                                        self.dest_dir[0])
                    img_count += 1
                extraction_data.append(sub_output)
        self.output_data.append(extraction_data)
        return xml_count, img_count
