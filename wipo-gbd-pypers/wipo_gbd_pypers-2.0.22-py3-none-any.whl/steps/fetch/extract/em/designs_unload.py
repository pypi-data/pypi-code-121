import os
import xmltodict
import codecs
import xml.dom.minidom as md
from pymongo import MongoClient
from pypers.steps.base.extract_step import ExtractStep


class DesignUnload(ExtractStep):
    """
    Unload EMID Documents from DB
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
                    "name": "archive_name",
                    "descr": "the name of the archive that has been extracted",
                    "iterable": True
                }
            ],
            "params": [
                {
                    "name": "dburl",
                    "descr": "the url of the database to unload xml from",
                    "value": 'mongodb://localhost:27017/'
                },
                {
                    "name": "dbname",
                    "descr": "the name of the database to unload xml from"
                },
                {
                    "name": "commons",
                    "descr": "the name of the commons collection",
                    "value": 'commons'
                }
            ]
        }
    }

    def get_raw_data(self):
        return None

    def process_xml_data(self, _):
        if len(self.archive_name) == 0:
            return 0, 0
        docsdb = MongoClient(self.dburl)[self.dbname]
        commons = getattr(MongoClient(self.dburl), self.commons)

        coll = self.meta['pipeline']['collection']
        run_id = self.meta['pipeline']['run_id']

        extraction_data = []

        # extract in a directory having the same name as the archive
        dest_dir = os.path.join(self.output_dir, self.archive_name)
        os.makedirs(dest_dir)

        unloaded = {}
        # ------------------------------------------
        # 1: find all documents inserted in this run
        # ------------------------------------------
        docs = docsdb.get_collection(coll).find(
            {'run_id': run_id, 'archive': self.archive_name},
            {'_id': 0, 'run_id': 0, 'archive': 0})

        self.logger.info('found %s designs for run [%s] and archive [%s]' % (
            docs.count(), run_id, self.archive_name))

        # expand applicant and representatives
        for doc in docs:
            self.expand(commons.get_collection('emap'), 'applicant', doc)
            self.expand(commons.get_collection('emrp'), 'representative', doc)

            # transform to xml and write the file
            dsgnum = doc.pop('uid')
            unloaded[dsgnum] = 1
            xml_file = os.path.join(dest_dir, '%s.xml' % dsgnum)

            with codecs.open(xml_file, 'w', 'utf-8') as fh:
                xml_str = md.parseString(xmltodict.unparse(doc)).toprettyxml()
                fh.write(xml_str)

            sub_output = {}
            sub_output['appnum'] = dsgnum
            sub_output['xml'] = os.path.relpath(xml_file, dest_dir)
            extraction_data.append(sub_output)

        to_unload = {}
        # ------------------------------------------
        # 2: find all applicants updated in this run
        # ------------------------------------------
        applicants = commons.get_collection('emap').find(
            {'run_id': run_id},
            {'_id': 0, 'run_id': 0, 'archive': 0})
        for applicant in applicants:
            ap_uid = applicant['Applicant']['ApplicantIdentifier']
            ap_designs = commons.get_collection('emap-map').find_one(
                {'applicant': ap_uid}, {'designs': 1})
            for dsg_uid in (ap_designs or {}).get('designs', []):
                self.logger.info('applicant %s - design %s' % (ap_uid, dsg_uid))
                if unloaded.get(dsg_uid, None) is None:
                    to_unload[dsg_uid] = 1
        # -----------------------------------------------
        # 3: find all representatives updated in this run
        # -----------------------------------------------
        representatives = commons.get_collection('emrp').find(
            {'run_id': run_id}, {'_id': 0, 'run_id': 0, 'archive': 0})

        for representative in representatives:
            rp_uid = representative[
                'Representative']['RepresentativeIdentifier']
            rp_designs = commons.get_collection('emrp-map').find_one({
                'representative': rp_uid}, {'designs': 1})
            for dsg_uid in (rp_designs or {}).get('designs', []):
                self.logger.info('representative %s - design %s' % (
                    rp_uid, dsg_uid))
                if unloaded.get(dsg_uid, None) is None:
                    to_unload[dsg_uid] = 1
        # --------------------------------------------------------
        # 4: unload modified designs by applicants/representatives
        # --------------------------------------------------------
        for uid in to_unload.keys():
            docs = docsdb.get_collection(coll).find(
                {'uid': uid},
                {'_id': 0, 'run_id': 0, 'archive': 0}, limit=1).sort(
                [('run_id', -1), ('archive', -1)])

            for doc in docs:
                if doc['Design']['@operationCode'] == 'Delete':
                    # no point in updating a deleted document
                    continue

                self.expand(commons.get_collection('emap'),
                            'applicant', doc)
                self.expand(commons.get_collection('emrp'),
                            'representative', doc)

                # transform to xml and write the file
                dsgnum = doc.pop('uid')

                unloaded[dsgnum] = 1
                xml_file = os.path.join(dest_dir, '%s.xml' % dsgnum)

                with codecs.open(xml_file, 'w', 'utf-8') as fh:
                    xml_str = md.parseString(
                        xmltodict.unparse(doc)).toprettyxml()
                    fh.write(xml_str)

                sub_output = {}
                sub_output['appnum'] = dsgnum
                sub_output['xml'] = os.path.relpath(xml_file, dest_dir)
                extraction_data.append(sub_output)
        self.output_data = [extraction_data]
        self.dest_dir = [dest_dir]
        self.archive_name = [self.archive_name]
        docsdb.client.close()
        commons.client.close()
        return len(extraction_data), 0

    def expand(self, coll, type, doc):

        _skip_fields = {'_id': 0, 'run_id': 0, 'uid': 0, 'archive': 0}

        objs2expand = doc['Design'].get(
            '%sDetails' % type.capitalize(), {}).get(type.capitalize(), [])

        # if only one found => transform to a list of one
        if isinstance(objs2expand, dict):
            objs2expand = [objs2expand]

        expanded = []
        for obj2expand in objs2expand:
            ident = obj2expand['%sIdentifier' % type.capitalize()]
            details = coll.find({'uid': ident}, _skip_fields, limit=1) \
                          .sort([('run_id', -1), ('archive', -1)])

            for detail in details:
                expanded.append(detail[type.capitalize()])

            doc['Design']['%sDetails' % type.capitalize()] = {
                type.capitalize(): expanded}
