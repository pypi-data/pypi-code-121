import unittest
from pypers.pipelines import dir, load_pipelines
import os
import json


class TestSchedulerInit(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(dir, 'good_test.json'), 'w') as f:
            f.write(json.dumps({
                'name': 'toto',
                'label': 'pipeline'
            }))

    def tearDown(self):
        os.remove(os.path.join(dir, 'good_test.json'))
        if os.path.exists(os.path.join(dir, 'bad_test.json')):
            os.remove(os.path.join(dir, 'bad_test.json'))

    def test_load_files(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.assertTrue(os.path.exists(os.path.join(dir, 'good_test.json')))
        pipeline_names, pipeline_specs, pipelines = load_pipelines()
        self.assertTrue(pipeline_names.get('toto', None) is not None)

    def test_load_with_errors(self):
        if os.environ.get('SHORT_TEST', None):
            return
        with open(os.path.join(dir, 'bad_test.json'), 'w') as f:
            f.write(json.dumps({
                'label': 'pipeline'
            }))
        try:
            _, _, _ = load_pipelines()
            self.fail("should fail with KeyError because of hte name")
        except KeyError as e:
            self.assertEqual(str(e), "'name not found in %s'" %
                             os.path.join(dir, 'bad_test.json'))
        with open(os.path.join(dir, 'bad_test.json'), 'w') as f:
            f.write(json.dumps({
                'name': 'toto',
            }))
        try:
            _, _, _ = load_pipelines()
            self.fail("should fail with KeyError because of hte label")
        except KeyError as e:
            self.assertEqual(str(e), "'label not found in %s'" %
                             os.path.join(dir, 'bad_test.json'))
        with open(os.path.join(dir, 'bad_test.json'), 'w') as f:
            f.write("test")
        try:
            _, _, _ = load_pipelines()
            self.fail("should fail with KeyError because of hte label")
        except ValueError as e:
            pass


if __name__ == "__main__":
    unittest.main()
