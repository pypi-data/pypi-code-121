import pydmt.helpers.project

# deb section
deb_package = True
deb_section = "python"
deb_priority = "optional"
deb_architecture = "all"
deb_pkgname = pydmt.helpers.project.get_name()
# to which series to publish the package?
# https://wiki.ubuntu.com/Releases
deb_series = [
    # "eoan",  # 19.10
    "disco",  # 19.04
    "cosmic",  # 18.10
    "bionic",  # 18.04
    # "artful",  # 17.10 EOL
    # "zesty",  # 17.04 EOL
    # "yakkety",  # 16.10 EOL
    "xenial",  # 16.04
    # "wily",  # 15.10 EOL
    # "vivid",  # 15.04 EOL
    # "utopic", # 14.10 EOL
    "trusty",  # 14.04
    # "saucy", # 13.10 EOL
    # "raring", # 13.04 EOL
]
# these are dependencies for runtime
# deb_depends = f"${misc:Depends}, ${python3:Depends}, python3-mako"
# these are dependencies for buildtime at launchpad ppa
deb_builddepends = "python3, python3-setuptools, debhelper, dh-python"
deb_standards_version = "3.9.8"
# deb_standards_version="3.9.5"
deb_x_python_version = ">= 3.4"
deb_x_python3_version = ">= 3.4"
deb_urgency = "low"
