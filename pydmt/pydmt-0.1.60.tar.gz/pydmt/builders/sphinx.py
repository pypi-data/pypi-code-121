"""
This is the module which is in charge of running sphinx to generate
automatic documentation.

TODO
maybe call sphinx programatically and this way we would not have
to set the PYTHONPATH and get better integration with sphinx?
"""


import os
import shutil
from typing import List, Generator, Tuple

from pydmt.api.builder import Builder, Node, SourceFile, SourceFolder, TargetFolder
from pydmt.utils.filesystem import files_under_folder, unlink_files, copy_mkdir
from pydmt.utils.digest import sha1_file
from pydmt.utils.subprocess import check_call


class BuilderSphinx(Builder):
    """
    This is review of how to build a sphinx documentation:
    - if you want documentation for the code you need to run "sphinx-apidoc"
    - it will generate files that describe every sub package in your package.
    - after this you run "sphinx-build"
    - "sphinx-quickstart" is not needed unless you are starting a new project.
    """
    def get_sources(self) -> List[Node]:
        file_list = [
            SourceFile(os.path.join(self.source_folder, "index.rst")),
            SourceFile(os.path.join(self.source_folder, "conf.py")),
            SourceFolder(os.path.join(self.source_folder, "static")),
            SourceFolder(os.path.join(self.source_folder, "copy")),
        ]
        if os.path.isfile(self.package_name + ".py"):
            file_list.append(SourceFile(self.package_name + ".py"))
        if os.path.isdir(self.package_name):
            # we add only py files because python source folder may have .pyc
            # and other junk floating around...
            for fname in files_under_folder(self.package_name, suffix=".py"):
                file_list.append(SourceFile(fname))
        if os.path.isdir("config"):
            file_list.append(SourceFolder("config"))
        return file_list

    def get_targets(self) -> List[Node]:
        return [TargetFolder(self.target_folder)]

    def __init__(self,
                 source_folder: str = "sphinx",
                 target_folder: str = "docs"):
        super().__init__()
        self.package_name = os.path.basename(os.getcwd())
        self.source_folder = source_folder
        self.target_folder = target_folder

    def _get_source_folder_targets(self) -> List[str]:
        return [
            os.path.join(self.source_folder, "modules.rst"),
            os.path.join(self.source_folder, f"{self.package_name}.rst"),
            # We need to add the list of all output files of running sphinx-apidoc
            # os.path.join(self.source_folder, "{}.endpoints.rst".format(self.package_name)),
        ]

    def build(self) -> None:
        unlink_files(self._get_source_folder_targets(), only_if_exist=True)
        if os.path.isdir(self.target_folder):
            shutil.rmtree(self.target_folder, ignore_errors=False)
        args = [
            "sphinx-apidoc",
            "-q",  # quiet
            "-o",
            # self.target_folder,
            self.source_folder,
        ]
        # single file module vs package
        if os.path.isfile(self.package_name + '.py'):
            args.append(self.package_name + '.py')
        else:
            args.append(self.package_name)
        check_call(args)
        os.environ["PYTHONPATH"] = "."
        check_call([
            "sphinx-build",
            # don't use a saved environment, always read all files
            # "-E",
            # Do not emit colored output(default: auto - detect)
            "--no-color",
            # turn warnings into errors
            "-W",
            # no output on stdout, just warnings on stderr
            "-q",
            self.source_folder,
            self.target_folder,
        ])
        for filename in files_under_folder(os.path.join(self.source_folder, "copy")):
            basename = os.path.basename(filename)
            copy_mkdir(filename, os.path.join(self.target_folder, basename))

    def yield_results(self) -> Generator[Tuple[str, str], None, None]:
        return_list = self._get_source_folder_targets()
        return_list.extend(files_under_folder(self.target_folder))
        for x in return_list:
            yield sha1_file(x), x
