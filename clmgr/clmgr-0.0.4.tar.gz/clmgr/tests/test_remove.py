import filecmp
import os


from clmgr.main import main

test_dir = os.path.dirname(os.path.realpath(__file__))


def test_remove_java():
    global test_dir

    test_args = [
        "-c",
        test_dir + "/config/remove.yml",
        "--file",
        test_dir + "/input/java/Remove.java",
        "--header-length",
        "120",
    ]

    # Run clmgr
    main(test_args)

    # Verify result
    assert filecmp.cmp(
        test_dir + "/input/java/Remove.java",
        test_dir + "/output/java/Remove.java",
        shallow=False,
    )
