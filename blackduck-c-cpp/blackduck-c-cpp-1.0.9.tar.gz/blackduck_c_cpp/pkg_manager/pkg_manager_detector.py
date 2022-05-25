"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import platform
import logging
import subprocess
from blackduck_c_cpp.util import util


class PkgDetector:
    """
    Detects Operating system, its distribution and package manager
    """

    def __init__(self):
        # default values to skip package manager steps
        self.package_manager = 'not_found'
        self.os_distribution = 'not_found'

    """ 
    Here are some notes to enhance this method for expanded usefulness:
    /etc/os-release       // ubuntu, redhat, centos or debian (etc... - look inside)
    /etc/SuSE-release     // SUSE 
    /etc/redhat-release   // redhat
    /etc/redhat_version   // redhat
    /etc/system-release   // centos, redhat
    /etc/slackware-release // Slackware
    /etc/fedora-release   // fedora
    /etc/alpine-release   // alpine
    /etc/debian_release   // old debian
    /etc/debian-version   // debian or ubuntu
    /etc/lsb-release      // debian or ubuntu
    /etc/mandrake-release // Mandrake
    /etc/yellowdog-release // Yellow dog
    /etc/gentoo-release    // Gentoo
    /etc/sun-release       // Sun JDS
    /etc/release          // Solaris/Sparc
    """

    def get_platform(self):
        """
        Returns package manager and os distribution
        """
        try:
            platform_name = platform.system()
            logging.info("Platform name is: {}".format(platform_name))
            if 'linux' in platform_name.lower():
                if util.run_cmd("rpm -qa --quiet", suppress_output=True) == 0:
                    self.package_manager = "rpm"
                    self.os_distribution = "fedora"  # default distribution if /etc/os-release file not found
                elif util.run_cmd("dpkg --help", suppress_output=True) == 0:
                    self.package_manager = "dpkg"
                    self.os_distribution = "ubuntu"  # default distribution if /etc/os-release file not found
                (exit_code, os_dist) = subprocess.getstatusoutput("cat /etc/os-release | grep HOME_URL")
                if exit_code == 0:
                    if 'ubuntu' in os_dist.lower():
                        self.os_distribution = "ubuntu"
                    elif 'centos' in os_dist.lower():
                        self.os_distribution = "centos"
                    elif 'fedora' in os_dist.lower():
                        self.os_distribution = "fedora"
                    elif 'opensuse' in os_dist.lower():
                        self.os_distribution = "opensuse"
                    elif 'alpine' in os_dist.lower():
                        self.os_distribution = "alpine"
                    else:
                        pass
            elif 'darwin' in platform_name.lower():
                if util.run_cmd("brew --help") == 0:
                    self.package_manager = 'brew'
                    self.os_distribution = 'Mac'
            elif 'windows' in platform_name.lower():
                self.package_manager = 'not_found'
                self.os_distribution = 'windows'
            logging.info("Operating system distribution is {}".format(self.os_distribution))
            logging.info("Package manager is {}".format(self.package_manager))
            return self.package_manager, self.os_distribution
        except:
            logging.warning("Operating system distribution is not found")
            logging.warning("Package manager is not found")
            return None, None
