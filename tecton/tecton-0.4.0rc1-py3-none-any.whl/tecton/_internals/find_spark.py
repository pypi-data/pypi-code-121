import importlib.resources
import importlib.util
import sys
from pathlib import Path


def find_spark():
    spec = importlib.util.find_spec("pyspark")
    if spec:
        # pyspark exists in the system path
        return
    tecton_spec = importlib.util.find_spec("tecton")
    vendor_path = Path(tecton_spec.origin).parent / "vendor/pyspark"
    if not vendor_path.exists():
        raise Exception(f"Could not locate system pyspark or vendored pyspark (looked in {vendor_path})")
    # insert at the beginning. This is important because although we already know pyspark isn't anywhere in the path,
    # we've also vendored the corresponding version of py4j
    sys.path.insert(0, str(vendor_path))
    if importlib.util.find_spec("pyspark") == None:
        raise Exception(f"Could not import vendored pyspark (added path {vendor_path})")
