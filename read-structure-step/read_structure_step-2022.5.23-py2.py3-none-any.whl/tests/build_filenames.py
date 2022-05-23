import os


def build_data_filename(*filename):
    # Make sure file exists
    test_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(test_dir, "data")

    fname = os.path.join(data_dir, *filename)

    return fname


def build_scratch_filename(filename):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    scratch_dir = os.path.join(test_dir, "scratch")
    if not os.path.exists(scratch_dir):
        os.mkdir(scratch_dir)

    return os.path.join(scratch_dir, filename)
