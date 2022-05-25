from unittest.mock import patch
from tuxbake.models import OEBuild


def test_build(oebuild_repo_init_object):
    from tuxbake.build import build

    oebuild_repo_init_object.local_manifest = None
    oebuild_object = oebuild_repo_init_object.as_dict()

    with patch.object(OEBuild, "do_build", return_value="build_called"):
        data = build(**oebuild_object)
        assert data == OEBuild(**oebuild_object)
        ret_val = data.do_build()
        assert ret_val == "build_called"
