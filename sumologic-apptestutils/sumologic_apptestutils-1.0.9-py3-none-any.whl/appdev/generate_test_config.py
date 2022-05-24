import json
import os

from sumoapputils.common.testapp import TestApp
from sumoapputils.common.utils import get_content_dirpath, ALL_APPS_FILENAME, EXCLUDED_APP_PREFIXES
from sumoappclient.common.utils import get_normalized_path


def get_json_file():
    manifestjsonfile = appjsonfile = None
    for fname in os.listdir(os.getcwd()):
        if fname.endswith("manifest.json"):
            if not manifestjsonfile:
                manifestjsonfile = fname
            else:
                raise Exception("Multiple manifest file")
        elif fname.endswith(".json"):
            if not appjsonfile:
                appjsonfile = fname
            else:
                raise Exception("Multiple app json file")

    return manifestjsonfile, appjsonfile


def get_content_count(folder, stats):
    for dash in folder["children"]:
        if dash["type"] not in stats["ContentType"]:
            continue
        stats["ContentType"][dash["type"]] += 1
        if dash["type"] in ("Report", "DashboardSyncDefinition", "MewboardSyncDefinition", "Dashboard",
                            "DashboardV2SyncDefinition"):
            panels = dash["rootPanel"]["panels"] if dash.get("rootPanel") else dash.get("panels", [])
            panelData = [{"name": panel["title"] if TestApp.is_mew_board(dash) else panel["name"],
                          "verifyData": False} for panel in panels]
            num_panels = len(panels)
            dashboardData = {"name": dash["name"], "panelData": panelData, "panelsCount": num_panels}
            stats["ContentType"]["ReportPanel"] += num_panels  # includes title/text panels
            if not TestApp.is_mew_board(dash):
                for panel in panels:
                    propjson = json.loads(panel["properties"])
                    target = propjson.get("common", {}).get("configuration", {}).get("drilldown", {}).get(
                        "fallback", {}).get("target", {})
                    if (target.get("id", None)):
                        stats["linking"][panel["name"]] = [dash["name"], target["name"]]
            stats["dashboardData"].append(dashboardData)
        elif dash["type"] in ("Folder", "FolderSyncDefinition"):
            print("Found folder inside folder", dash["name"])
            get_content_count(dash, stats)


def get_app_config(manifestfile, appfile, withpaneldata=False):
    # Todo will change for mewboards and v2 json
    stats = {"dashboardData": []}
    appjson = json.load(open(appfile))
    manifestjson = json.load(open(manifestfile))
    stats['appname'] = manifestjson["name"]
    stats['categories'] = manifestjson['categories']
    stats["sources"] = {}
    for p in manifestjson["parameters"]:
        stats["sources"].setdefault(p["dataSourceType"], 0)
        stats["sources"][p["dataSourceType"]] += 1
    stats["hasMultipleSources"] = len(stats["sources"]) > 1
    stats["linking"] = {}
    stats["ContentType"] = {"ReportPanel": 0,
                            "Report": 0,
                            "Search": 0,
                            "Folder": 0,
                            "MewboardSyncDefinition": 0,
                            "DashboardV2SyncDefinition": 0,
                            "Dashboard": 0,
                            "FolderSyncDefinition": 0,
                            "DashboardSyncDefinition": 0,
                            "SavedSearchWithScheduleSyncDefinition": 0}
    get_content_count(appjson, stats)

    if not withpaneldata and "dashboardData" in stats:
        stats.pop("dashboardData")

    stats["ContentType"]["Search"] += stats["ContentType"].pop(
        "SavedSearchWithScheduleSyncDefinition")  # saved search new
    stats["ContentType"]["Report"] += stats["ContentType"].pop("DashboardSyncDefinition")  # classic new
    stats["ContentType"]["Report"] += stats["ContentType"].pop("Dashboard")  # mewboard old
    stats["ContentType"]["Report"] += stats["ContentType"].pop("MewboardSyncDefinition")  # mewboard new
    stats["ContentType"]["Report"] += stats["ContentType"].pop("DashboardV2SyncDefinition")  # mewboard new
    stats["ContentType"]["Folder"] += stats["ContentType"].pop("FolderSyncDefinition")  # folder new

    return stats


def generate_partner_app_config(unique_file_suffix):
    manifestfile, appfile = get_json_file()
    data = get_app_config(manifestfile, appfile)

    app_config_file = "app-config-%s.json" % unique_file_suffix
    changed_app_file = "changed-apps.txt"

    # file for running unit tests
    with open(changed_app_file, "w") as cfg:
        line = "%s:%s" % (appfile, manifestfile)
        print(line)
        cfg.write("%s\n" % line)

    # file for app metadata for running API & UI tests
    with open(app_config_file, "w") as cfg:
        json_data = json.dumps([data], indent=4)
        print(json_data)
        cfg.write("%s\n" % json_data)


def generate_all_partner_app_config(unique_file_suffix, changed_files_path):
    with open(changed_files_path, "r") as fp:
        changed_app_files = fp.readlines()
        filtered_app_files = set()

        for filepath in changed_app_files:
            filepath = filepath.strip()
            if filepath and filepath.endswith(".json"):
                filename = os.path.basename(filepath)
                if filename.endswith(".manifest.json"):
                    appfile = get_normalized_path(filepath.replace(".manifest", ""))
                    manifestfile = get_normalized_path(filepath)
                else:
                    appfile = get_normalized_path(filepath)
                    manifestfile = get_normalized_path(filepath.replace(".json", ".manifest.json"))
                if os.path.isfile(appfile) and os.path.isfile(manifestfile):
                    filtered_app_files.add("%s:%s" % (appfile, manifestfile))
                else:
                    print("Skipping line %s appfile: %s manifestfile: %s doesn't exists" % (
                        filepath, appfile, manifestfile))
            else:
                print("Skipping line  %s" % filepath)

    app_config_filepath = "app-config-%s.json" % unique_file_suffix
    changed_app_filepath = "changed-apps.txt"
    if filtered_app_files:
        all_data = []
        with open(changed_app_filepath, "w") as cfg:
            for line in filtered_app_files:
                appfile, manifestfile = line.split(":")
                all_data.append(get_app_config(manifestfile, appfile))
                cfg.write("%s\n" % line)

        with open(app_config_filepath, "w") as cfg:
            json_data = json.dumps(all_data, indent=4)
            print(json_data)
            cfg.write("%s\n" % json_data)
        print("generated files %s %s" % (changed_app_filepath, app_config_filepath))
    else:
        # generating empty files
        open(changed_app_filepath, 'a').close()
        open(app_config_filepath, 'a').close()
        print("No app file changes found")


def filter_app_files(changed_app_files, all_app_config):
    # this script generates array of apps which needs to be tested

    filtered_full_app_list = set()

    file_mapper = {}
    with open(all_app_config) as fp:
        app_files = fp.readlines()

    for line in app_files:
        line = line.strip()
        # filters apps which are commented + PS apps
        if line and not line.startswith(EXCLUDED_APP_PREFIXES):
            appfile, manifestfile = line.split(":")
            file_mapper[appfile] = line
            file_mapper[manifestfile] = line
        else:
            print("Skipping line from full_app_list.txt: %s" % line)

    for filepath in changed_app_files:
        filepath = filepath.replace("src/main/app-package/", "").strip()
        # filters files using full_app_list.txt to filter deprecated json files
        if filepath in file_mapper:
            filtered_full_app_list.add(file_mapper[filepath])
        else:
            print("Changed File: %s Does not exist in full_app_list.txt: %s" % (filepath, filepath in file_mapper))

    return list(filtered_full_app_list)


def generate_appdev_app_config(unique_file_suffix, changed_files_path=None):
    content_dir_path = get_content_dirpath()
    if changed_files_path is not None:
        with open(changed_files_path, "r") as fp:
            changed_app_files = fp.readlines()
        filtered_app_files = filter_app_files(changed_app_files, os.path.join(get_content_dirpath(),
                                                                              "bin", ALL_APPS_FILENAME))
    else:
        # if not filepath is specified config is generated for all apps
        all_app_config = os.path.join(content_dir_path,
                                      "bin", ALL_APPS_FILENAME)
        with open(all_app_config, "r") as all_apps:
            app_list = all_apps.readlines()

        filtered_app_files = filter(lambda x: x and x.strip() and not (
            x.startswith(EXCLUDED_APP_PREFIXES)),
                                    app_list)
        for line in app_list:
            if line.startswith(EXCLUDED_APP_PREFIXES):
                print("Skipping line from full_app_list.txt: %s" % line)

        filtered_app_files = map(lambda x: x.strip(), filtered_app_files)

    changed_apps_file = "changed-apps-%s.txt" % unique_file_suffix
    changed_app_filepath = os.path.join(content_dir_path, "test", changed_apps_file)
    app_config_file = "app-config-%s.json" % unique_file_suffix
    app_config_filepath = os.path.join(content_dir_path, "test", app_config_file)
    all_data = []
    with open(changed_app_filepath, "w") as cfg:
        for line in filtered_app_files:
            appfile, manifestfile = line.split(":")
            appfile = os.path.join(content_dir_path, "src", "main", "app-package", appfile)
            manifestfile = os.path.join(content_dir_path, "src", "main", "app-package", manifestfile)
            all_data.append(get_app_config(manifestfile, appfile))
            cfg.write("%s\n" % line)

    with open(app_config_filepath, "w") as cfg:
        json_data = json.dumps(all_data, indent=4)
        print(json_data)
        cfg.write("%s\n" % json_data)
    print("generated files %s %s" % (changed_app_filepath, app_config_filepath))