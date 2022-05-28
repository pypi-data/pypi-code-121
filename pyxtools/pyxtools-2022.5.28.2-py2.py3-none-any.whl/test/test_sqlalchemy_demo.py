# -*- coding:utf-8 -*-
from __future__ import absolute_import

import os
import unittest

import numpy as np

from pyxtools.tmp_tools.sqlalchemy_demo import FeatureRecord, get_sqlite_engine, get_sqlite_session


class TestSqlAlchemy(unittest.TestCase):
    def setUp(self):
        self.file = "./tmp.dat"
        FeatureRecord.sqlite_file = self.file
        FeatureRecord.init_table_object()

    def tearDown(self):
        if os.path.exists(self.file):
            os.remove(self.file)

    def testClose(self):
        engine = get_sqlite_engine(sqlite_file=self.file)
        db_session = get_sqlite_session(engine=engine)
        self.assertEqual(id(db_session.bind), id(engine))

    def testInfo(self):
        db_session = FeatureRecord.get_session()
        train, test = FeatureRecord.get_info(db_session)
        self.assertTrue(isinstance(train, int))
        self.assertTrue(isinstance(test, int))
        db_session.close()

    def testAdd(self):
        db_session = FeatureRecord.get_session()

        train, test = FeatureRecord.get_info(db_session)
        count = train + test

        # train data
        for index, label in enumerate([1, -1]):
            feature = np.random.random((1, 1024))
            instance = FeatureRecord.add_feature(db_session=db_session, image_id="a.jpg", label=label,
                                                 feature=feature)

            train, test = FeatureRecord.get_info(db_session)
            print("train is {}, test is {}, count is {}".format(train, test, count))
            # self.assertTrue((count + 1) == (train + test))
            count = train + test

            result_list = FeatureRecord.list_feature(db_session=db_session, uid_list=[instance.id])
            self.assertTrue(len(result_list) == 1)
            (obj_id, obj_image_id, obj_label, obj_feature) = result_list[0]
            self.assertTrue(obj_id == instance.id)
            self.assertTrue(obj_image_id == instance.image_id)
            self.assertTrue(obj_label == instance.label)
            self.assertTrue(type(obj_feature) == type(feature))
            self.assertTrue(np.sum(obj_feature) == np.sum(feature))

        db_session.close()
