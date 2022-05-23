import os


def mopac_exists():

    if os.path.isdir("/opt/mopac/"):
        mopac_path = "/opt/mopac/"
    else:
        try:
            mopac_path = os.path.split(os.environ["mopac"])[0]
        except KeyError:
            try:
                mopac_path = os.environ["MOPAC_LICENSE"]
            except KeyError:
                return False

        mopac_exe = mopac_path + "MOPAC2016.exe"

        if os.path.isfile(mopac_exe):
            return True
        else:
            return False
