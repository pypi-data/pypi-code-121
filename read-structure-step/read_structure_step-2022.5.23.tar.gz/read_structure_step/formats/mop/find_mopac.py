import seamm_util
from pathlib import Path
import os

mopac_error_identifiers = []


def find_mopac():
    try:
        mopac_exe = "/opt/mopac/MOPAC2016.exe"

        if os.path.isfile(mopac_exe) is False:
            raise FileNotFoundError(
                'The directory "/opt/mopac/" exists, but the executable \
                "MOPAC2016.exe" is not there'
            )

    except FileNotFoundError:
        try:

            mopac_path = os.path.split(os.environ["mopac"])[0]
            mopac_exe = mopac_path + "MOPAC2016.exe"

            if os.path.isfile(mopac_exe) is False:
                raise FileNotFoundError(
                    'The environment variable "mopac" is defined, but \
                            the executable "MOPAC2016.exe" is not there'
                )

        except (KeyError, FileNotFoundError):
            try:
                mopac_exe = Path(os.environ["MOPAC_LICENSE"]) / "MOPAC2016.exe"
                mopac_exe = str(mopac_exe)

                if os.path.isfile(mopac_exe) is False:
                    raise FileNotFoundError(
                        'The environment variable "mopac" is defined, but the \
                                executable "MOPAC2016.exe" is not there'
                    )

            except (KeyError, FileNotFoundError):
                try:
                    mopac_exe = seamm_util.check_executable("MOPAC2016.exe")
                except FileNotFoundError:
                    return None

    return mopac_exe
