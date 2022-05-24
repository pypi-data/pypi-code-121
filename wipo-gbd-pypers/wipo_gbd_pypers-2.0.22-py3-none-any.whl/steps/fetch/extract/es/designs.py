import os
import glob
import shutil
from xml.dom.minidom import parse
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep
from pypers.steps.fetch.extract.es import get_sub_folders


class Designs(ExtractStep):
    """
    Extract ESID archive
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args": {
            "params": [
                {
                    "name": "get_imgs_pdf",
                    "descr": "a flag whether to get all "
                             "imgs in one shot in a pdf file",
                    "value": 0
                },
                {
                    "name": "img_ref_dir",
                    "descr": "the directory that contains previous extractions"
                }
            ]
        }
    }

    def __find_img_inref(self, name):
        img_base = name[0:name.find('-')]
        img_match = glob.glob(os.path.join(self.img_ref_dir,
                                           img_base[-4:-2], img_base[-2:],
                                           '%s.high.jpg' % name))
        if len(img_match):
            return img_match.pop()
        else:
            return None

    def find_and_replace(self, parent, tag=None, file_prefix=None, files=[]):
        if not len(parent):
            return
        if not len(files):
            return

        parent = parent[0]
        identifiers = [os.path.basename(p)
                       for p in xmldom.get_nodevalues('URI',
                                                      dom=parent)]

        # this is to support 2 different naming schemes
        identifiers = [
            i.split('-')[1]
            if not i.startswith('ES') else i.replace('-pa', '')
            for i in identifiers]
        children = parent.getElementsByTagName(tag)
        for idx, child in enumerate(children):
            # 191385-MI119399
            identifier = identifiers[idx]
            identifier = os.path.basename(identifier)

            for zfile in files:
                if os.path.basename(zfile) == '%s-%s.xml' % (
                        file_prefix, identifier):
                    zdom = parse(zfile)
                    matches = zdom.getElementsByTagName(tag)
                    if len(matches):
                        parent.replaceChild(matches[0], child)
                    # done with the file
                    os.remove(zfile)

    def get_raw_data(self):
        return get_sub_folders(self)

    def process_xml_data(self, sub_folders):
        extraction_data = []
        xml_count = img_count = 0
        for sub_folder in sub_folders:
            xml_data_file = glob.glob(os.path.join(sub_folder,  'DATA-*.xml'))
            # safe to make the assumption of only one DATA file
            xml_data_file = xml_data_file.pop()
            try:
                data_dom = parse(xml_data_file)
            except Exception as e:
                self.logger.error('ERROR: could not parse %s' % xml_data_file)
                continue

            appnum = xmldom.get_nodevalue('ApplicationNumber', dom=data_dom)
            dsnnum = xmldom.get_nodevalue('DesignURI', dom=data_dom)
            dsnnum = dsnnum[-4:]
            # not really necessary here, but just in case
            appnum = appnum.replace('/', '').replace('-', '')

            appuid = '%s-%s' % (appnum, dsnnum)

            xml_count += 1
            files_mapper = [('Applicant', 'Applicant'),
                            ('Representative', 'Representative'),
                            ('PreviousApplicant', 'Applicant')]
            for key in files_mapper:
                files = glob.glob(
                    os.path.join(sub_folder, '%s-*.xml' % key[0].upper()))
                parent = data_dom.getElementsByTagName('%sDetails' % key[0])
                self.find_and_replace(parent, tag=key[1],
                                      file_prefix=key[0].upper(), files=files)
            xmldom.save_xml(data_dom, xml_data_file)
            try:
                os.rmdir(sub_folder)
            except Exception as e:
                pass  # directory not empty. what else is there?

            sub_output = {
                'appnum': appuid,
                'xml': os.path.relpath(xml_data_file, self.dest_dir[0])
            }
            img_uris = xmldom.get_nodevalues('ViewURI', dom=data_dom)

            # no images
            if not len(img_uris):
                self.logger.info('%s - %s' % (appnum, ''))
                extraction_data.append(sub_output)
                continue

            # get the images
            for idx, img_uri in enumerate(img_uris):
                img_count += 1

                img_name = '%s.%d' % (appuid, (idx+1))
                img_match = self.__find_img_inref(img_name)

                if img_match is not None:
                    self.logger.info('%s - %s - FOUND' % (appnum, img_name))
                    img_dest_file = os.path.join(self.dest_dir[0],
                                                 '%s.jpg' % img_name)
                    shutil.copyfile(img_match, img_dest_file)

                    sub_output.setdefault('img', [])
                    sub_output['img'].append(os.path.relpath(
                        img_dest_file, self.dest_dir[0]))
                else:
                    if self.get_imgs_pdf:
                        pdf_uri = 'http://www.oepm.es/imas/disenos/%s/%s-%s.pdf'
                        pdf_uri = pdf_uri % (appnum[1:5], appnum, dsnnum[-2:])
                        sub_output['pdf_uri'] = pdf_uri
                        self.logger.info('%s - %s - DOWNLOAD PDF: %s' % (
                            appnum, img_name, pdf_uri))
                    else:
                        sub_output.setdefault('img_uri', [])
                        sub_output['img_uri'].append(img_uri)
                        self.logger.info('%s - %s - DOWNLOAD: %s' % (
                            appnum, img_name, img_uri))

            extraction_data.append(sub_output)

        self.output_data = [extraction_data]
        return xml_count, img_count
