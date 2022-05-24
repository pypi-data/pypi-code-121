import unittest
from pypers.core.pipelines import Pipeline
from pypers.core.constants import JOB_STATUS
import shutil
import os
import json
import datetime
from pypers.core.interfaces.msgbus.base import MSGBase
from pypers.core.interfaces.db.base import DbBase
from pypers.core.interfaces.db.test import MockDBLogger, MockDBConfig
from mock import patch, MagicMock


pipeline_cfg = '''{
    "dag": {
        "load": "ipas_fetch"
    },
    "config": {
        "pipeline": {
            "project_name": "vntm",
            "description": "desc",
            "collection": "vntm",
            "input": {
                "from_dir": "%s/archives",
                "from_ftp": {
                    "ftp_server": "dataexchange.wipo.int",
                    "ftp_user": "vt",
                    "ftp_passwd": "fglhk467056bgh",
                    "ftp_dir": "/To_BrandsDatabase/CHANGES"
                }
            },
            "output_dir": "%s/workspace"
        },
        "steps": {
            "fetch": {
                "file_regex": "VN_Trademarks_.*zip"
            }
        }
    }
}'''

step_cfg = {
    'name': 'My_ftp',
    'step_class': 'fetch.download.ftp.FTP',
    'config': {
        'pipeline': {},
    },
    'sys_path': '/'
}


class MockDB(DbBase):

    def update(self, cfg):
        self.cfg = cfg

    def params(self, name, value):
        setattr(self, name, value)

    def get_pipeline_config(self, *args, **kwargs):
        return {}

    def create_pypers_config_schema(self):
        return

    def get_running_steps(self, *args, **kwargs):
        return []

    def get_step_config(self, *args, **kwargs):
        return self.cfg

    def has_step_config_changed(self, *args, **kwargs):
        return self.step_changed

    def create_step_config(self, *args, **kwargs):
        self.cfg = args[3]

    def has_step_run(self, *args, **kwargs):
        return self.step_run

    def get_run_id_config(self, *args, **kwargs):
        return self.run_config

    def set_step_output(self, *args, **kwargs):
        return args[3]

    def create_new_run_for_pipeline(self, *args, **kwargs):
        return


class MockSQS(MSGBase):
    counter = 0

    def get_pypers_queue(self):
        pass

    def reset_history(self, runid, collection):
        pass

    def send_message(self, *args, **kwargs):
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


mocked_dbr_config = MockDBConfig()


def mock_db_config(*args, **kwargs):
    return mocked_dbr_config


class TestSchedulerInit(unittest.TestCase):

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    def setUp(self):
        self.path_test = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'foo'))
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        os.makedirs(self.path_test)
        shutil.copy(os.path.join(os.path.dirname(__file__), "local_fetch.json"),
                    os.path.join(self.path_test, 'local_fetch.json'))
        shutil.copy(os.path.join(os.path.dirname(__file__),
                                 "local_fetch2.json"),
                    os.path.join(self.path_test, 'local_fetch2.json'))
        self.pipeline_cfg = pipeline_cfg % (self.path_test,
                                            self.path_test)

    def tearDown(self):
        try:
            shutil.rmtree(self.path_test)
        except Exception as e:
            pass
        try:
            shutil.rmtree('My_ftp')
        except Exception as e:
            pass
        try:
            shutil.rmtree('test_pipelines.py')
        except Exception as e:
            pass

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db_config",
           MagicMock(side_effect=mock_db_config))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_load_cfg_db(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Load normal config from dict
        cfg = Pipeline.load_cfg_from_db('test_fetch')
        self.assertEqual(cfg['name'], 'ipas_fetch')

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_load_cfg(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Load normal config from dict
        row_data = json.loads(self.pipeline_cfg)
        cfg = Pipeline.load_cfg(row_data)
        self.assertEqual(cfg['name'], 'ipas_fetch')
        row_data['dag']['load'] = os.path.join(self.path_test,
                                               'local_fetch.json')
        # Load config from file with spec in local file
        with open(os.path.join(self.path_test, 'config_ex.json'), 'w') as f:
            f.write(json.dumps(row_data))
        cfg = Pipeline.load_cfg(os.path.join(self.path_test, 'config_ex.json'))
        self.assertEqual(cfg['name'], 'local_fetch')
        os.remove(os.path.join(self.path_test, 'config_ex.json'))
        # Load config form bad file
        try:
            cfg = Pipeline.load_cfg(
                os.path.join(self.path_test, 'config_ex.json'))
            self.fail("Should fail because configure file is not present")
        except Exception as e:
            self.assertTrue(str(e).startswith("Unable to load config file"))
        # Load good config with bad specfile
        try:
            row_data['dag']['load'] = os.path.join(self.path_test,
                                                   'toto.json')
            cfg = Pipeline.load_cfg(row_data)
            self.fail("Should fail because configure spec file is not present")
        except Exception as e:
            self.assertTrue(str(e).startswith("Pipeline"))

    @patch("pypers.core.interfaces.db.get_db_logger", MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_load_dag(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        cfg = Pipeline.load_cfg(row_data)
        # Force add a new inputs node
        cfg['inputs'] = 'keyboard'
        dag = Pipeline.create_dag(cfg)
        self.assertEqual(len(dag.nodes()), 6)

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_create_steps(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        cfg = Pipeline.load_cfg(row_data)
        cfg['sys_path'] = '/'
        steps_list = Pipeline.create_steps(cfg)
        self.assertEqual(len(steps_list), 5)

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_get_unbound_inputs(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        row_data['dag']['load'] = os.path.join(self.path_test,
                                               'local_fetch.json')
        uinputs = Pipeline.get_unbound_inputs(row_data)
        self.assertEqual(uinputs['fetch'], ['keyboard'])

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_get_params(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        row_data['dag']['load'] = os.path.join(self.path_test,
                                               'local_fetch.json')
        params = Pipeline.get_params(row_data)
        self.assertEqual(params['steps_order'],
                         ['fetch', 'group', 'extract',
                          'organize', 'clean','inputs'])
        self.assertEqual(params['steps']['fetch']["params"][0]['value'], 1.0)

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_validated_config(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        retval = Pipeline.validate_config(row_data, 'Unknown')
        print(retval)
        self.assertEqual(retval, {})
        # Remove to make the validation fail
        # For the outputdir
        row_data['config']['pipeline']['output_dir'] = './'
        retval = Pipeline.validate_config(row_data, 'Unknown')
        self.assertEqual(retval['pipeline']['output_dir'],
                         './ : not an absolute path')
        row_data['config']['pipeline']['output_dir'] = ['1', '2']
        retval = Pipeline.validate_config(row_data, 'Unknown')
        self.assertEqual(retval['pipeline']['output_dir'],
                         "['1', '2'] : invalid type, found <class 'list'>, "
                         "expected str")

        row_data['config']['pipeline']['output_dir'] = None
        row_data['config']['pipeline']['project_name'] = None
        row_data['config']['pipeline']['description'] = None
        retval = Pipeline.validate_config(row_data, 'Unknown')
        self.assertEqual(retval['pipeline']['output_dir'], "missing value")
        self.assertEqual(retval['pipeline']['description'], "missing value")
        self.assertEqual(retval['pipeline']['project_name'], "missing value")

        row_data = json.loads(self.pipeline_cfg)
        row_data['dag']['load'] = os.path.join(self.path_test,
                                               'local_fetch.json')
        retval = Pipeline.validate_config(row_data, 'Unknown')
        self.assertEqual(retval['steps']['fetch']['limit'],
                         "1.0 : invalid type, found <class 'float'>, "
                         "expected int")
        self.assertEqual(retval['steps']['fetch']['keyboard'],
                         'missing value')

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_create_pipeline(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Normal creation
        row_data = json.loads(self.pipeline_cfg)
        pipeline = Pipeline(row_data)
        self.assertEqual(pipeline.meta['pipeline']['collection'], 'vntm')
        self.assertTrue(pipeline.run_id <=
                        datetime.datetime.today().strftime('%Y%m%d.%H%M'))
        self.assertTrue(os.path.exists(pipeline.output_dir))
        # Creation with bad configuration
        try:
            pipeline = Pipeline('inexsting_file')
            self.fail("Should raise exception because cfg file is invalid")
        except Exception as e:
            print("__", str(e), "__")
            self.assertTrue('Failed to load config' in str(e))

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    def test_next_step(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        pipeline = Pipeline(row_data)

        steps = pipeline.get_next_steps()
        self.assertEqual(steps, {'fetch'})

        pipeline.completed.append('fetch')
        steps = pipeline.get_next_steps()
        self.assertEqual(steps, {'group'})

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_update_status(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        pipeline = Pipeline(row_data)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        run_conifg = {
            'steps_config': {
                'fetch': {
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
                                'status': None
                            }
                        }
                    },
                    'output': {
                        'results': {
                            'meta': {
                                'pipeline': {}
                            }
                        },
                        'status': None
                    }
                }
            }
        }
        mockde_db.params('run_config', run_conifg)
        pipeline.run_step('fetch')
        pipeline.update_status()
        self.assertEqual(pipeline.status, JOB_STATUS.RUNNING)
        run_conifg['steps_config']['fetch']['sub_steps']['0']['output']['status'] = JOB_STATUS.SUCCEEDED
        mockde_db.params('step_run', True)
        mockde_db.params('run_config', run_conifg)
        pipeline.update_status()
        # Force a SUCCEEDED
        self.assertEqual(len(pipeline.completed), 1)

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_run_step(self):
        mocked_msg.counter = 0
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        pipeline = Pipeline(row_data)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        tmp = {
            'sub_steps': {
                '0': {
                    'output': {
                        'results': {
                            'meta': {
                                'pipeline': {},
                                'step': {},
                                'job': {}
                            },
                            'outputs': {
                                'output_data': ['foo'],
                                'dest_dir': ['foobar']
                            }
                        }
                    }
                }
            }
        }
        run_conifg = {'steps_config': {}}
        for step in pipeline.ordered:
            run_conifg['steps_config'][step] = tmp
        counter = 1
        for step in pipeline.ordered:
            try:
                pipeline.run_step(step)
            except Exception as e:
                break
            self.assertEqual(mocked_msg.counter, counter)
            counter += 1
        # With inputs
        row_data = json.loads(self.pipeline_cfg)
        cfg = Pipeline.load_cfg(row_data)
        # Force add a new inputs node
        cfg['inputs'] = 'keyboard'
        pipeline = Pipeline(cfg)
        pipeline.run_step('inputs')
        self.assertEqual(pipeline.outputs['inputs']['output_dir'], '')

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_run_step2(self):
        if os.environ.get('SHORT_TEST', None):
            return
        # Test with custom pipeline
        mocked_msg.counter = 0
        row_data = json.loads(self.pipeline_cfg)
        row_data['dag']['load'] = os.path.join(self.path_test,
                                               'local_fetch.json')
        pipeline = Pipeline(row_data)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        tmp = {
            'sub_steps': {
                '0': {
                    'output': {
                        'results': {
                            'meta': {
                                'pipeline': {},
                                'step': {},
                                'job': {}
                            },
                            'outputs': {
                                'output_data': ['foo'],
                                'dest_dir': ['foobar']
                            }
                        }
                    }
                }
            }
        }
        run_conifg = {'steps_config': {}}
        for step in pipeline.ordered:
            run_conifg['steps_config'][step] = tmp
        mockde_db.params('run_config', run_conifg)
        counter = 1
        for step in pipeline.ordered:

            try:
                mockde_db.params('step_run', False)
                pipeline.run_step(step)
            except Exception as e:
                # In the local_fetch.json the bindings for pimg.input_data is
                # forced to a list in order to test the behaviour of this kind
                # of input. When submiting the job, the distribution will fail.
                # pimg step doesn't accept a list as input_data
                break
                pass
            mockde_db.params('step_run', True)
            if step == 'inputs':
                counter -= 1
            self.assertEqual(mocked_msg.counter, counter)
            counter += 1

    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_run(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        pipeline = Pipeline(row_data)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
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
        res = pipeline.run(verbose=True)
        self.assertEqual(res, None)

    @patch('sys.exit', MagicMock(return_value=1))
    @patch("pypers.core.interfaces.db.get_db_logger",
           MagicMock(side_effect=mock_logger))
    @patch("pypers.core.interfaces.db.get_db", MagicMock(side_effect=mock_db))
    @patch("pypers.core.interfaces.msgbus.get_msg_bus", MagicMock(side_effect=mock_sqs))
    def test_run2(self):
        if os.environ.get('SHORT_TEST', None):
            return
        row_data = json.loads(self.pipeline_cfg)
        pipeline = Pipeline(row_data)
        mockde_db.params('step_changed', False)
        mockde_db.params('step_run', False)
        res = pipeline.run(verbose=True)
        self.assertEqual(res, None)


if __name__ == "__main__":
    unittest.main()
