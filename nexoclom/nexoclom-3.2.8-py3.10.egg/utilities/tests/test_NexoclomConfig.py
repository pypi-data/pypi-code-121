from nexoclom.utilities import NexoclomConfig
import os
import shutil
import subprocess
import pytest


configfiles = ['.nexoclom', '.nexoclom_test', '.nexoclom_test2']
results = [{'savepath':'/Users/mburger/Work/Research/modeloutputs',
            'database':'thesolarsystemmb',
            'port':5432,
            'dbhost': False},
           {'savepath':'/Users/mburger/Work/Research/modeloutputs_test',
            'database':'thesolarsystemmb_test',
            'port':5432,
            'dbhost': False},
           {'savepath':'/Users/mburger/Work/Research/modeloutputs2',
            'database':'thesolarsystemmb',
            'port':1234,
            'dbhost': 'dlhlalab1.stsci.edu'}]


@pytest.mark.utilities
@pytest.mark.parametrize('inputs', zip(configfiles, results))
def test_read_configfile_and_database_connect(inputs):
    def compare_config(conf, res):
        assert conf.savepath == res['savepath']
        assert conf.database == res['database']
        assert conf.port == res['port']
        assert conf.dbhost == res['dbhost']
        return 0
        
    def compare_database(con, res):
        assert con.autocommit
        assert con.info.dbname == res['database']
        return 0
    
    configfile, result = inputs
    os.environ['NEXOCLOMCONFIG'] = os.path.join(os.environ['HOME'], configfile)
    if configfile == '.nexoclom_test':
        # Test with environment variable
        # config file = '/Users/mburger/.nexoclom_test'
        if os.path.exists(result['savepath']):
            shutil.rmtree(result['savepath'])
        else:
            pass
        
        # Verify NexoclomConfig() works
        config = NexoclomConfig()
        assert os.path.exists(result['savepath'])
        compare_config(config, result)
        
        # Verify config.verify_database_running() works
        subprocess.run('pg_ctl stop', capture_output=True, shell=True)
        # verify database starts up
        assert config.verify_database_running() == 'Started Database'

        # verify database running
        assert config.verify_database_running() == 'Database Already Running'
        
        # Verify config.database_connect works
        compare_database(config.database_connect(), result)
    elif configfile == '.nexoclom':
        del os.environ['NEXOCLOMCONFIG']
        
        config = NexoclomConfig()
        compare_config(config, result)
    elif configfile == '.nexoclom_test2':
        # Test with different port and external database
        config = NexoclomConfig(os.path.join(os.environ['HOME'], configfile))
        compare_config(config, result)
if __name__ == '__main__':
    for param in zip(configfiles, results):
        test_read_configfile_and_database_connect(param)
