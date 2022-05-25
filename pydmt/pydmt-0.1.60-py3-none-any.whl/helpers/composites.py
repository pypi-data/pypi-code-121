import pydmt.helpers.apt
import pydmt.helpers.git

deb_version = f"{pydmt.helpers.git.git_version}~{pydmt.helpers.apt.codename}"
