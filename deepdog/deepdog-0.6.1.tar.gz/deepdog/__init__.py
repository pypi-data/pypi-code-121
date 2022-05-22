import logging
from deepdog.meta import __version__
from deepdog.bayes_run import BayesRun
from deepdog.bayes_run_simulpairs import BayesRunSimulPairs


def get_version():
	return __version__


__all__ = [
	"get_version",
	"BayesRun",
	"BayesRunSimulPairs",
]


logging.getLogger(__name__).addHandler(logging.NullHandler())
