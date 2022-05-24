import os
import sys
from importlib import reload
import xmltodict
import codecs
import gzip
import shutil
import xml.dom.minidom as md
from pymongo import MongoClient
from pypers.steps.base.step_generic import EmptyStep


class FullUnload(EmptyStep):
    """
    Unload FULL EMID Documents from DB
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "outputs": [
                {
                    "name": "dest_dir",
                    "descr": "the destination dir of the extraction"
                }
            ],
            "params": [
                {
                    "name": "dburl",
                    "descr": "the url of the database to load xml into",
                    "value": 'mongodb://localhost:27017/'
                },
                {
                    "name": "dbname",
                    "descr": "the name of the database to load xml into"
                },
                {
                    "name": "commons",
                    "descr": "the name of the commons collection",
                    "value": 'commons'
                }
            ]
        }
    }

    def process(self):

        docsdb = MongoClient(self.dburl)[self.dbname]
        commons = getattr(MongoClient(self.dburl), self.commons)

        coll = 'emid'
        # extract in a directory having the same name as the archive
        dest_dir = os.path.join(self.output_dir, 'full')
        os.makedirs(dest_dir)

        unloaded = {}

        # ------------------------------------------
        # 1: find all documents inserted in this run
        # ------------------------------------------
        count = docsdb.get_collection(coll).count()
        offset = 0
        limit = 1000

        while(offset + limit < count):
            self.logger.info('%s -> %s / %s' % (offset, offset + limit, count))
            print('%s -> %s / %s' % (offset, offset + limit, count))
            offset += limit

            docs = docsdb.get_collection(coll).find({}, {'_id': 0}).sort(
                    [('uid', 1), ('archive', -1), ('run_id', -1)]
            ).skip(offset).limit(limit)

            # expand applicant and representatives
            for doc in docs:
                dsgnum, run_id, archive = (doc.pop('uid'),
                                           doc.pop('run_id'),
                                           doc.pop('archive'))
                if dsgnum in unloaded.keys():
                    self.logger.info('OBSOLETE: %s\t%s\t%s' % (
                        dsgnum, run_id, archive))
                    continue
                unloaded[dsgnum] = 1

                self.expand(commons.get_collection('emap'),
                            'applicant', doc)
                self.expand(commons.get_collection('emrp'),
                            'representative', doc)

                # transform to xml and write the file
                dsgnum_padded = dsgnum[0:dsgnum.find('-')].zfill(4)
                xml_path = os.path.join(dest_dir, dsgnum_padded[-4:-2],
                                        dsgnum_padded[-2:])
                if not os.path.exists(xml_path):
                    os.makedirs(xml_path)

                xml_file = os.path.join(xml_path, '%s.xml' % dsgnum)
                with codecs.open(xml_file, 'w', 'utf-8') as fh:
                    xml_str = md.parseString(
                        xmltodict.unparse(doc)).toprettyxml()
                    fh.write(xml_str)

                # gzip the xml
                with open(xml_file, 'rb') as f_in,\
                        gzip.open('%s.gz' % xml_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                os.remove(xml_file)

        self.dest_dir = [dest_dir]
        docsdb.client.close()
        commons.client.close()

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
                          .sort([('run_id', -1),('archive', -1)])
            for detail in details:
                expanded.append(detail[type.capitalize()])
            doc['Design']['%sDetails' % type.capitalize()] = {
                type.capitalize(): expanded}
