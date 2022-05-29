import filecmp
import os


from clmgr.main import main

test_dir = os.path.dirname(os.path.realpath(__file__))


def test_multiple_update_java():
    global test_dir

    # Test arguments
    test_args = [
        "-c",
        test_dir + "/config/multiple.update.yml",
        "--file",
        test_dir + "/input/java/MultipleUpdate.java",
        "--header-length",
        "120",
    ]

    main(test_args)

    assert filecmp.cmp(
        test_dir + "/input/java/MultipleUpdate.java",
        test_dir + "/output/java/MultipleUpdate.java",
        shallow=False,
    )
