import os
import time
import csv
import glob
import requests
import xml.dom.minidom as md
from bs4 import BeautifulSoup
from pypers.utils import utils
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract ITID archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "input_files",
                    "type": "file",
                    "descr": "the files to extract"
                }
            ],
            "params": [
                {
                    "name": "img_dir",
                    "type": "str",
                    "descr": "Image directory for extractor",
                    "value": "/data/scratch/itid/"
                },
                {
                    "name": "store_dir",
                    "type": "str",
                    "descr": "Download directory for extractor",
                    "value": "/data/scratch/itid-downloaded/"
                },
                {
                    "name": "img_map_file",
                    "type": "str",
                    "descr": "Image map file",
                    "value": "/data/scratch/itid/query_design_id.csv"
                },
                {
                    "name": "img_map_redo_f",
                    "type": "str",
                    "descr": "Image map file",
                    "value": "/data/scratch/itid/query_design_id.redo.csv"
                },

            ]
        }
    }

    def get_raw_data(self):
        self.bad_files = []
        return None

    def process_xml_data(self, *args):
        if not len(self.input_files):
            return 0, 0

        xml_count = img_count = 0

        # the images
        img_dir = self.img_dir
        store_dir = self.store_dir

        img_map = {}

        with open(self.img_map_redo_f, 'r') as infile:
            img_map_redo = [
                el.rstrip() for el in infile.readlines()]

        with open(self.img_map_file, 'r') as infile:
            reader = csv.reader(infile)
            next(reader, None)  # skip the header
            for rows in reader:
                if rows[2]:
                    img_map[rows[2]] = rows[0]
                else:
                    img_map[rows[1][2:]] = rows[0]

        with open(self.img_map_file, 'r') as infile:
            reader = csv.reader(infile)
            next(reader, None)  # skip the header
            num_map = dict((rows[2],
                            rows[1][2:]) for rows in reader if rows[2])
        proxy_params = self.get_connection_params()
        for input_file in self.input_files:
            archive_uid, _ = os.path.splitext(os.path.basename(input_file))

            extraction_data = []

            # extract in a directory having the same name as the archive
            dest_dir = os.path.join(self.output_dir, archive_uid)
            os.makedirs(dest_dir)

            with requests.session() as session, open(input_file, 'r') as fh:
                soup = BeautifulSoup(fh, "html.parser")
                links = soup.find_all('a')
                for link in links:
                    url = link.attrs['href']
                    appnum = link.get_text()

                    dsgnum = num_map.get(appnum, appnum)
                    dsgid = img_map.get(appnum, img_map.get(dsgnum, None))

                    if not dsgid:
                        continue

                    try:
                        img_map_redo.index(dsgid)
                        self.logger.info(dsgid, 'missed')
                    except Exception as e:
                        continue

                    dsgyear = dsgnum[:4]

                    if dsgyear == '0000':
                        self.logger.info("%s, %s, bad number'" % (url, appnum))
                        continue
                    imgs = glob.glob(os.path.join(
                        img_dir, '*', '*', dsgid, '%s_*-media*' % dsgid))
                    imgs = utils.sort_human(imgs)
                    self.logger.info('  - %s imgs' % len(imgs))

                    xml_count += 1

                    mark_fname = os.path.join(dest_dir, '%s.xml' % dsgnum)
                    # store
                    store_file = os.path.join(store_dir, '%s.xml' % dsgnum)
                    if os.path.exists(store_file):
                        os.rename(store_file, mark_fname)
                    else:
                        # time.sleep(1)
                        response = session.get(url, proxies=proxy_params)
                        try:
                            mark_str = ''.join(
                                c for c in response.content if (ord(c) >= 32))
                            mark_dom = md.parseString(mark_str)
                            if len(mark_dom.getElementsByTagName(
                                    'exceptionVO')):
                                self.logger.error('ERROR for %s - %s' % (url, dsgid))
                                self.bad_files.append("%s - %s" % (url, dsgid))
                                continue

                            data_app_node = mark_dom.getElementsByTagName(
                                'ApplicantKey')
                            data_rep_node = mark_dom.getElementsByTagName(
                                'RepresentativeKey')

                            for app_key in data_app_node:
                                applicant_uri = xmldom.get_nodevalue(
                                    'URI', dom=app_key)

                                time.sleep(.1)
                                response = session.get(applicant_uri,
                                                       proxies=proxy_params)
                                try:
                                    app_dom = md.parseString(
                                        response.content)

                                    app_node = app_dom.getElementsByTagName(
                                        'Applicant')
                                    if len(app_node):
                                        applicant_node = app_key.parentNode
                                        applicant_node.replaceChild(
                                            app_node[0],
                                            applicant_node.getElementsByTagName(
                                                'Applicant')[0])
                                except Exception as e:
                                    self.logger.error(
                                        'missing applicant for %s [%s]' % (
                                            dsgnum, applicant_uri))
                            for rep_key in data_rep_node:
                                rep_uri = xmldom.get_nodevalue(
                                    'URI', dom=rep_key)

                                time.sleep(.1)
                                response = session.get(rep_uri,
                                                       proxies=proxy_params)
                                try:
                                    rep_dom = md.parseString(response.content)
                                    rep_node = rep_dom.getElementsByTagName(
                                        'Representative')
                                    if len(rep_node):
                                        rep_node_o = rep_key.parentNode
                                        rep_node_o.replaceChild(
                                            rep_node[0],
                                            rep_node_o.getElementsByTagName(
                                                'Representative')[0])
                                except Exception as e:
                                    self.logger.error(
                                        'missing representative for %s [%s]' % (
                                            dsgnum, rep_key))
                        except ValueError as ve:
                            self.logger.error('REDO %s' % dsgid)
                            self.logger.error(ve)
                            raise ve

                        try:
                            dom_elt = mark_dom.getElementsByTagName(
                                'DesignRepresentationSheetDetails')[0]
                            dom_elt.setAttribute('wipoviewcount',
                                                 str(len(imgs)))
                        except Exception as _:
                            pass

                        xmldom.save_xml(
                            mark_dom, mark_fname, addindent='  ', newl='\n')

                    sub_output = {}
                    sub_output['appnum'] = '%s-0001' % dsgnum
                    sub_output['xml'] = os.path.relpath(mark_fname, dest_dir)
                    sub_output['img'] = []

                    for img in imgs:
                        self.logger.info('  - ', os.path.basename(img))
                        img_count += 1
                        sub_output['img'].append(img)
                    extraction_data.append(sub_output)
            self.output_data.append(extraction_data)
            self.dest_dir.append(dest_dir)
            self.archive_name.append(archive_uid)
        return xml_count, img_count
