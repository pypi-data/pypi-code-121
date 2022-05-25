import os.path
import subprocess
from typing import List


class Tar:
    @staticmethod
    def gzip(output_file_name: str, path_to_zip: str, exclude_paths: List = ()) -> int:
        """
        exclude_paths: relative path from path_to_zip
        """
        commands = ["tar", "-C", path_to_zip]
        for exclude_path in exclude_paths:
            commands.extend(["--exclude", exclude_path])
        commands.extend(["-zcf", output_file_name, "."])

        subprocess.run(commands).check_returncode()
        return os.path.getsize(output_file_name)

    @staticmethod
    def extract(tar_file_name: str, path_to_extract: str):
        subprocess.run(["mkdir", "-p", path_to_extract]).check_returncode()
        subprocess.run(["tar", "xf", tar_file_name, "-C", path_to_extract]).check_returncode()
