from shutil import copytree, ignore_patterns

from ..model.build_pack import BuildPack
from ..output_callback import OutputCallBack
from ..util import clean_dir, create_file_from_content, execute


class BasePackage:
    def __init__(self, build_dir, build_pack: BuildPack):
        self.build_pack = build_pack
        self.build_dir = build_dir
        self.build_path = f"{build_dir}/build"

    def clean(self):
        clean_dir(self.build_path)

    def pre_package(self, callback: OutputCallBack):
        if self.build_pack.pre_build_script:
            callback.print_header("Going to run pre build script")
            pre_build_script = f"{self.build_dir}/preBuildScript"
            create_file_from_content(
                pre_build_script, self.build_pack.pre_build_script, executable=True
            )
            cmd = [pre_build_script]
            for line in execute(cmd):
                callback.print_line(line.rstrip())

    def package(self, callback: OutputCallBack):
        if self.build_pack.ignore_patterns:
            patterns = ignore_patterns(
                *self.build_pack.ignore_patterns, f"{self.build_dir}*"
            )
        else:
            patterns = ignore_patterns(f"{self.build_dir}")
        copytree("./", self.build_path, ignore=patterns)
