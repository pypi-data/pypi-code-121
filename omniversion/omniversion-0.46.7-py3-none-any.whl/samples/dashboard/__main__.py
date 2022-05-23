from omniversion import Omniversion

from omniversion.pretty_print import pprint

omniversion = Omniversion()
pprint(omniversion)
print(omniversion.packages.filter(package_manager="pip", host="centos-instance", verb=["list", "version"]))
