# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import tempfile
import time
from glob import glob
from io import open
from os import environ, path, system
from shutil import rmtree
from sys import platform, version_info

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install_lib import install_lib

root_dir = path.abspath(path.dirname(__file__))


# This is where the version should be updated for releases
CONTRAST_RELEASE_VERSION = "5.12.0"


def read(*parts):
    with open(path.join(root_dir, *parts), encoding="utf-8") as f:
        return f.read()


# TODO: PYT-1119 add "service_api_pb2.py" to this list
PROTOBUF_FILES = ["dtm_pb2.py", "settings_pb2.py"]
for filename in PROTOBUF_FILES:
    file_location = path.join("src", "contrast", "api", filename)
    if not path.isfile(path.join(root_dir, file_location)):
        raise RuntimeError(
            "Unable to find generated protobuf file: {}".format(file_location)
        )

extension_path = path.join("contrast", "assess_extensions")
extension_source_dir = path.join("src", extension_path)
version_dir = path.join(extension_source_dir, "py{}{}".format(*version_info[:2]))
common_dir = path.join(extension_source_dir, "common")

c_sources = glob(path.join(common_dir, "*.c")) + glob(path.join(version_dir, "*.c"))

# Add source files common to all python3 versions
if version_info[0] == 3:
    c_sources.extend(glob(path.join(extension_source_dir, "py3", "*.c")))

if platform.startswith("darwin"):
    link_args = ["-rpath", "@loader_path"]
    platform_args = []
else:
    platform_args = ["-Wno-cast-function-type"]
    link_args = []

debug = environ.get("ASSESS_DEBUG")
debug_args = ["-g", "-O1"] if debug else []
macros = [("ASSESS_DEBUG", 1)] if debug else []
macros.append(("EXTENSION_BUILD_TIME", '"{}"'.format(time.ctime())))

strict_build_args = ["-Werror"] if environ.get("CONTRAST_STRICT_BUILD") else []

extensions = [
    Extension(
        "contrast.assess_extensions.cs_str",
        c_sources,
        libraries=["funchook"],
        include_dirs=[
            extension_source_dir,
            path.join(extension_source_dir, "include"),
        ],
        library_dirs=[extension_source_dir],
        # Path relative to the .so itself (works for gnu-ld)
        runtime_library_dirs=["$ORIGIN"],
        extra_compile_args=[
            "-Wall",
            "-Wextra",
            "-Wno-unused-parameter",
            "-Wmissing-field-initializers",
        ]
        + strict_build_args
        + debug_args
        + platform_args,
        extra_link_args=link_args,
        define_macros=macros,
    )
]

tempdir = None
funchook_temp = None


build_err_msg = """Failed to build Contrast C extension.
It is necessary for autotools (autoconf, automake) to be installed in order for
Contrast to build properly. On lightweight systems such as Alpine, it may be
necessary to install linux-headers if they are not available already. Some
other systems may require "build essential" packages to be installed.
"""


class ContrastBuildExt(build_ext):
    def run(self):
        if system("/bin/sh src/contrast/assess_extensions/build_funchook.sh") != 0:
            raise RuntimeError(build_err_msg)

        build_ext.run(self)

        global tempdir
        global funchook_temp

        ext = "dylib" if platform.startswith("darwin") else "so"
        funchook_name = "libfunchook.{}".format(ext)
        funchook = path.join(extension_source_dir, funchook_name)

        tempdir = tempfile.mkdtemp("contrast-build")
        funchook_temp = path.join(tempdir, funchook_name)
        self.copy_file(funchook, funchook_temp)


class ContrastInstallLib(install_lib):
    def run(self):
        install_lib.run(self)

        if funchook_temp is not None:
            dest_dir = path.join(self.install_dir, extension_path)
            self.copy_file(funchook_temp, dest_dir)
            rmtree(tempdir)


if int(environ.get("CONTRAST_DEV_VERSION", "0")):
    version_config = dict(
        use_scm_version={
            # Parse out the issue name as prefix if it exists
            "tag_regex": (
                r"^(?P<prefix>(CONTRAST|PYT)-\d+/)?(?P<version>.*)(?P<suffix>)?"
            ),
            "git_describe_command": "git describe --tags --dirty --long",
        },
        setup_requires=["setuptools_scm"],
    )
else:
    version_config = dict(version=CONTRAST_RELEASE_VERSION)


setup(
    name="contrast-agent",
    description="Contrast Security's agent for Python web frameworks",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://www.contrastsecurity.com",
    project_urls={
        "Change Log": "https://docs.contrastsecurity.com/en/python-agent-release-notes-and-archive.html",
        "Support": "https://support.contrastsecurity.com",
        "Trouble Shooting": "https://support.contrastsecurity.com/hc/en-us/search?utf8=%E2%9C%93&query=Python",
        "Wiki": "https://docs.contrastsecurity.com/",
    },
    # Author details
    author="Contrast Security, Inc.",
    author_email="python@contrastsecurity.com",
    # Choose your license
    license="CONTRAST SECURITY (see LICENSE.txt)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        # Audience
        "Intended Audience :: Developers",
        # License; commercial
        # supported languages
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="security development",
    # See MANIFEST.in for excluded packages
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"contrast": ["service_executables/*", "../data/policy.json"]},
    python_requires=">=3.7",
    # NOTE: if install_requirements changes, update license_info.py accordingly
    install_requires=[
        "protobuf>=3.12,<3.18; python_version < '3'",
        "protobuf>=3.12,<4; python_version >= '3'",
        "psutil>=5.7,<6",
        "requests>=2.4.2,<3",
    ],
    include_package_data=True,
    cmdclass=dict(build_ext=ContrastBuildExt, install_lib=ContrastInstallLib),
    ext_modules=extensions,
    extras_require={},
    entry_points={
        "console_scripts": [
            "contrast-fix-interpreter-permissions = contrast.scripts:fix_interpreter_permissions",
            "contrast-validate-config = contrast.scripts:validate_config",
        ]
    },
    **version_config,
)
