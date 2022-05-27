'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : Type.py
    Classe Type :
        Classe enfant de ClassIdName, contient la fonction getType
'''
import magic
from src.ClassIdName import ClassIdName
class Type(ClassIdName):

    @staticmethod
    def getType(p) -> str:
        '''
        Permet de récupérer le type d'un fichier
        
        Retourne:
            - le type du fichier
        '''
        return magic.from_file(p,mime=True).split("/")[0]