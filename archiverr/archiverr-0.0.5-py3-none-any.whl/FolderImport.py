'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : FolderImport.py
    Classe FolderImport :
        Classe permettant d'importer un dossier, il contient une liste de fichiers lors de l'instanciation via son path
'''
import os
from src.Resource import Resource
from src.Extension import Extension
import src.Constants as Constants
from src import myConfig

class FolderImport : 
    def __init__(self, path) -> None:
        '''
            Constructeur de la classe FolderImport

            Paramètres:
                - path: le chemin du dossier à parcourir
        '''
        self.path : str = path
        self.nbResource : int = 0
        self.resources : list = self.__getResources()
        pass

    def __getResources(self) -> list:
        '''
            Permet de récupérer les ressources d'un dossier

            Retourne:
            - la liste des ressources
        '''

        excludeExtensions = myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_EXCLUDE_EXTENSIONS).split(",")
        excludeFolders = myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_EXCLUDE_FOLDERS).split(",")
        resources = []
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in excludeFolders]
            for file in files:
                extension = Extension.getExtension(root + "/" + file)
                if extension not in excludeExtensions:
                    self.nbResource += 1
                    resources.append(Resource(os.path.join(root, file), False))
                
        return resources