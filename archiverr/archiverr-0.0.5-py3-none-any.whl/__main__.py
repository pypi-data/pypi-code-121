'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : __main__.py
    Contient le programme principal
'''
from src import myConfig
#from src import commands
from src.Utilities import Utilities
from src.Resource import Resource
from src.FolderImport import FolderImport
from src.Archive import Archive
import src.Constants as Constants

from toml import load
from datetime import datetime, timezone
from time import mktime
import getopt
import sys
from os import system
from os.path import exists, abspath, isdir, isfile

def main():
    '''
    Main function of Archiver.
    '''
    # Remove 1st argument from the
    # list of command line arguments
    commands = load(open(Constants.NAME_OF_COMMANDS_FILE))
    values = sys.argv[1:]
    
    
    # Options
    lstCommands = commands["commands"]["names"]
 

    # Long options
    #options = commands["commands"]["long_options"]


    try:
        #arguments, values = getopt.getopt(values,lstCommands) #options
        if len(values) == 0 or values[0] not in lstCommands:
            Utilities.displayManPage()
            sys.exit(0)
        currentCmd = values[0]

        # Commande création d'une nouvelle archive
        if currentCmd == commands["new"]["name"]:
            nameHidden = Utilities.getHiddenArchiveName(values[1])
            if Utilities.checkIfArchiveExist(nameHidden):
                raise Exception(Constants.MESSAGE_ARCHIVE_ALREADY_EXIST)
            Archive(nameHidden)
        
        # Commande ajout d'un fichier ou dossier à une archive
        elif currentCmd == commands["import"]["name"]:
            Utilities.checkCurrentArchive()
            absPath = abspath(values[1])
            nameOfArchive = myConfig.getOption(
                Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_CURRENT_ARCHIVE_NAME)

            Utilities.checkPath(absPath)
            if not exists(absPath):
                raise Exception(Constants.MESSAGE_FOLDER_FILE_DOES_NOT_EXIST)
            if isdir(absPath):
                Archive(nameOfArchive).archiveFolder(FolderImport(absPath))

            elif isfile(absPath):
                Archive(nameOfArchive).archiveResource(
                    Resource(absPath, False))
        
        # Commande fusion de deux archives
        elif currentCmd == commands["merge"]["name"]:
            Utilities.checkCurrentArchive()
            nameHidden1 = myConfig.getOption(
                Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_CURRENT_ARCHIVE_NAME)
            nameHidden2 = Utilities.getHiddenArchiveName(values[1])
            if not Utilities.checkIfArchiveExist(nameHidden1):
                raise Exception(Constants.MESSAGE_ARCHIVE_FIRST_DOES_NOT_EXIST)

            if not Utilities.checkIfArchiveExist(nameHidden2):
                raise Exception(
                    Constants.MESSAGE_ARCHIVE_SECOND_DOES_NOT_EXIST)

            Archive(nameHidden1).mergeTwoArchive(Archive(nameHidden2))
        

        elif currentCmd == commands["search"]["name"]:
            Utilities.checkCurrentArchive()
            filters = dict()
            # On enlève le premier élément de la liste, car c'est le nom de la commande
            values.pop(0)



            if len(values) != 0:
                filters = dict(x.split(':') for x in values)                     
            myArchive = Archive(myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_CURRENT_ARCHIVE_NAME))
            resources = myArchive.search(filters)
            myArchive.saveToExtract(resources)
            for res in resources:
                print(res.fileName.value+res.extension.value)

            if "-e" in values:
                absPath = abspath(values.index("-e")+1)
                nameOfArchive = myConfig.getOption(
                    Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_CURRENT_ARCHIVE_NAME)
                myArchive = Archive(nameOfArchive)
                metadataIds = myArchive.loadFromFileToExtract()
                metadatas = myArchive.myDb.getMetadatasByIds(metadataIds)
                myArchive.extractResources(metadatas,absPath)
        
        elif currentCmd == commands["extract"]["name"]:
            Utilities.checkCurrentArchive()
            metadatas = []
            absPath = abspath(values[0])
            nameOfArchive = myConfig.getOption(
                Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_CURRENT_ARCHIVE_NAME)
            myArchive = Archive(nameOfArchive)
            metadataIds = myArchive.loadFromFileToExtract()
            metadatas = myArchive.myDb.getMetadatasByIds(metadataIds)
            myArchive.extractResources(metadatas,absPath)
            pass

        elif currentCmd == commands["select"]["name"]:
            nameHidden = Utilities.getHiddenArchiveName(values[1])
            if not Utilities.checkIfArchiveExist(nameHidden):
                raise Exception(Constants.MESSAGE_ARCHIVE_DOES_NOT_EXIST)
            myConfig.setOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_CURRENT_ARCHIVE_NAME, nameHidden)
            pass
        
        elif currentCmd == commands["man"]["name"]:
            nameOfCmd = ""
            if len(values) != 0:
                nameOfCmd = values[0]
            Utilities.displayManPage(nameOfCmd)
        
        elif currentCmd == commands["serve"]["name"]:
            Utilities.startServer()
            pass

        elif currentCmd  == commands["list"]["name"]:
            for archive in Utilities.listArchivesInFolder():
                print(archive)
            pass

    except Exception as err: #Exepction
        # output error, and return with an error code
        Utilities.displayManPage()
        if err != None:
            print(err)
            sys.exit() 
        else:
            
            sys.exit()
        pass






