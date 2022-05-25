# (c) 2015-2018 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
import logging
import yaml

logger = logging.getLogger(__file__)

_config = {
    "lsf": None,
    "slurm": None,
    "sge": None,
    "pbs": None,
    "celery": None,
    "playmolecule": None,
    "configfile": os.getenv("JOBQUEUES_CONFIG")
    if os.getenv("JOBQUEUES_CONFIG")
    else None,
}


def config(
    lsf=_config["lsf"],
    slurm=_config["slurm"],
    sge=_config["sge"],
    pbs=_config["pbs"],
    celery=_config["celery"],
    playmolecule=_config["playmolecule"],
    configfile=_config["configfile"],
):
    """
    Function to temporarily change configuration variables.

    Parameters
    ----------
    lsf : str
        Defines a YAML file that can contain default profile configurations for an LsfQueue
    slurm : str
        Defines a YAML file that can contain default profile configurations for an SlurmQueue
    """
    _config["lsf"] = lsf
    _config["slurm"] = slurm
    _config["sge"] = sge
    _config["pbs"] = pbs
    _config["celery"] = celery
    _config["playmolecule"] = playmolecule
    _config["configfile"] = configfile


def loadConfig(cls, queuename, _configfile=None, _configapp=None, _logger=True):
    # Load configuration profile
    if _configfile is None:
        if _config[queuename] is not None:
            _configfile = _config[queuename]
        elif _config["configfile"] is not None:
            _configfile = _config["configfile"]

    if _configapp is not None and _configfile is None:
        raise RuntimeError(
            f"No {queuename} configuration YAML file defined for the app {_configapp}"
        )

    def setproperties(properties):
        if properties is None:
            return
        for p in properties:
            setattr(cls, p, properties[p])
            if _logger:
                logger.info(f"Setting {p} to {properties[p]}")

    configuration = None
    if _configfile is not None:
        if not os.path.isfile(_configfile) or not _configfile.endswith(
            (".yml", ".yaml")
        ):
            logger.warning(f"{_configfile} does not exist or it is not a YAML file.")

        with open(_configfile, "r") as f:
            configuration = yaml.load(f, Loader=yaml.FullLoader)
            # Support also config files with all queues in it
            if queuename in configuration:
                configuration = configuration[queuename]

        if _logger:
            logger.info(f"Loaded {queuename} configuration YAML file {_configfile}")

        if "default" in configuration:
            setproperties(configuration["default"])

        if _configapp is not None:
            if _configapp not in configuration:
                raise RuntimeError(
                    f"There is no configuration for app {_configapp} in {_configfile}"
                )
            else:
                setproperties(configuration[_configapp])


from jinja2 import (
    Environment,
    select_autoescape,
    PackageLoader,
    FileSystemLoader,
    ChoiceLoader,
)

loaders = []

templates = os.getenv("JOBQUEUES_TEMPLATES")
if templates is not None:
    loaders.append(FileSystemLoader(templates))

loaders.append(PackageLoader("jobqueues", "templates"))
loader = ChoiceLoader(loaders)
template_env = Environment(
    loader=loader,
    trim_blocks=True,
    autoescape=select_autoescape(
        [
            "*",
        ]
    ),
)
