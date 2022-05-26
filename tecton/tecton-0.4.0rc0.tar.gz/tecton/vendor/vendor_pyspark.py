import os
import tempfile
import shutil
from pathlib import Path
import subprocess
import zipfile

PYSPARK_VERSION = "3.1.2"

parent_dir = Path(__file__).parent
vendor_dir = parent_dir / "pyspark"
shutil.rmtree(vendor_dir, ignore_errors=True)
vendor_dir.mkdir()

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    os.chdir(d)
    subprocess.check_call(["pip", "wheel", f"pyspark=={PYSPARK_VERSION}"])


    def extract_whl(package_name):
        whl_glob = list(d.glob(f"{package_name}-*.whl"))
        assert len(whl_glob) == 1
        whl = whl_glob[0]
        with zipfile.ZipFile(whl) as z:
            for name in z.namelist():
                if all((name.startswith(f"{package_name}/"),
                        name.endswith(".py"),
                        not "/tests/" in name,
                        not "/examples/" in name)):
                    print(name)
                    z.extract(name, path=vendor_dir)
        with open(vendor_dir / package_name / "BUILD.bazel", "w") as f:
            f.write("\n".join([
                "py_library(",
                "    name = \"pkg\",",
                "    srcs = glob([\"**/*.py\"]),",
                "    visibility = [\"//sdk/pypi:__pkg__\"],",
                ")",
                "",
            ]))


    extract_whl("py4j")
    extract_whl("pyspark")

subprocess.check_call(["patch", str(vendor_dir / "pyspark/context.py"), str(parent_dir / "pyspark_context.patch")])
