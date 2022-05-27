'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : PathName.py
    Classe PathName :
        Classe enfant de ClassIdName, contient la fonction getPathName
'''
from src.ClassIdName import ClassIdName
from os import path

class PathName(ClassIdName): 

    def getFolders(self) -> list:
        '''
        Permet de récupérer les dossiers d'un dossier
        
        Retourne:
            - la liste des dossiers
        '''
        return self.value.split("/")


    @staticmethod
    def getPathName(p) -> str:
        '''
            Permet de récupérer le chemin du repertoire du fichier
        
            Paramètres:
                - p: le chemin du fichier
            
            Retourne:
                - le chemin du repertoire du fichier
        '''
        return path.dirname(p)