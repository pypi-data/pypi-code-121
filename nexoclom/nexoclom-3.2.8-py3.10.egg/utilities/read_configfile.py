import os


class ConfigfileError(Exception):
    def __init__(self, configfile, missing):
        self.expression = configfile
        self.message = f'{missing} not defined in {configfile}'


def read_configfile():
    """Configure external resources used in the model.
    The following parameters can be saved in the file `$HOME/.nexoclom`.
    * savepath = <path where output files are saved>
    * datapath = <path where MESSENGER data is kept>
    * database = <name of the postgresql database to use> (*optional*)
    * port = <port for postgreSQL server to use> (*optional*)
    
    If savepath and datapath are not present, an exception is raised
    """
    configfile = os.path.join(os.environ['HOME'], '.nexoclom')
    config = {}
    if os.path.isfile(configfile):
        # Read the config file into a dict
        for line in open(configfile, 'r').readlines():
            if '=' in line:
                key, value = line.split('=')
                config[key.strip()] = value.strip()
            else:
                pass
    else:
        pass

    savepath = config.get('savepath', None)
    if savepath is None:
        raise ConfigfileError(configfile, savepath)
    elif not os.path.exists(savepath):
        os.makedirs(savepath)
    else:
        pass

    datapath = config.get('datapath', None)
    if datapath is None:
        raise ConfigfileError(configfile, datapath)
    else:
        pass

    return config
