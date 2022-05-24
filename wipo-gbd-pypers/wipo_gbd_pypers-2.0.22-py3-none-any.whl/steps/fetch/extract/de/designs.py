import shutil
import os
import mimetypes
import codecs
import glob
import gzip
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from copy import deepcopy
from pypers.utils import utils
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract DEID archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
            {
                "params": [
                    {
                        "name": "xml_store",
                        "descr": "where xml files are stores"
                    }
                ]
            }
    }

    def get_raw_data(self):
        self.get_extracted_files()
        if len(self.input_archive) == 0:
            return [], {}
        xml_files = []
        img_map = {}  # key=filename value=filepath

        # brilliant
        seven7file = glob.glob(os.path.join(self.dest_dir[0], '*.7z'))
        seven7file += glob.glob(os.path.join(self.dest_dir[0], '*', '*.7z'))
        seven7file += glob.glob(os.path.join(self.dest_dir[0], '*', '*', '*.7z'))

        self.xml_from_7z = False
        for f in seven7file:
            self.xml_from_7z = True
            utils.sevenzextract(f, self.dest_dir[0])
            os.remove(f)
        for root, dirs, files in os.walk(self.dest_dir[0]):
            for file in files:
                name, ext = os.path.splitext(file)
                path = os.path.join(root, file)
                if ext.lower() == '.xml':
                    xml_files.append(path)
                else:  # not an xml, then most probably image
                    file_mime = mimetypes.guess_type(file)[0]
                    if (file_mime or '').startswith('image/'):
                        name = name[name.rfind('\\') + 1:]
                        img_map[name] = path
        return xml_files, img_map

    def process_xml_data(self, data):
        xml_files = data[0]
        if len(xml_files) == 0:
            return 0, 0
        helpers = Helpers(self.dest_dir[0], data[1], self.xml_store, self.logger)

        for xml_file in xml_files:
            self.logger.info('\nprocessing file: %s' % xml_file)
            # xml needs cleaning if was packed in a 7z
            if self.xml_from_7z:
                # silly chars
                chars = (('{', '&#228;'), ('}', '&#252;'),
                         ('|', '&#246;'), ('~', '&#223;'),
                         ('[', '&#196;'), (']', '&#220;'),
                         (u'\xc3', '['), (u'\xc2', ']'))
                ordinals = ((221, '['), (170, ']'), (249, '&#233;'))
                xmldom.clean_xmlfile(
                    xml_file, readenc='iso-8859-1', chars=chars,
                    ordinals=ordinals, overwrite=True)

            context = ET.iterparse(xml_file, events=('end',))
            for event, elem in context:
                if elem.tag == 'TEIL':
                    teil = elem.attrib['Teil'].lower().replace(' ', '_')
                    getattr(helpers, 'iter_%s' % teil)(elem)
                    elem.clear()
            os.remove(xml_file)
        self.output_data = [helpers.output_data]
        return len(xml_files), len(data[1])


class Helpers:
    """
    Class for processing of different bulletin bags
    """

    # -- ignored changes
    ignore_sub_teil = ['C_AL_HL_INTERESSE_LIZ_JA', 'C_AL_HL_INTERESSE_LIZ_NEIN',
                       'C_AL_HL_DINGL_RECHT_DRE', 'C_AL_HL_DINGL_RECHT_DRG',
                       'C_AL_HL_GERICHT_VERF_EIN', 'C_AL_HL_GERICHT_VERF_REX',
                       'C_AL_HL_GERICHT_VERF_SBX', 'C_AL_HL_INSOLVENZ_VERF_IVE',
                       'C_AL_HL_INSOLVENZ_VERF_IVB',
                       'C_AL_HL_NACHTRGL_INAN_PRIO',
                       'C_AL_HL_WIEDEREINSETZ_ANTR',
                       'C_AL_HL_WIEDEREINSETZ_DONE',
                       'C_AL_HL_WIEDEREINSETZ_BACK',
                       'C_AL_HL_WIDERRUF_BEKANNTM', 'C_AL_HL_ZWANGSVOLLSTR_ZVE',
                       'C_AL_HL_ZWANGSVOLLSTR_ZVB', 'C_AL_HL_SONSTIGES']

    def __init__(self, dir, img_map, xml_store, logger):
        self.logger = logger
        self.output_data = []
        self.output_dir = dir
        self.xml_dir = os.path.join(self.output_dir, 'xml')
        self.img_dir = os.path.join(self.output_dir, 'img')
        self.img_map = img_map
        self.xml_store = xml_store
        for subteil in self.ignore_sub_teil:
            setattr(self, "process_%s" % subteil, self._generic)

    def _generic(self, *args, **kwargs):
        pass

    def save_xml(self, dom, dsgnum, imgs=[]):
        idxml_file = os.path.join(self.xml_dir, '%s.xml' % dsgnum)
        sub_output = {}
        sub_output['appnum'] = dsgnum
        sub_output['xml'] = os.path.relpath(idxml_file, self.output_dir)
        sub_output['img'] = imgs
        self.output_data.append(sub_output)

        with codecs.open(idxml_file, 'w', 'utf8') as fh:
            fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
            fh.write(ET.tostring(dom).decode("utf-8"))

    def process_akte(self, akte, status=None):
        """ takes a design and creates a file per model (muster)"""
        appnum = akte.find('C_AKTE_REGISTER_NR').text

        # get the models attached to design
        mlist = akte.find('MUSTER_LISTE')

        # no models attached yet
        if mlist is None or not len(mlist.findall('MUSTER')):
            self.logger.info('%s - no models' % appnum)
            dsgnum = '%s-%s' % (appnum, '1'.zfill(4))
            if mlist is not None:
                akte.remove(mlist)
            self.save_xml(akte, dsgnum)
            return

        musters = mlist.findall('MUSTER')
        akte.remove(mlist)
        # iterate over models and create a document for each
        for muster in musters:
            model_akte = deepcopy(akte)

            musternb = int(muster.find('C_MUSTER_MUSTER_NR').text)
            dsgnum = '%s-%s' % (appnum, str(musternb).zfill(4))

            # find images for model
            imgs = []

            # get images per muster
            anzahl = muster.find('C_MUSTER_ANZAHL_DARSTELLUNGEN')

            # at least one image
            if anzahl is None:
                anzahl = ET.SubElement(muster, 'C_MUSTER_ANZAHL_DARSTELLUNGEN')
                anzahl.text = '1'

            # true nb of reproductions (images)
            _anzahl = ET.SubElement(muster, 'WIPO_MUSTER_ANZAHL_DARSTELLUNGEN')

            img_count = int(anzahl.text)
            img_found = 0
            for i in range(img_count):
                # global
                imgname0 = '%s%s%s%s' % (appnum[2:6],
                                         appnum[-5:],
                                         str(musternb).zfill(3),
                                         str(i + 1).zfill(2))

                imgname1 = '%s%s%s' % (appnum[1:],
                                       str(musternb).zfill(3),
                                       str(i + 1).zfill(2))

                imgname2 = 'n%s%s%s' % (appnum,
                                        str(musternb).zfill(3),
                                        str(i + 1).zfill(2))

                img_match = self.img_map.get(
                    imgname0, self.img_map.get(
                        imgname1, self.img_map.get(
                            imgname2, None))
                )

                if img_match:
                    img_found += 1
                    img_newname = '%s.%s' % (dsgnum, str(i + 1))
                    _, img_ext = os.path.splitext(img_match)
                    img_file = os.path.join(
                        self.img_dir, '%s%s' % (img_newname, img_ext))
                    if os.path.exists(img_match):
                        os.rename(img_match, img_file)
                        img_subpath = os.path.relpath(img_file, self.output_dir)
                        imgs.append(img_subpath)
                    self.logger.info('%s - %s [%s]' % (dsgnum, img_newname, img_match))
                else:
                    self.logger.info('%s - %s' % (dsgnum, ''))

            _anzahl.text = str(img_found)
            model_akte.append(muster)
            self.save_xml(model_akte, dsgnum, imgs=imgs)

    def iter_teil_a(self, teil):
        """ TEIL A : Registrations"""
        aktes = teil.findall('AKTE')
        for akte in aktes:
            status = ET.SubElement(akte, 'WIPO_STATUS')
            status.text = 'Registered'
            self.process_akte(akte)

    def iter_teil_b(self, teil):
        """ TEIL B : Publications"""
        aktes = teil.findall('AKTE')
        for akte in aktes:
            status = ET.SubElement(akte, 'WIPO_STATUS')
            status.text = 'Published'
            self.process_akte(akte)

    def iter_teil_d(self, teil):
        """ TEIL D : renewals"""
        self.logger.info('\n<< iter_teil_d : renewals >>')
        subs = teil.findall('SUBTEIL')
        for sub in subs:
            type = sub.attrib['SubTeil']
            aktes = sub.findall('AKTE')
            for akte in aktes:
                files = self.get_files_toupdate(akte)
                for f in files:
                    self.update_file(f, 'WIPO_GRANT', type)
                    self.update_file(f, 'WIPO_STATUS', 'Renewed')

    def iter_teil_e(self, teil):
        """ TEIL E : inactive designs"""
        self.logger.info('<< iter_teil_e : inactive >>')
        subs = teil.findall('SUBTEIL')
        for sub in subs:
            type = sub.attrib['SubTeil']
            aktes = sub.findall('AKTE')
            for akte in aktes:
                files = self.get_files_toupdate(akte)
                for f in files:
                    self.update_file(f, 'WIPO_STATUS', type)
                    self.logger.info('  ', os.path.basename(f))
                appnum = akte.find('C_AKTE_REGISTER_NR').text
                self.logger.info('%s inactive for %s ' % (appnum, type))

    def iter_teil_f(self, teil):
        """ TEIL F : changes"""
        self.logger.info('<< iter_teil_f : changes >>')
        subs = teil.findall('SUBTEIL')
        for sub in subs:
            type = sub.attrib['SubTeil']
            aktes = sub.findall('AKTE')
            for akte in aktes:
                appnum = akte.find('C_AKTE_REGISTER_NR').text
                self.logger.info('%s change of %s ' % (appnum, type))
                getattr(self, 'process_%s' % type)(akte)

    def process_C_AL_HL_AENDERUNG_INHABER(self, akte):
        """ change of owner """
        newval = akte.find('C_AKTE_ERLAEUTERUNG_ZUR_HL').text
        self.logger.info('  owner: %s' % newval)
        files = self.get_files_toupdate(akte)
        for f in files:
            self.update_file(f, 'C_AKTE_INHABER', newval)
            self.logger.info('  ', os.path.basename(f))

    def process_C_AL_HL_AENDERUNG_ENTWERFER(self, akte):
        """change of designer"""
        musters = akte.find('MUSTER_LISTE').findall('MUSTER')
        for muster in musters:
            nb = muster.find('C_MUSTER_MUSTER_NR').text
            newtag = muster.find('C_AKTE_ERLAEUTERUNG_ZUR_HL')
            newval = '' if newtag is None else newtag.text
            files = self.get_files_toupdate(akte, musters=[nb])
            for file in files:
                dom = md.parse(file)
                try:
                    mdom = dom.getElementsByTagName('MUSTER')[0]
                    xmldom.set_nodevalue('C_AKTE_ERLAEUTERUNG_ZUR_HL',
                                         newval, dom=mdom)
                    xmldom.save_xml(dom, file)
                    self.logger.info('  designer: %s' % newval)
                except Exception as e:
                    self.logger.error('  ERROR: could not set new designer. moving on')

    def process_C_AL_HL_AENDERUNG_VERTRETER(self, akte):
        """change in representative"""
        newval = akte.find('C_AKTE_ERLAEUTERUNG_ZUR_HL').text
        self.logger.info('  representative: %s' % newval)
        files = self.get_files_toupdate(akte)
        for f in files:
            self.update_file(f, 'C_AKTE_VERTRETER', newval)
            self.logger.info('  ', os.path.basename(f))

    def process_C_AL_HL_AENDERUNG_ZUSTELL(self, akte):
        """change in correspondance"""
        newval = akte.find('C_AKTE_ERLAEUTERUNG_ZUR_HL').text
        self.logger.info('  correspondance: %s' % newval)

        files = self.get_files_toupdate(akte)
        for f in files:
            self.update_file(f, 'C_AKTE_ZUSTELL_ANSCHRIFT', newval)
            self.logger.info('  ', os.path.basename(f))

    def process_C_AL_HL_BERICHTIGUNG(self, akte):
        """correction"""
        newval = akte.find('C_AKTE_ERLAEUTERUNG_ZUR_HL').text
        self.logger.info('  correction: %s' % newval)
        files = self.get_files_toupdate(akte)
        for f in files:
            self.update_file(f, 'C_AL_HL_BERICHTIGUNG', newval)
            self.logger.info('  ', os.path.basename(f))

    def update_file(self, f, key, value):
        xmldom.set_nodevalue(key, value, file=f, force=True)

    def get_files_toupdate(self, akte, musters=None):
        appnum = akte.find('C_AKTE_REGISTER_NR').text
        # see what models are affected by this change
        if not musters:
            musters = akte.find('C_AKTE_BETROFFENE_MUSTER_NRN')
            if musters is None:
                musters = ['*']
            else:
                musters = musters.text.split(', ')
        # first try to find file in this extraction
        file_extraction = os.path.join(self.xml_dir, appnum)
        # get the updated file(s) from the store
        file_store = os.path.join(self.xml_store,
                                  appnum[-4:-2], appnum[-2:], appnum)
        files = []
        # first look for files in this extraction
        for muster in musters:
            files += glob.glob('%s-%s.xml' % (
                file_extraction, muster.zfill(4)
                if not muster == '*' else muster))
        # files found in this extraction. return and exit
        if len(files):
            return files
        # then fall back to store
        for muster in musters:
            files += glob.glob('%s-%s.xml.gz' % (
                file_store, muster.zfill(4) if not muster == '*' else muster))
        fouts = []
        for f in files:
            fname = os.path.basename(f)
            fname = fname[0:fname.find('.')]

            fdest = os.path.join(self.xml_dir, '%s.xml' % fname)
            with gzip.open(f, 'rb', 'utf8') as fin, codecs.open(
                    fdest, 'wb', 'utf8') as fout:
                for line in fin.readlines():
                    fout.write(line.decode("utf-8"))
            fouts.append(fdest)
            # need to also move the model images
            highs = glob.glob('%s.*.high.jpg' % os.path.join(
                os.path.dirname(f), fname))
            imgs = []
            for img in highs:
                imgname = os.path.basename(img).replace('.high', '')
                imgout = os.path.join(self.img_dir, imgname)
                shutil.copyfile(img, imgout)

                imgs.append(os.path.relpath(imgout, self.output_dir))
            sub_output = {}
            sub_output['appnum'] = fname
            sub_output['xml'] = os.path.relpath(fdest, self.output_dir)
            sub_output['img'] = imgs
            self.output_data.append(sub_output)
        return fouts
