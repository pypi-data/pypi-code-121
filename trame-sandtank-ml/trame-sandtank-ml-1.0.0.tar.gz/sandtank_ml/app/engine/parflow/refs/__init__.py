from pathlib import Path
from shutil import copyfile

BASE_DIR = str(Path(__file__).parent.resolve().absolute())

REF_FILES = [
    "run.yaml",
    "SandTank_Indicator.pfb",
    "SandTank.pfsol",
]


def copy_refs(run_directory):
    for name in REF_FILES:
        src_file = Path(BASE_DIR, name)
        dst_file = Path(run_directory, name)
        copyfile(src_file, dst_file)
