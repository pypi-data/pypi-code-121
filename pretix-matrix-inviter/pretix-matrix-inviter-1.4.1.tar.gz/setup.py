import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

from pretix_matrix_inviter import __version__


try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except Exception:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="pretix-matrix-inviter",
    version=__version__,
    description="Invite Pretix participants to a Matrix Room or Space.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.fachschaften.org/kif/pretix-matrix-inviter",
    project_urls={
        "Changelog": "https://gitlab.fachschaften.org/kif/pretix-matrix-inviter/-/blob/main/CHANGELOG.md",
        "Tracker": "https://gitlab.fachschaften.org/kif/pretix-matrix-inviter/-/issues",
        "Pretix Marketplace": "https://marketplace.pretix.eu/products/pretix-matrix-inviter/",
    },
    author="Felix Schäfer",
    author_email="admin@kif.rocks",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Topic :: Communications :: Chat",
    ],
    install_requires=["requests"],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_matrix_inviter=pretix_matrix_inviter:PretixPluginMeta
""",
)
