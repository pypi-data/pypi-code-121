from collections import namedtuple
from glob import glob
import os

import yaml

# Describe a (set of) files that should be deployed with an AlazarTech
# product. See module documentation for details.
DeploymentSpecification = namedtuple('DeploymentSpecification', [
    'pattern',   # type: str
    'compress',  # type: bool
    'encrypt',   # type: bool
    'many',      # type: bool
    'sign',      # type: bool
    'destdir',   # type: str
    'exclude',   # type: list of str
    ])

def get_specs_from_file(specspath):
    output = []
    with open(specspath, 'r') as sfile:
        specslist = yaml.load(sfile, Loader=yaml.FullLoader)
        for specsdict in specslist:
            if 'many' not in specsdict:
                specsdict['many'] = False
            if 'compress' not in specsdict:
                specsdict['compress'] = False
            if 'encrypt' not in specsdict:
                specsdict['encrypt'] = False
            if 'sign' not in specsdict:
                specsdict['sign'] = False
            if 'destdir' not in specsdict:
                specsdict['destdir'] = '/'
            if 'exclude' not in specsdict:
                specsdict['exclude'] = []
            output.append(DeploymentSpecification(**specsdict))
    return output

def get_things(spec):
    '''Returns the list of files/directories to copy based on a spec'''
    thinglist = glob(spec.pattern)
    if not thinglist:
        raise ValueError("Pattern {} matched no element".format(spec.pattern))
    if not spec.many and len(thinglist) > 1:
        raise ValueError(
            "Pattern {} matched more than one element: {}".format(spec.pattern, thinglist)
        )

    normlist = [os.path.normpath(thing) for thing in thinglist]

    for exclusions in spec.exclude:
        exclusionlist = glob(exclusions)
        for excludefile in exclusionlist:
            try:
               normlist.remove(os.path.normpath(excludefile))
            except:
                '''do nothing'''

    return normlist

def getenv(env_var):
    '''Queries the environment variable named `env_var`, and raises an exception if
    it is not set.'''
    if env_var not in os.environ:
        raise ValueError("{} environment variable is not set".format(env_var))
    return os.environ[env_var]
