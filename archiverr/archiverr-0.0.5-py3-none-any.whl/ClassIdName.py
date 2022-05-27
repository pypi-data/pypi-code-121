'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : ClassIdName.py
    Classe ClassIdName : 
        Classe mère des classes contenant seulement un id et une valeur
'''
class ClassIdName: 
    def __init__(self, id, value):
        self.id = id
        self.value = value
    def __str__(self):
        return str(self.id) + " " + self.value

    def toJson(self) -> str:
        try : 
            return '{"id": "'+ str(self.id)+'", "name": "'+self.value+'"}'
        except :
            print("Error in Extension.toJson()")