from pymongo import MongoClient
from pypers.steps.fetch import common


# extends the common load
class DesignLoad(common.Load):

    # runs after loading into db
    def postprocess(self):
        docsdb = MongoClient(self.dburl)[self.dbname]
        commons = getattr(MongoClient(self.dburl), self.commons)

        coll = self.meta['pipeline']['collection']
        run_id = self.meta['pipeline']['run_id']

        # find the docs added for this run and for this archive
        new_docs = docsdb.get_collection(coll).find(
            {'run_id': run_id, 'archive': self.archive_name[0]},
            {'_id': 0, 'uid': 1, 'Design.ApplicantDetails': 1,
             'Design.RepresentativeDetails': 1})

        # for every doc, map applicants and representatives
        for new_doc in new_docs:
            self.mapdocs(commons.get_collection('emap-map'), 'applicant',
                         new_doc)
            self.mapdocs(commons.get_collection('emrp-map'), 'representative',
                         new_doc)

        docsdb.client.close()
        commons.client.close()

    # maps applicants and representatives into designs
    def mapdocs(self, collection, type, doc):

        dsgnum = doc['uid']
        objs2map = doc['Design'].get('%sDetails' % type.capitalize(), {}) \
                                .get(type.capitalize(), [])

        # if only one found => transform to a list of one
        if isinstance(objs2map, dict):
            objs2map = [objs2map]

        for obj2map in objs2map:
            ident = obj2map['%sIdentifier' % type.capitalize()]
            query = {}
            typemap = collection.find_one({type: ident})

            if typemap is None:
                collection.insert_one({type: ident, 'designs': [dsgnum]})
            else:
                # check if mapping already done
                try:
                    typemap['designs'].index(dsgnum)
                # create the map
                except Exception as e:
                    collection.update({type: ident},
                                      {'$push': {'designs': dsgnum}})

