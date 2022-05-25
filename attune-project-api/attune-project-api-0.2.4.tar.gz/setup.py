import os
import shutil

from setuptools import find_packages
from setuptools import setup

pip_package_name = "attune-project-api"
py_package_folder = "attune_project_api"
package_version = '0.2.4'

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile("MANIFEST"):
    os.remove("MANIFEST")

includePathContains = ("alembic_migrations", "alembic.ini")
excludePathContains = ("__pycache__", "platforms", "dist")
includeFilesStartWith = ()
excludeFilesEndWith = (".pyc", ".Apple")
excludeFilesStartWith = ("test", "tests")


def find_package_files():
    paths = []
    for (path, directories, filenames) in os.walk(py_package_folder):
        if not [e for e in includePathContains if e in path]:
            if [e for e in excludePathContains if e in path]:
                continue

        for filename in filenames:
            if not [e for e in includeFilesStartWith if filename.startswith(e)]:
                if [e for e in excludeFilesEndWith if filename.endswith(e)]:
                    continue

                if [e for e in excludeFilesStartWith if filename.startswith(e)]:
                    continue

            relPath = os.path.join(path, filename)
            paths.append(relPath[len(py_package_folder) + 1 :])

    return paths


package_files = find_package_files()

requirements = [
    "twisted",
    "pygit2",
    "vortexpy==2.6.*",
    "pytz",
    "pathvalidate",
    # Support for inspecting 7z archives
    "py7zr",
    "markdown",
    "alembic",
]


doc_requirements = [
    "sphinx",
    "sphinx-rtd-theme",
    "sphinx-autobuild",
    "pytmpdir",
]

requirements.extend(doc_requirements)

setup(
    name=pip_package_name,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    package_data={"": package_files},
    install_requires=requirements,
    zip_safe=False,
    version=package_version,
    description="",
    author="ServerTribe",
    author_email="support@servertribe.com",
    classifiers=["Programming Language :: Python :: 3.9"],
)
