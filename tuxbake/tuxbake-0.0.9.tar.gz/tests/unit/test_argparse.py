from unittest.mock import patch
import argparse


def test_setup_parser():
    from tuxbake.argparse import setup_parser

    assert isinstance(setup_parser(), argparse.ArgumentParser)

    """
      ( -- ) Refers to named optional arguments, i.e parser_map data can be in any order and also optional until specified as required.
    """
    parser_map = {
        "--build-definition": "oniro.json",
        "--runtime": "docker",
        "--image": None,
        "--src-dir": None,
        "--build-dir-name": "build",
        "--local-manifest": None,
        "--pinned-manifest": None,
    }
    data = ["test.py"]  # adding first argument as file_name
    for key in parser_map:
        data.extend([key, parser_map[key]])
    with patch("sys.argv", data):
        data = setup_parser().parse_args()
        assert all(
            [
                data.build_definition == parser_map["--build-definition"],
                data.runtime == parser_map["--runtime"],
                data.image == parser_map["--image"],
                data.src_dir == parser_map["--src-dir"],
                data.build_dir_name == parser_map["--build-dir-name"],
                data.local_manifest == parser_map["--local-manifest"],
                data.pinned_manifest == parser_map["--pinned-manifest"],
            ]
        )
