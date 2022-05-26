from shutil import copytree, ignore_patterns

from servicefoundry.internal.io.output_callback import OutputCallBack

from ..const import SFY_DIR
from ..model.build_pack import BuildPack
from ..util import clean_dir, create_file_from_content, execute


class BasePackage:
    def __init__(self, build_dir, build_pack: BuildPack):
        self.build_pack = build_pack
        self.build_dir = build_dir

    def clean(self, callback: OutputCallBack):
        callback.print_line(f"Cleaning build directory {self.build_dir}")
        clean_dir(self.build_dir)

    def pre_package(self, callback: OutputCallBack):
        self._copy_file()
        if self.build_pack.pre_build_script:
            callback.print_header("Going to run pre build script")
            pre_build_script = f"{self.build_dir}/preBuildScript"
            create_file_from_content(
                pre_build_script, self.build_pack.pre_build_script, executable=True
            )
            cmd = [pre_build_script]
            for line in execute(cmd):
                callback.print_line(line.rstrip())

    def _copy_file(self):
        if self.build_pack.ignore_patterns:
            patterns = ignore_patterns(*self.build_pack.ignore_patterns, SFY_DIR)
        else:
            patterns = ignore_patterns(SFY_DIR)
        copytree("./", self.build_dir, ignore=patterns)

    def package(self, callback: OutputCallBack):
        pass
