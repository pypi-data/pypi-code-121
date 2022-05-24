import unittest
from pypers.core.step import Step, FunctionStep
from pypers.core.constants import JOB_STATUS
import os
import shutil
import json
from datetime import datetime
from pypers.core.interfaces.db.base import DbBase
from pypers.core.interfaces.db.test import MockDBLogger
from mock import patch, MagicMock
from pypers.core.interfaces.msgbus.base import MSGBase


class MockDB(DbBase):

    def update(self, cfg):
        self.cfg = cfg

    def params(self, name, value):
        setattr(self, name, value)

    def get_pipeline_config(self, *args, **kwargs):
        return {}
    
    def create_pypers_config_schema(self):
        return

    def get_step_config(self, *args, **kwargs):
        return self.cfg

    def has_step_config_changed(self, *args, **kwargs):
        return self.step_changed

    def create_step_config(self, *args, **kwargs):
        return

    def has_step_run(self, *args, **kwargs):
        return self.step_run

    def get_run_id_config(self, *args, **kwargs):
        return self.run_config

    def set_step_output(self, *args, **kwargs):
        return args[3]


class MockSQS(MSGBase):
    counter = 0

    def get_pypers_queue(self):
        pass

    def reset_history(self, runid, collection):
        pass

    def send_message(self, runid, collection=None, step=None, index=None,
                     custom_config=None, restart=False):
        self.counter += 1

    def get_messges(self):
        return None, None

    def delete_message(self, message_id):
        pass


mockde_db = MockDB()
mocked_msg = MockSQS()


def mock_db(*args, **kwargs):
    return mockde_db


def mock_sqs(*args, **kwargs):
    return mocked_msg


mocked_logger = MockDBLogger()


def mock_logger(*args, **kwargs):
    return mocked_logger


class MockStep(Step):
    spec = {
        "version": "1.0.1",
        'url': "www.wipo.int",
        "args": {
            "inputs": [{
                'name': 'toto',
                'value': 'foo/test.xml',
                "iterable": True
            },
                {
                    'name': 'toto2',
                    'value': 'foo2',
                    "iterable": False
                }
            ],
            "outputs": [{
                'name': 'titi',
                'value': 'fuuu'
            }, {
                'name': 'test1',
                'value': '{{output_dir}}'
            }, {
                'name': 'test3',
                'type': 'file',
                'value': '{{param3}}'
            }, {
                'name': 'param3',
                'type': 'file',
                'value': 'foo/bar/test.txt'
            }, {
                'name': 'test4',
                'type': 'file',
                'value': 'foo/bar/*.txt'
            }, {
                'name': 'test2',
                'value': '{{param2}}'
            }, {
                'name': 'param2',
                'value': ['foo', 'bar']
            }
            ],
            "params": [{
                'name': 'google',
                'type': 'int'
            }]
        },
        "requirements": {
            "cpu_foo": '1'
        },
        'local': True
    }

    req_spec = {
        'cpu_foo': {
            'name': 'cpu_foo',
            'descr': '1',
            'type': 'int',
            'value': 1,
        }
    }


class MockStep2(Step):
    spec = {
        "version": "1.0.1",
        "args": {
            "inputs": [{
                'name': 'toto',
                'value': 'foo',
                "iterable": False
            },
                {
                    'name': 'toto2',
                    'value': 'foo2',
                    "iterable": False
                }
            ],
            "outputs": [
                {
                    'name': 'out_result',
                    'value': 'a value'
                }
            ],
        },
        'local': True
    }

    def preprocess(self):
        pass

    def process(self):
        pass

    def postprocess(self):
        pass


class MockFunctionStep(FunctionStep):
    spec = {
        "version": "1.0.1",
        "args": {
            "inputs": [{
                'name': 'toto',
                'value': 'foo',
                "iterable": False
            }],
            "outputs": [
                {
                    'name': 'out_result',
                    'value': 'a value'
                }
            ],
        },
    }

    def preprocess(self):
        pass

    def process(self):
        pass

    def postprocess(self):
        pass


class StreamMock:
    def __init__(self):
        pass

    def close(self):
        pass


class PopenMockObj:

    should_fail = False

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.stdout = StreamMock()
        self.stderr = StreamMock()
        self.returncode = 0

    def communicate(self):
        return "%s" % self.args, "%s" % self.kwargs


class TestStep(unittest.TestCase):

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.path = os.path.dirname(__file__)
        self.step = MockStep('test', 'test', 'step')
        self.step.output_dir = 'foo'
        self.path_test = 'foo'
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)

    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_new_step(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Empty step
        s = Step('test', 'test', 'step')
        self.assertEqual(s.name, 'step')
        self.assertEqual(s.__version__, None)
        # Mock step
        self.assertEqual(self.step.name, 'test_step')
        self.assertEqual(self.step.__version__, '1.0.1')
        self.assertEqual(self.step.toto, 'foo/test.xml')
        self.assertEqual(self.step.titi, 'fuuu')

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_get_reqs(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Get Non Defaults
        reqs = self.step.get_reqs()
        self.assertEqual(reqs, [])
        # Get with Defaults
        reqs = self.step.get_reqs(no_default=False)
        self.assertEqual(len(reqs), 1)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test__key_groups(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # test with a wrong type
        try:
            self.step.keys_values(key_groups={'foo_bar': 'root'})
            self.fail("Should rise an exeception")
        except Exception as e:
            self.assertEqual(str(e), "Invalid key_groups type <class 'dict'>")
        # test with wrong list or set
        try:
            self.step.keys_values(key_groups={'root'})
            self.fail("Should rise an exeception")
        except Exception as e:
            self.assertEqual(str(e),
                             "test_step: Invalid key_groups {'root'}")
        # Test with wrong string
        try:
            self.step.keys_values(key_groups='root')
            self.fail("Should rise an exeception")
        except Exception as e:
            self.assertEqual(str(e), "Invalid key_groups root")

        # test with a string
        res = self.step.keys_values(key_groups='inputs')
        self.assertEqual(res, {'toto': 'foo/test.xml', 'toto2': 'foo2'})
        # test with a list
        res = self.step.keys_values(key_groups=['inputs'])
        self.assertEqual(res, {'toto': 'foo/test.xml', 'toto2': 'foo2'})

        res = self.step.keys_values(key_filter={'name': 'toto'})
        self.assertEqual(res['toto'], 'foo/test.xml')

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_keys(self):
        if os.environ.get('SHORT_TEST', None):
            return
        res = self.step.keys(key_groups='inputs')
        self.assertEqual(res, ['toto', 'toto2'])
        res = self.step.keys(key_filter={'name': 'toto'})
        self.assertEqual(res, ['toto'])

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_key_pec(self):
        if os.environ.get('SHORT_TEST', None):
            return
        res = self.step.key_spec('toto')
        self.assertEqual(
            res, {'iterable': True, 'name': 'toto', 'value': 'foo/test.xml'})

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_validate_value(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.assertEqual(Step.validate_value('', 'str', ''), '')
        self.assertEqual(Step.validate_value('', 'int', ''),
                         'missing value')
        self.assertEqual(Step.validate_value(1.0, 'float', ''), '')
        self.assertEqual(
            Step.validate_value(1, 'float', ''),
            "1 : invalid type, found <class 'int'>, expected float")
        self.assertEqual(Step.validate_value(1, 'int', ''), '')
        self.assertEqual(
            Step.validate_value(1.0, 'int', ''),
            "1.0 : invalid type, found <class 'float'>, expected int")
        self.assertEqual(
            Step.validate_value(__file__, 'file', ''), '')
        self.assertEqual(
            Step.validate_value('toto', 'file', ''), 'toto : no such file')
        self.assertEqual(
            Step.validate_value([__file__, 'toto'], 'file', ''),
            'toto : no such file\n')
        self.assertEqual(
            Step.validate_value({'foo': 'bar'}, 'file', ''),
            "{'foo': 'bar'} : invalid type, found <class 'dict'>, "
            "expected str or list")
        self.assertEqual(
            Step.validate_value(self.path, 'dir', ''), '')
        self.assertEqual(
            Step.validate_value('fuu', 'dir', ''), 'fuu : no such directory')
        self.assertEqual(
            Step.validate_value(
                os.path.join(self.path, 'folders.txt'), 'dir', ''),
            'fuu : no such directorybar : no such directory')
        self.assertEqual(
            Step.validate_value(['fuu'], 'dir', ''), 'fuu : no such directory')
        self.assertEqual(
            Step.validate_value([['fuu']], 'dir', ''),
            "['fuu'] : invalid type, found <class 'list'>, expected str")
        self.assertEqual(
            Step.validate_value({'fuu': 'bar'}, 'dir', ''),
            "{'fuu': 'bar'} : invalid type, found <class 'dict'>, "
            "expected str or list")

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_validate_config(self):
        if os.environ.get('SHORT_TEST', None):
            return
        cfg = {
            'toto': 'google'
        }
        res = self.step.validate_config(cfg)
        self.assertEqual(res, {'google': 'missing value'})
        cfg = {
            'google': 1.0
        }
        res = self.step.validate_config(cfg)
        self.assertEqual(res, {
            'google': "1.0 : invalid type, found <class 'float'>, "
                      "expected int"})

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_store_outputs(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.assertEqual(self.step.output_dir, self.path_test)
        res = self.step.store_outputs()

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_get_iterables(self):
        if os.environ.get('SHORT_TEST', None):
            return
        iterables = self.step.get_iterables()
        self.assertEqual(iterables, ['toto'])

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_load_cfg(self):
        if os.environ.get('SHORT_TEST', None):
            return
        cfg = {
            'name': 'config',
            'google': 1.0,
            'output_dir': self.path_test
        }
        res = Step.load_cfg(cfg)
        self.assertEqual(res, cfg)
        with open(os.path.join(self.path_test, 'config.cfg'), 'w') as f:
            f.write(json.dumps(cfg))
        res = Step.load_cfg(os.path.join(self.path_test, 'config.cfg'))
        self.assertEqual(res, cfg)
        with open(os.path.join(self.path_test, 'config.cfg'), 'r') as f:
            try:
                res = Step.load_cfg(f)
                self.fail()
            except Exception as e:
                pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_import_class(self):
        if os.environ.get('SHORT_TEST', None):
            return
        imported_class = Step.import_class(
            'pypers.core.test.test_step.MockStep')
        self.assertEqual(type(imported_class('test', 'test', 'step')), MockStep)
        imported_class = Step.import_class('fetch.common.cleanup.Cleanup')
        self.assertEqual(imported_class.__name__, 'Cleanup')

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_create(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.assertEqual(type(Step.create(MockStep)), MockStep)
        self.assertEqual(
            type(Step.create('pypers.core.test.test_step.MockStep')), MockStep)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_load_step(self):
        cfg = {
            'name_value': 'MockStep',
            'cpu_foo': '12',
            'version': 1.0,
            'output_dir': self.path_test
        }
        try:
            mockde_db.update(cfg)
            Step.load_step('test', 'test', 'step')
            self.fail("No step class is define")
        except Exception as e:
            self.assertEqual('Unable to load step class  ', str(e))
        cfg['step_class'] = 'pypers.core.test.test_step.MockStep'
        cfg['sys_path'] = os.getcwd()
        mockde_db.update(cfg)
        res = Step.load_step('test', 'test', 'step')
        self.assertEqual(type(res), MockStep)
        self.assertEqual(res.name, 'MockStep')
        self.assertEqual(res.cpu_foo, 12)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_configure_params(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.step.configure_params()
        self.assertEqual(self.step.test1, self.path_test)
        self.assertEqual(self.step.test2, 'foo')
        self.assertEqual(self.step.test3, 'test')

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_set_outputs(self):
        if os.environ.get('SHORT_TEST', None):
            return
        os.makedirs(os.path.join(self.path_test, 'bar'))
        with open(os.path.join(self.path_test, 'bar', 'test.txt'), 'w') as f:
            f.write('toto')
        self.step.output_dir = os.path.abspath(os.path.dirname(self.path_test))
        self.step.configure_params()
        self.assertEqual(self.step.test1, self.step.output_dir)
        self.step.test3 = os.path.join(self.path_test, 'bar', 'test.txt')
        self.step.set_outputs()
        self.assertEqual(self.step.test1, [self.step.output_dir])
        self.assertEqual(self.step.test2, ['foo'])
        self.assertEqual(self.step.test4, [os.path.abspath(
            os.path.dirname(self.path_test)) + '/foo/bar/test.txt'])

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_set_outputs_exception1(self):
        if os.environ.get('SHORT_TEST', None):
            return
        os.makedirs(os.path.join(self.path_test, 'bar'))
        with open(os.path.join(self.path_test, 'bar', 'test.txt'), 'w') as f:
            f.write('toto')
        self.step.test3 = os.path.join(self.path_test, 'bar', 'test.txt')
        self.step.output_dir = os.path.abspath(os.path.dirname(self.path_test))
        self.step.test4 = 'foo/*.txt'
        self.step.configure_params()
        try:
            self.step.set_outputs()
            self.fail("Exception should have been trigger")
        except Exception as e:
            self.assertEqual(
                'test4 error: reg ex foo/*.txt does not match any file in '
                'the output directory', str(e))
        self.step.test4 = 'foo/toto.txt'
        try:
            self.step.set_outputs()
            self.fail("Exception should have been trigger")
        except Exception as e:
            self.assertEqual('File not found: foo/toto.txt', str(e))

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_set_status(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.step.set_status(JOB_STATUS.RUNNING)
        self.assertEqual(self.step.status, JOB_STATUS.RUNNING)
        self.assertTrue(datetime.utcnow() > self.step.running_at)
        self.step.set_status(JOB_STATUS.SUCCEEDED)
        self.assertEqual(self.step.status, JOB_STATUS.SUCCEEDED)
        self.assertTrue(datetime.utcnow() > self.step.completed_at)
        self.step.set_status(JOB_STATUS.FAILED)
        self.assertEqual(self.step.status, JOB_STATUS.FAILED)
        self.assertTrue(datetime.utcnow() > self.step.completed_at)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_submit_job(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.step.output_dir = os.path.abspath(self.path_test)
        cfg = {
            'name': 'config',
            'google': 1.0,
            'output_dir': os.path.abspath(self.path_test),
            'step_class': 'pypers.core.test.test_step.MockStep',
        }
        mockde_db.update(cfg)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        self.step.submit_job(cfg)
        cfg['output_dir'] = os.path.abspath(self.path_test)
        self.assertEqual(len(self.step.jobs), 1)
        self.step.submit_job(cfg)
        self.assertEqual(len(self.step.jobs), 2)
        # Create a pickle job
        job = Step.load_step('test', 'test', 'step')
        job.status = JOB_STATUS.SUCCEEDED
        os.makedirs(os.path.join(self.path_test, '2'))
        cfg['output_dir'] = os.path.join(os.path.abspath(self.path_test))
        self.step.submit_job(cfg)
        self.assertEqual(len(self.step.jobs), 3)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_get_url(self):
        if os.environ.get('SHORT_TEST', None):
            return
        self.assertEqual(self.step.get_url(), 'http://www.wipo.int')


class TestStepDistribute(unittest.TestCase):

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.path = os.path.dirname(__file__)
        self.path_test = 'foo'
        self.step = MockStep('test', 'test', 'step')
        self.step.output_dir = 'foo'
        self.step.output_dir = os.path.abspath(self.path_test)
        try:
            shutil.rmtree('foo/')
        except Exception as e:
            pass
        os.makedirs(self.path_test)

    def tearDown(self):
        try:
            shutil.rmtree('foo/')
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_distribute(self):
        if os.environ.get('SHORT_TEST', None):
            return
        with open(os.path.join(self.path_test, 'test.xml'), 'w') as f:
            f.write("test value")
        cfg = {
            'name': 'config',
            'google': 1.0,
            'output_dir': os.path.abspath(self.path_test),
            'step_class': 'pypers.core.test.test_step.MockStep',
            'toto': 'foo/test.xml',
            'meta': {
                'pipeline': [],
                'step': [],
                'job': {
                    'toto': ['1']
                }
            }
        }
        mockde_db.update(cfg)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        self.step.cfg = cfg
        res = self.step.distribute()
        self.assertEqual(res, 1)
        res = self.step.distribute()
        self.assertEqual(res, 2)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_distribute2(self):
        if os.environ.get('SHORT_TEST', None):
            return
        step = MockStep2('test', 'test', 'step')
        step.output_dir = 'foo'
        step.output_dir = os.path.abspath(self.path_test)
        with open(os.path.join(self.path_test, 'test.xml'), 'w') as f:
            f.write("test value")
        cfg = {
            'name': 'config',
            'google': 1.0,
            'output_dir': os.path.abspath(self.path_test),
            'step_class': 'pypers.core.test.test_step.MockStep2',
            'toto': 'foo/test.xml',
            'meta': {
                'pipeline': [],
                'step': [],
                'job': {
                    'toto': ['1']
                }
            }
        }
        step.cfg = cfg
        mockde_db.update(cfg)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        res = step.distribute()
        self.assertEqual(res, 1)

        # Test with pickle with no success
        step = MockStep2('test', 'test', 'step')
        step.output_dir = 'foo'
        step.output_dir = os.path.abspath(self.path_test)
        run_conifg = {
            'steps_config': {
                'step': {
                    'sub_steps': {
                        '0': {
                            'output': {
                                'results': {
                                },
                                'status': None
                            }
                        }
                    },
                    'output': {
                        'results': {},
                        'status': None
                    }
                }
            }
        }
        mockde_db.params('run_config', run_conifg)
        mockde_db.params('step_run', True)
        step.cfg = cfg
        res = step.distribute()
        self.assertEqual(res, 1)
        # Test with pickle with success
        step = MockStep2('test', 'test', 'step')
        step.output_dir = 'foo'
        step.output_dir = os.path.abspath(self.path_test)
        step.set_status(JOB_STATUS.SUCCEEDED)
        run_conifg = {
            'steps_config': {
                'step': {
                    'sub_steps': {
                        '0': {
                            'output': {
                                'results': {
                                },
                                'status': JOB_STATUS.SUCCEEDED
                            }
                        }
                    },
                    'output': {
                        'results': {
                        },
                        'status': JOB_STATUS.SUCCEEDED
                    }
                }
            }
        }
        mockde_db.params('run_config', run_conifg)
        mockde_db.params('step_run', True)
        step.cfg = cfg
        mockde_db.update(cfg)
        mockde_db.params('step_changed', False)
        res = step.distribute()
        self.assertEqual(res, 0)

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_get_status(self):
        if os.environ.get('SHORT_TEST', None):
            return
        for s in [JOB_STATUS.FAILED, JOB_STATUS.INTERRUPTED,
                  JOB_STATUS.RUNNING]:
            step = MockStep2('test', 'test', 'step')
            step.output_dir = 'foo'
            step.output_dir = os.path.abspath(self.path_test)
            cfg = {
                'name': 'config',
                'google': 1.0,
                'output_dir': os.path.abspath(self.path_test),
                'step_class': 'pypers.core.test.test_step.MockStep2',
                'toto': 'foo/test.xml',
                'meta': {
                    'pipeline': [],
                    'step': [],
                    'job': {
                        'toto': ['0']
                    }
                }
            }
            mockde_db.update(cfg)
            mockde_db.params('step_changed', False)
            mockde_db.params('step_run', False)
            step.cfg = cfg
            step.distribute()
            self.assertEqual(len(step.jobs), 1)
            mockde_db.params('step_run', True)
            run_conifg = {
                'steps_config': {
                    'step': {
                        'sub_steps': {
                            '0': {
                                'output': {
                                    'results': {
                                        'meta': {
                                            'pipeline': {},
                                            'step': {},
                                            'job': {},
                                        },
                                        'outputs': {}
                                    },
                                    'status': s
                                }
                            }
                        },
                        'output': {
                            'results': {
                                'meta': {
                                    'pipeline': {}
                                }
                            },
                            'status': s
                        }
                    }
                }
            }
            mockde_db.params('run_config', run_conifg)
            res = step.get_status()
            self.assertEqual(res[0], s)

        step = MockStep2('test', 'test', 'step')
        step.output_dir = 'foo'
        step.output_dir = os.path.abspath(self.path_test)
        cfg = {
            'name': 'config',
            'google': 1.0,
            'output_dir': os.path.abspath(self.path_test),
            'step_class': 'pypers.core.test.test_step.MockStep2',
            'toto': 'foo/test.xml',
            'meta': {
                'pipeline': [],
                'step': [],
                'job': {
                    'pipeline': [],
                    'step': [],
                    'job': {
                        'toto': '1',
                        'non_array': '2'
                    }
                }
            }
        }
        step.cfg = cfg
        mockde_db.update(cfg)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        step.distribute()
        self.assertEqual(len(step.jobs), 1)
        for job in step.jobs:
            step.jobs[job].out_result = ["a result"]
        for _ in range(0, 50):
            res = step.get_status()
            self.assertEqual(res[0], JOB_STATUS.RUNNING)


class TestStepRun(unittest.TestCase):

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.path = os.path.dirname(__file__)
        self.step = MockStep2('test', 'test', 'step')
        self.step.output_dir = 'foo'
        self.path_test = 'foo'
        try:
            shutil.rmtree('foo/')
        except Exception as e:
            pass
        os.makedirs(self.path_test)

    def tearDown(self):
        try:
            shutil.rmtree('foo/')
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_run(self):
        if os.environ.get('SHORT_TEST', None):
            return
        try:
            self.step.run()
            self.fail("shoud fail")
        except NotImplementedError as e:
            pass


class TestFunctionStepRun(unittest.TestCase):

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.path = os.path.dirname(__file__)
        self.step = MockFunctionStep('test', 'test', 'step')
        self.step.output_dir = 'foo'
        self.path_test = 'foo'
        try:
            shutil.rmtree('foo/')
        except Exception as e:
            pass
        os.makedirs(self.path_test)

    def tearDown(self):
        try:
            shutil.rmtree('foo/')
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_run(self):
        if os.environ.get('SHORT_TEST', None):
            return
        os.makedirs('foo/bar')
        with open('foo/bar/test.txt', 'w') as f:
            f.write('toto')
        self.step.output_dir = os.path.abspath(self.path_test)
        self.step.run()
        self.assertEqual(self.step.status, JOB_STATUS.SUCCEEDED)


if __name__ == "__main__":
    unittest.main()
