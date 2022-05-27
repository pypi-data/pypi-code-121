'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : Constants.py
    Fichier contenant toutes les constantes de l'application
'''
from sys import platform
from getpass import getuser

NAME_OF_CONFIG_FILE = "config.ini"
NAME_OF_COMMANDS_FILE = "commands.toml"
NAME_OF_SQLITE_DB = "archiver.db"
NAME_OF_SQL_CONSTRUCT = "./src/archiver.sql"
NAME_OF_FOLDER_ARCHIVE = "Archives"
NAME_OF_SECTION_ARCHIVE = "archive"
NAME_OF_EXCLUDE_EXTENSIONS = "exclude_extensions"
NAME_OF_EXCLUDE_FOLDERS = "exclude_folders"
NAME_OF_CURRENT_ARCHIVE_NAME = "current_archive_name"
NAME_OF_DEFAULT_ARCHIVE_DIR = "default_archive_dir"
NAME_OF_DEFAULT_EXTENSION_COMPRESSION = "default_extension_compression"
HIDDEN_ARCHIVE_PREFIX = "" #.
PATH_OF_CONFIG_FILE = ""
PATH_TO_SERVER = "./src/flask_app"

# Metadata types
TYPE_UNIVERSAL = "universal"
TYPE_SPECIFIC = "specific"

# Check operating system
if platform == "win32":
    DEFAULT_ARCHIVE_DIR = "C:/Users/{}/{}".format(getuser(), HIDDEN_ARCHIVE_PREFIX+NAME_OF_FOLDER_ARCHIVE)
elif platform == "linux":
    DEFAULT_ARCHIVE_DIR = "/home/{}/{}".format(getuser(),HIDDEN_ARCHIVE_PREFIX+NAME_OF_FOLDER_ARCHIVE)


DEFAULT_ARCHIVE_URL = "http://localhost/archives/"
DEFAULT_EXTENSION_COMPRESS = ".7z"
DEFAULT_PATH_ARCHIVER = "Archiver"

DICT_OF_CONFIG_SECTIONS = {
    "archive": {
        NAME_OF_CURRENT_ARCHIVE_NAME: "",
        NAME_OF_DEFAULT_ARCHIVE_DIR: DEFAULT_ARCHIVE_DIR,
        "default_archive_url": "",
        NAME_OF_DEFAULT_EXTENSION_COMPRESSION: DEFAULT_EXTENSION_COMPRESS
    }
}


# Region messages for the user

MESSAGE_ARCHIVE_ALREADY_EXIST = "L'archive existe déjà."
MESSAGE_ARCHIVE_DOES_NOT_EXIST = "L'archive n'existe pas."
MESSAGE_ARCHIVE_CREATED = "L'archive a été créée."
MESSAGE_ARCHIVE_FIRST_DOES_NOT_EXIST = "La première archive n'existe pas."
MESSAGE_ARCHIVE_SECOND_DOES_NOT_EXIST = "La deuxième archive n'existe pas."
MESSAGE_FOLDER_FILE_DOES_NOT_EXIST = "Le dossier/ressource n'existe pas."
MESSAGE_NO_CURRENT_ARCHIVE = "Aucune archive n'est sélectionnée."

# Endregion

