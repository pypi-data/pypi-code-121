import os
import psycopg
from sqlalchemy import create_engine
import subprocess
from nexoclom.utilities.exceptions import ConfigfileError


DEFAULT_DATABASE = 'thesolarsystemmb'
DEFAULT_PORT = 5432

class NexoclomConfig:
    """Configure external resources used in the model.
    The following parameters can be saved in the file `$HOME/.nexoclom`.
    * savepath = <path where output files are saved>
    * database = <name of the postgresql database to use> (*optional*)
    * port = <port for postgreSQL server to use> (*optional*)
    * dbhost = <hostname for postgreSQL database> (*optional* - leave blank
        to use local database)
    
    If savepath is not present, an exception is raised
    """
    def __init__(self, verbose=False):
        configfile = os.environ.get('NEXOCLOMCONFIG', os.path.join(
            os.environ['HOME'], '.nexoclom'))
        
        if verbose:
            print(f'Using configuration file {configfile}')
        else:
            pass
        self.configfile = configfile
        
        config = {}
        if os.path.isfile(configfile):
            # Read the config file into a dict
            for line in open(configfile, 'r'):
                if '=' in line:
                    key, value = line.split('=')
                    config[key.strip()] = value.strip()
                else:
                    pass
        else:
            pass
        
        self.savepath = config.get('savepath', None)
        if self.savepath is None:
            raise ConfigfileError(configfile, self.savepath)
        elif not os.path.exists(self.savepath):
            os.makedirs(self.savepath)
        else:
            pass
        
        self.database = config.get('database', DEFAULT_DATABASE)
        
        if 'port' not in config:
            self.port = DEFAULT_PORT
        else:
            self.port = int(config['port'])
        
        for key, value in config.items():
            if key not in self.__dict__:
                self.__dict__[key] = value
            else:
                pass
            
        self.dbhost = config.get('dbhost', None)
        
    def __repr__(self):
        return self.__dict__.__repr__()
    
    def __str__(self):
        return self.__dict__.__str__()
    
    def verify_database_running(self):
        # verify database is running; start it if it isn't
        proc = subprocess.run('pg_ctl status', capture_output=True, shell=True)
        if 'server is running' in str(proc.stdout):
            return 'Database Already Running'
        else:
            subprocess.run(f'pg_ctl -o "-p {self.port}" start -l {os.environ["PGDATA"]}/logfile',
                           shell=True)
            return 'Started Database'

    def create_engine(self):
        """Wrapper for slalchemy.create_engine() that determines which database and port to use.

        :return:
        :param database: Default = None to use value from config file
        :param port: Default = None to use value from config file
        :param return_con: False to return database name and port instead of connection
        :return: SQLAlchemy engine
        """
        self.verify_database_running()
        
        if self.dbhost:
            # con = psycopg.connect(host=self.dbhost, dbname=self.database,
            #                       port=self.port)
            url = (f"postgresql+psycopg2://{os.environ['USER']}@{self.dbhost}:"
                   f"{self.port}/{self.database}")
        else:
            url = (f"postgresql+psycopg2://{os.environ['USER']}@localhost:"
                   f"{self.port}/{self.database}")
            # con = psycopg.connect(dbname=self.database, port=self.port)
        engine = create_engine(url, echo=True, future=True)
        # con.autocommit = True

        return engine
