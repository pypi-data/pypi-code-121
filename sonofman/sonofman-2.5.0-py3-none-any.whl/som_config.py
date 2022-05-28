#!/usr/bin/env python3

import configparser
import os
import sys
import pkg_resources
import shutil
import sonofman.som_util as som_util


""" 
Snap:
* System info orig:  /snap/bible-multi-the-son-of-man/x1/lib/python3.8/site-packages/sonofman/data/sonofman.ini
* System info used:  /home/<user>/snap/bible-multi-the-son-of-man/x1/.local/share/bible-multi-the-son-of-man/sonofman.ini

PyCharm:
* System info orig:  /home/<user>/Git/BibleMultiTheSonOfMan/sonofman/data/sonofman.ini
* System info used:  /home/<user>/.local/share/bible-multi-the-son-of-man/sonofman.ini

Flatpak:
* System info orig:  /app/lib/python3.9/site-packages/sonofman/data/sonofman.ini
* System info used:  /home/<user>/.var/app/org.hlwd.sonofman/data/sonofman.ini
"""


class SomConfig:
    def __init__(self):
        self.somutil = som_util.SomUtil
        self.is_flatpak = False
        self.path = ""  # path_to_data

        som_path_ini = pkg_resources.resource_filename('sonofman.data', 'sonofman.ini')
        som_path_db = pkg_resources.resource_filename('sonofman.data', 'bible.db')
        self.somutil.print("* System info orig: {0}".format(som_path_ini))

        # Create config if not exists.
        # Dependant of system: linux, mac...
        # If error => don't try to create config, but use the read only version
        self.platform = sys.platform.upper()  # LINUX
        if self.platform == "LINUX":
            env = os.environ
            home = env.get("HOME")

            xdg_data_home = env.get("XDG_DATA_HOME")
            self.somutil.print("* XDG_DATA_HOME: {0}".format(xdg_data_home))
            if xdg_data_home is None:
                self.is_flatpak = False
            else:
                self.is_flatpak = True if xdg_data_home.find("/.var/app/org.hlwd.sonofman/data") >= 0 else False

            self.path = "{0}/.var/app/org.hlwd.sonofman/data".format(home) if self.is_flatpak else "{0}/.local/share/bible-multi-the-son-of-man".format(home)
            ini_fullpath = "{0}/sonofman.ini".format(self.path)
            db_fullpath = "{0}/bible.db".format(self.path)

            som_path_ini = ini_fullpath
            self.somutil.print("* System info used: {0}".format(som_path_ini))

            # Create files
            is_db_file_exists = os.path.exists(db_fullpath)
            if not is_db_file_exists:
                os.makedirs(self.path, mode=0o777, exist_ok=True)
                shutil.copy(som_path_db, db_fullpath)

            is_ini_file_exists = os.path.exists(ini_fullpath)
            if not is_ini_file_exists:
                os.makedirs(self.path, mode=0o777, exist_ok=True)
                contentfile = """[PREFERENCES]
locale = "en"
alt_locale = "en"
use_colors = "0"
bible_prefered = "k"
history_current = "0"
bible_multi = "k"
color_k = "A_NORMAL#COLOR1"
color_v = "A_NORMAL#COLOR2"
color_l = "A_NORMAL#COLOR5"
color_d = "A_DIM#COLOR5"
color_a = "A_DIM#COLOR5"
color_o = "A_NORMAL#COLOR1"
color_s = "A_NORMAL#COLOR1"
color_2 = "A_NORMAL#COLOR1"
color_highlight_search = "A_REVERSE#"
no_color_k = "A_NORMAL#"
no_color_v = "A_NORMAL#"
no_color_l = "A_NORMAL#"
no_color_d = "A_NORMAL#"
no_color_a = "A_NORMAL#"
no_color_o = "A_NORMAL#"
no_color_s = "A_NORMAL#"
no_color_2 = "A_NORMAL#"
no_color_highlight_search = "A_REVERSE#"

[HISTORY]
0 = "k#ART_APP_HELP_BEGINNING"
"""
                configfile = open(ini_fullpath, 'x')
                configfile.write(contentfile)
                configfile.close()

        # General: after creation of file or not
        self.som_path_ini = som_path_ini

        self.config = configparser.ConfigParser()
        self.config.read(som_path_ini)

        try:
            self.somutil.print("* System path: {0}".format(sys.path))
        finally:
            pass

    def get_option(self, section, option, lst_valid_values, default_value):
        # noinspection PyBroadException
        try:
            value = self.config[section][option]
            value = value.replace("\"", "")
            if lst_valid_values is not None and value not in lst_valid_values:
                value = default_value
        except Exception as ex:
            self.somutil.print("! Unable to load parameter ({1}): {0}".format(ex, option))
            return default_value
        return value

    def set_option(self, section, option, value):
        try:
            self.config[section][option] = '"{0}"'.format(value)
        except Exception as ex:
            self.somutil.print("! Unable to set parameter ({1}): {0}".format(ex, option))

    def save_config(self):
        try:
            configfile = open(self.som_path_ini, 'w')
            self.config.write(configfile)
            configfile.close()
        except Exception as ex:
            self.somutil.print("! Unable to save config: {0}".format(ex))


"""
Future<String> _getInternalDatabasePath() async {
  try {
    if (Platform.isLinux) {
      final Map env = Platform.environment;
      final String home = env["HOME"];
      final String linuxPath = join(home, ".local/share/bible-multi-the-life");
      await SQFLITE_FFI.databaseFactoryFfi.setDatabasesPath(linuxPath);
    }
  } catch(ex) {
    if (P.isDebug) print(ex);
  }
  return (Platform.isLinux)
      ? await SQFLITE_FFI.databaseFactoryFfi.getDatabasesPath()
      : await SQFLITE.getDatabasesPath();
}
"""
"""
DB CLEANING:

delete from clipboard;
delete from cachetab;
delete from biblenote;
"""
