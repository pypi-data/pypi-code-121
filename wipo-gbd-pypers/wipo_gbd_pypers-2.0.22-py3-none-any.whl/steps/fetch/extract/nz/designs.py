import os
import shutil
import requests
import base64
import xml.etree.ElementTree as ET
from pypers.utils.xmldom import save_xml
from pypers.steps.fetch.extract.nz.trademarks import Trademarks


class Designs(Trademarks):
    """
    Extract NZID designs information from api
    """

    def process_xml_data(self, _):
        ns = 'http://www.iponz.govt.nz/XMLSchema/designs/information'
        ET.register_namespace('', ns)
        xml_count = 0
        img_count = 0
        for archive_path in self.input_xml:
            extraction_data = []
            appnum_list = []
            xml_file, dest_dir, xml_dir, img_dir, archive_name = \
                self.get_xml_data(archive_path)
            # collect application numbers for update
            context = ET.iterparse(xml_file, events=('end', ))
            for event, elem in context:
                if elem.tag[0] == "{":
                    uri, tag = elem.tag[1:].split("}")
                else:
                    tag = elem.tag
                # should not get to this as the download step
                # will not output a file with transaction error
                if tag == 'TransactionError':
                    raise Exception(
                        '%s has a transaction errror. abort!' % xml_file)
                if tag == 'Design':
                    appnum = elem.find(
                        '{%(ns)s}RegistrationNumber' % {'ns': ns}).text
                    appnum_list.append(appnum)
            # for every application number, get its details into an xml file
            with requests.session() as session:
                for appnum in appnum_list:
                    sub_output = {}

                    # saving xml files
                    # ----------------
                    appxml_file = os.path.join(xml_dir, '%s.xml' % appnum)
                    design_dom = self.get_application(session, appnum)
                    if design_dom is None:
                        continue
                    xml_count += 1
                    save_xml(design_dom, appxml_file, addindent='  ', newl='\n')

                    sub_output['appnum'] = appnum
                    sub_output['xml'] = os.path.relpath(appxml_file, dest_dir)

                    # loop over design articles
                    design_articles = design_dom.getElementsByTagName(
                        'DesignArticle')

                    sub_output['img'] = []
                    for article_idx, design_article in enumerate(
                            design_articles):
                        # see if there is an image and get it
                        article_imgs = design_article.getElementsByTagName(
                            'RepresentationSheetFilename')

                        # saving img files
                        # ----------------
                        for idx, article_img in enumerate(article_imgs):
                            article_img_val = str(
                                article_img.firstChild.nodeValue)
                            img_src_name = '%s-%s.%d.high.jpg' % (
                                appnum, str(article_idx + 1).zfill(4), idx + 1)
                            img_dest_name = '%s-%s.%d.jpg' % (
                                appnum, str(article_idx + 1).zfill(4), idx + 1)

                            img_store = os.path.join(self.img_ref_dir,
                                                     appnum[-4:-2],
                                                     appnum[-2:],
                                                     img_src_name)
                            if os.path.exists(img_store):
                                article_img_dest = os.path.join(img_dir,
                                                                img_dest_name)
                                shutil.copyfile(img_store, article_img_dest)
                                sub_output['img'].append(
                                    os.path.relpath(article_img_dest, dest_dir))
                                continue

                            self.logger.info('  %s: %s-downloading new img' % (
                                idx+1, article_img_val))
                            post_data = '<soapenv:Envelope xmlns:get="http://' \
                                        'data.business.govt.nz/services/' \
                                        'getDocument" xmlns:soapenv="' \
                                        'http://schemas.xmlsoap.org/soap/' \
                                        'envelope/"><soapenv:Body>' \
                                        '<get:getDocument>' \
                                        '<get:ObjectIdentifier>%s' \
                                        '</get:ObjectIdentifier>' \
                                        '</get:getDocument>' \
                                        '</soapenv:Body></soapenv:Envelope>'
                            post_data = post_data % article_img_val
                            article_img_ext, article_img_dat = self.get_image(
                                session, post_data)

                            if article_img_ext is not None:
                                img_dest_name = '%s-%s.%d.%s' % (
                                    appnum, str(article_idx + 1).zfill(4),
                                    idx + 1, article_img_ext)
                                article_img_dest = os.path.join(img_dir,
                                                                img_dest_name)
                                with open(article_img_dest, 'wb') as fh:
                                    fh.write(base64.b64decode(article_img_dat))
                                sub_output['img'].append(
                                    os.path.relpath(article_img_dest, dest_dir))
                    extraction_data.append(sub_output)

            self.output_files_handeling(extraction_data, dest_dir,
                                        archive_name)
        return xml_count, img_count
