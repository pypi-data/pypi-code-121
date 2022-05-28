import pkgutil


def get_resource(resname: str, package: str = "yog.res"):
    return pkgutil.get_data(package, resname)