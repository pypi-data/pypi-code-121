'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : Resource.py
    Classe Resource :
        Classe contenant un sha1 et une ou des métadonnées
'''
from src.Metadata import Metadata
from src.Extension import Extension
from src.PathName import PathName
from src.FileName import FileName
from src.Type import Type
from datetime import datetime
import hashlib
import json

'''
import shutil
import time
import py7zr
'''


class Resource():

    def __init__(self, p, isCompressed, m: Metadata = None, type : Type = None) -> None:
        self.path = p
        #self.allMetadatas = []
        
        #self.mime = None
        self.universalMetadata = None

        # Ce champs sert à la fusion pour stocker toutes les métadonnées appartenant à la même ressource
        self.allMetadatas = []
        if not isCompressed:
            self.sha1 = self.__getSha1(self.path)
            self.type = Type(-1, Type.getType(self.path))
            self.universalMetadata = Metadata(
                FileName(-1, FileName.getFileName(self.path)), 
                Extension(-1, Extension.getExtension(self.path)), 
                Metadata.getCreationDate(self.path), 
                Metadata.getModificationDate(self.path), 
                0,#Metadata.getSizeCompressed(self.path), 
                Metadata.getSizeUncompressed(self.path),
                PathName(-1, PathName.getPathName(self.path)),
                self.sha1) 
            #self.allMetadatas.append(m)
            Metadata.deleteMetadataInResource(p)
        else:
            self.sha1 = p
            self.type = type
            #self.allMetadatas.append(m)
            self.universalMetadata = m
        pass

    def __getSha1(self, fileName) -> str:
        '''
            Permet de récupérer le sha1 d'un fichier

            Retourne:
                - le sha1 du fichier
        '''
        sha1 = hashlib.sha1()
        with open(fileName, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()


    def __getattr__(self, attr):
        '''
            Permet de récupérer les attributs d'un objet Resource

            Paramètres:
                - attr: l'attribut à récupérer

            Retourne:
                - l'attribut de l'objet
        '''
        '''
        TO DO:
            - mettre un match attr par classe metadata
              pour prendre en compte d'autre metadonnées dans le futur
              Mettre constante de chaque champ dans la classe Metadata pour trouver directement le champ
        '''
        match attr:
            case "typeName":
                return self.type.value
            case "fileName":
                return self.universalMetadata.fileName
            case "pathName":
                return self.universalMetadata.pathName
            case "sizeUncompressed":
                return self.universalMetadata.sizeUncompressed
            case "extension":
                return self.universalMetadata.extension
            case "creationDate":
                return self.universalMetadata.creationDate
            case "modificationDate":
                return self.universalMetadata.modificationDate
            case "createdAt":
                return self.universalMetadata.createdAt

    def toJSON(self):
        '''
            Permet de convertir un objet Resource en JSON

            Paramètres:
                - self: l'objet à convertir

            Retourne:
                - le JSON de l'objet
        '''
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def toDICT(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __eq__(self, other) -> bool:
        # Ajouter comparaison des méta-données @TODO
        return self.sha1 == other.sha1

    def __str__(self) -> str:
        return self.path + " : " + self.sha1
