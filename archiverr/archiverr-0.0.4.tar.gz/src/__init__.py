'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : __init__.py
    Initialise la configuration
'''
from src.Config import Config
import src.Constants as Constants
from toml import load
myConfig = Config()
#commands = load(open(Constants.NAME_OF_COMMANDS_FILE))