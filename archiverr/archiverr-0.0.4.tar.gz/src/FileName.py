'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : FileName.py
    Classe FileName :
        Classe enfant de ClassIdName, contient la fonction getFileName
'''
from src.ClassIdName import ClassIdName
from os import path
class FileName(ClassIdName):
    @staticmethod
    def getFileName(p) -> str:
        '''
        Permet de récupérer le nom d'un fichier

        Retourne:
            - le nom du fichier
        '''
        return path.basename(path.splitext(p)[0])

