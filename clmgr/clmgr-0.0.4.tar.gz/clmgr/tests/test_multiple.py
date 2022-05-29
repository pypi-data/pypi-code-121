import filecmp
import os


from clmgr.main import main

test_dir = os.path.dirname(os.path.realpath(__file__))


def test_multiple_java():
    global test_dir

    # Test arguments
    test_args = [
        "-c",
        test_dir + "/config/multiple.yml",
        "--file",
        test_dir + "/input/java/Multiple.java",
        "--header-length",
        "120",
    ]

    main(test_args)

    assert filecmp.cmp(
        test_dir + "/input/java/Multiple.java",
        test_dir + "/output/java/Multiple.java",
        shallow=False,
    )
