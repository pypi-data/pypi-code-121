import os
import json

from .logging import log, print_t, print_e

from .downloads import CONFIG_HOME, expand_path

PROFILE_HOME = os.path.join(CONFIG_HOME, "profiles")

profile_home = expand_path(PROFILE_HOME)


def load_profiles():
    all_profiles = {}

    try:
        entry = os.scandir(profile_home)
        files = filter(lambda x: x.is_file(), entry)
        fnames = map(lambda x: x.path, files)
        profiles = filter(
            lambda x: os.path.splitext(os.path.basename(x))[1].lower() == ".json",
            fnames,
        )

        for p in profiles:
            print_t("load profile", p)
            try:
                with open(p) as f:
                    cont = f.read()
                    o = json.loads(cont)
                    nam = os.path.splitext(os.path.basename(p))[0]
                    all_profiles[nam] = o
            except Exception as ex:
                print_t(ex, "load failed", p)

    except Exception as ex:
        print_e(ex, "load failed")

    print_t("all_profiles", all_profiles)

    return all_profiles
