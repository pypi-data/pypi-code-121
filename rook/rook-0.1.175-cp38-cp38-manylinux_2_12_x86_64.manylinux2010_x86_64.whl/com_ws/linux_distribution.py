import sys
import platform


class LinuxDistribution:
    name = ''
    version = ''

    if platform.system() == "Linux":
        if sys.version_info[0] < 3:
            name, version = platform.linux_distribution()[:2]
        else:
            try:
                import distro
                name = distro.name()
                version = distro.version()
            except ImportError:
                pass

    @staticmethod
    def get_version():
        return LinuxDistribution.version

    @staticmethod
    def get_name():
        return LinuxDistribution.name
