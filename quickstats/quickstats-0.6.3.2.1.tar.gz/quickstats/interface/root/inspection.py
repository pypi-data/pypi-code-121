import os
import sys
import re
import subprocess
import numbers
from collections import namedtuple

# taken from root_numpy:
# https://github.com/scikit-hep/root_numpy/blob/master/root_numpy/setup_utils.py
class ROOTVersion(namedtuple('_ROOTVersionBase',
                             ['major', 'minor', 'micro'])):

    def __new__(cls, *version):
        if len(version) == 1:
            version = version[0]

        if isinstance(version, numbers.Integral):
            if version < 1E4:
                raise ValueError(
                    "{0:d} is not a valid ROOT version integer".format(version))
            return super(ROOTVersion, cls).__new__(
                cls,
                int(version / 1E4),
                int((version / 1E2) % 100),
                int(version % 100))

        if isinstance(version, tuple):
            return super(ROOTVersion, cls).__new__(cls, *version)

        # parse the string version X.YY/ZZ
        match = re.match(
            r"(?P<major>[\d]+)\.(?P<minor>[\d]+)/(?P<micro>[\d]+)", version)
        if not match:
            raise ValueError(
                "'{0}' is not a valid ROOT version string".format(version))
        return super(ROOTVersion, cls).__new__(
            cls,
            int(match.group('major')),
            int(match.group('minor')),
            int(match.group('micro')))
    
    def __eq__(self, version):
        if not isinstance(version, tuple):
            version = ROOTVersion(version)
        return super(ROOTVersion, self).__eq__(version)

    def __ne__(self, version):
        return not self.__eq__(version)

    def __gt__(self, version):
        if not isinstance(version, tuple):
            version = ROOTVersion(version)
        return super(ROOTVersion, self).__gt__(version)

    def __ge__(self, version):
        if not isinstance(version, tuple):
            version = ROOTVersion(version)
        return super(ROOTVersion, self).__ge__(version)

    def __lt__(self, version):
        if not isinstance(version, tuple):
            version = ROOTVersion(version)
        return super(ROOTVersion, self).__lt__(version)

    def __le__(self, version):
        if not isinstance(version, tuple):
            version = ROOTVersion(version)
        return super(ROOTVersion, self).__le__(version)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '{0:d}.{1:02d}/{2:02d}'.format(*self)
    
def get_subprocess_output(args):
    try:
        output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0].strip()
    except OSError:
        raise RuntimeError(f"failed to invoke command \"{args[0]}\""
                           f", please check ROOT is installed properly")
    if isinstance(output, bytes):
        output = output.decode('utf-8')
    return output

class ROOTChecker:
    def __init__(self):
        self.rootsys = self.get_rootsys()
        self.root_config_cmd = self.get_root_config_cmd()
    
    @staticmethod
    def get_rootsys():
        rootsys = os.getenv('ROOTSYS', None)
        return rootsys
    
    @staticmethod
    def get_root_config_cmd():
        rootsys = ROOTChecker.get_rootsys()
        if rootsys is not None:
            root_config_cmd = os.path.join(rootsys, 'bin', 'root-config')
        else:
            root_config_cmd = 'root-config'
        return root_config_cmd 
    
    def get_specs(self):
        specs = {
            'version': self.get_installed_root_version(self.root_config_cmd),
            **self.get_root_flags(self.root_config_cmd)
        }
        return specs
    
    @staticmethod
    def get_installed_root_version(root_config_cmd:str='root-config'):
        version = get_subprocess_output([root_config_cmd, '--version'])
        return ROOTVersion(version)
    
    @staticmethod
    def get_active_root_version():
        import ROOT
        version = ROOT.gROOT.GetVersionInt()
        return ROOTVersion(version)
    
    @staticmethod
    def get_root_flags(root_config_cmd:str='root-config'):
        root_cflags = get_subprocess_output([root_config_cmd, '--cflags'])
        root_ldflags = get_subprocess_output([root_config_cmd, '--libs'])
        flags = {
            'cflags': root_cflags.split(),
            'ldflags': root_ldflags.split()
        }
        return flags
    
    @staticmethod
    def has_feature(feature:str, root_config:str='root-config'):
        has_feature = get_subprocess_output([root_config_cmd, '--has-{0}'.format(feature)])
        return has_feature == 'yes'