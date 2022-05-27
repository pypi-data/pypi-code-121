'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : SubType.py
    Classe SubType :
        Classe enfant de ClassIdName, contient la fonction getSubType
'''
import magic

from src.ClassIdName import ClassIdName
import magic
class SubType(ClassIdName):
    @staticmethod
    def getSubType(p) -> str:
        '''
        Permet de récupérer le type d'un fichier
        
        Retourne:
            - le type du fichier
        '''
        return magic.from_file(p,mime=True).split("/")[1]