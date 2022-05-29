from unittest import TestCase, mock

from os.path import dirname, realpath, join
from xpipe.config import load_config, to_yaml, to_dict, load_config_from_str
import numpy as np
import yaml

class TestConfiguration(TestCase):

    def setUp(self):
        dir_path = dirname(realpath(__file__))
        self.conf = load_config(join(dir_path, "./resources/template.yaml"))


    def test_eq(self):
        self.assertEqual(self.conf, self.conf)
        self.assertEqual(self.conf.training, self.conf.training)
        self.assertNotEqual(self.conf, self.conf.training)


    def test_get_integer(self):
        self.assertEqual(
            self.conf.training.batch_size(), 
            10
        )


    def test_get_list(self):
        l = self.conf.training.classes()
        self.assertIsInstance(l, list)
        self.assertListEqual(l, [0,1,2,3,4])

    # ---------- Test objects ----------
    
    def test_instantiate_object(self):
        ar = self.conf.obj_test()
        self.assertIsInstance(ar, np.ndarray)
        self.assertListEqual(list(ar), [1,2])


    def test_get_object_parameter(self):
        self.assertListEqual(
            self.conf.obj_test._params.object(), 
            [1, 2]
        )


    def test_instantiate_list_objects(self):
        objects_list = self.conf.data.transforms()
        self.assertListEqual(list(objects_list[0]), [1, 2])
        self.assertListEqual(list(objects_list[1]), [2, 3])
        self.assertEqual(len(objects_list), 4)
    
    # ---------- Test includes ----------

    def test_include(self):
        a = self.conf.inc.a()
        self.assertEqual(a, 1)
        self.assertTrue(len(self.conf.inc.user()))
        self.assertListEqual(self.conf.inc.inc.object(), [1,2,3,4])
        
    
    def test_include_obj(self):
        a = self.conf.obj_include()
        self.assertListEqual(list(a), [1,2,3,4])


    def test_double_star(self):
        def test(batch_size, lr, classes, **kwargs):
            self.assertEqual(batch_size(), 10)
            self.assertEqual(lr(), 0.01)
        a = self.conf.training
        test(**a)


    def test_env_var(self):
        a = self.conf.user()
        self.assertTrue(len(a))
    

    def test_str_fmt(self):
        a = self.conf.str_fmt()
        self.assertTrue(len(a))
    

    def test_class(self):
        c = self.conf.np_array()
        self.assertEqual(c, np.array)
    
    # ---------- test references ----------

    def test_ref(self):
        a = self.conf.test_ref()
        self.assertEqual(a, self.conf.training.batch_size())
    

    def test_ref_relative(self):
        a = self.conf.ref_relative.ref_relative1.ref_relative2.value()
        value = self.conf.ref_relative.value()
        self.assertEqual(a, value)
    

    def test_ref_attr(self):
        a = self.conf.ref_attr.conf_a()
        value = self.conf.obj_config._params.conf.a()
        self.assertEqual(a, value)

    def test_ref_in_include_to_include(self):
        a = self.conf.include.ref_to_inc()
        value = self.conf.include.inc.object()
        np.testing.assert_almost_equal(a, value)


    def test_included_ref(self):
        ref = self.conf.include.ref()
        self.assertEqual(ref, self.conf.include.user())
    

    def test_yaml(self):
        yaml = to_yaml(self.conf)
        conf = load_config_from_str(yaml)
        self.assertEqual(self.conf.training, conf.training)
        self.assertEqual(self.conf.data, conf.data)
    
    
    def test_dict(self):
        d = to_dict(self.conf)
        y = yaml.dump(d["training"])
        conf = load_config_from_str(y)
        d2 = to_dict(conf)
        self.assertEqual(d["training"], d2)