'''
AUTEUR : Théo Hurlimann
LIEU : CFPT Informatique Genève
DATE : avril 2022
PROJET: ARCHIVER
VERSION : 1.0
FICHIER : Bdd.py
    Classe Bdd : 
        Contient la connection à la base de données ansi que les fonctions de gestion de la base de données
'''
from src import Constants
from src.Resource import Resource
from src.Metadata import Metadata
from src.Extension import Extension
from src.FileName import FileName
from src.PathName import PathName
from src.Type import Type
from src.FolderName import FolderName
import src.Archive as Archive




import sqlite3, pandas as pd
from os import mkdir, path, makedirs, chmod
from datetime import date, timedelta
from src.Utilities import Utilities


class Bdd:
    def __init__(self, pathArchive) -> None:
        self.pathFile = pathArchive + "/" + Constants.NAME_OF_SQLITE_DB
        self.pathArchive = pathArchive
        self.connect = None
        self.cursor = None
        self.connectToDb()
        pass
    
    #region SQLITE3

    def connectToDb(self):
        """Permet d'initialiser la connexion à la base de données"""
        if not path.isfile(self.pathFile):
            open(self.pathFile, 'a').close()
            self.createDbTables()
        else:
            self.connect = sqlite3.connect(self.pathFile)
            self.cursor = self.connect.cursor()

    
    def createDbTables(self) -> bool:
        """Crée les tables de la base de données
        
        Retourne:
            Bool : True si la création a réussi, sinon False
        """
        try:
            self.connect = sqlite3.connect(self.pathFile)
            self.cursor = self.connect.cursor()
            sql_file = open(Constants.NAME_OF_SQL_CONSTRUCT, 'r')
            sql_as_string = sql_file.read()
            self.cursor.executescript(sql_as_string)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    #endregion

    #region Exist

    def pathNameExist(self, pathName : PathName) -> bool:
        """Permet de savoir si un chemin existe
        
        Paramètres:
            Pathname (PathName): le chemin à vérifier
        
        Retourne:
            Bool : True si le chemin existe
            Bool : False si le chemin n'existe pas
        """
        self.cursor.execute("select pathName from pathNames where pathName = ?;", (pathName.value,))
        if self.cursor.fetchone() is None:
            return False
        return True

    def folderNameExist(self, folder : FolderName) -> bool:
        """Permet de savoir si un dossier existe
        
        Paramètres:
            folderName (FolderName): le dossier à vérifier
        
        Retourne:
            Bool : True si le dossier existe
            Bool : False si le dossier n'existe pas
        """
        self.cursor.execute("select name from folderNames where name = ?;", (folder.value,))
        if self.cursor.fetchone() is None:
            return False
        return True
    
    def fileNameExist(self, fileName : FileName) -> bool:
        """Permet de savoir si un fichier existe
        
        Paramètres:
            fileName (FileName): le fichier à vérifier
            
        Retourne:
            Bool : True si le fichier existe
            Bool : False si le fichier n'existe pas
        """
        self.cursor.execute("select name from fileNames where name = ?;", (fileName.value,))
        if self.cursor.fetchone() is None:
            return False
        return True

    def extensionExist(self, extension : Extension) -> bool:
        """Permet de savoir si une extension existe
        
        Paramètres:
            extension (Extension): l'extension à vérifier
        
        Retourne:
            Bool : True si l'extension existe
            Bool : False si l'extension n'existe pas
        """
        self.cursor.execute("select name from extensions where name = ?;", (extension.value,))
        if self.cursor.fetchone() is None:
            return False
        return True

    def typeExist(self, type : Type) -> bool:
        """Permet de savoir si un type existe

        Paramètres:
            type (Type): le type à vérifier
        
        Retourne:
            Bool : True si le type existe
            Bool : False si le type n'existe pas
        """
        self.cursor.execute("select name from Types where name = ?;", (type.value,))
        if self.cursor.fetchone() is None:
            return False
        return True

    def subTypeExist(self, subType : Type) -> bool:
        """Permet de savoir si un sous type existe
        
        Paramètres:
            subType (Type): le sous type à vérifier
        
        Retourne:
            Bool : True si le sous type existe
            Bool : False si le sous type n'existe pas
        """
        self.cursor.execute("select name from SubTypes where name = ?;", (subType.value,))
        if self.cursor.fetchone() is None:
            return False
        return True

    def resourceExist(self,r : Resource):
        """Permet de savoir si un ressource existe
        
        Paramètres:
            r (Resource): la ressource à vérifier
        
        Retourne:
            Bool : True si la ressource existe
            Bool : False si la ressource n'existe pas
        """
        self.cursor.execute("select sha1 from Resources where sha1 = ?;", (r.sha1,))
        result = self.cursor.fetchone()
        if result is None:
            return False
        return True

    def metadataExist(self, m : Metadata) -> bool:
        """Permet de savoir si une metadata existe avec toutes les informations

        Paramètres:
            m (Metadata): la metadata à vérifier
        
        Retourne:
            Bool : True si la metadata existe
            Bool : False si la metadata n'existe pas
        """
        self.cursor.execute("SELECT fileName_id, extension_id, creationDate, modificationDate, sizeCompressed, sizeUncompressed, pathName_id from metadatas where fileName_id = ? and extension_id = ? and creationDate = ? and modificationDate = ? and sizeCompressed = ? and sizeUncompressed = ? and pathName_id = ?", 
        (m.fileName.id, m.extension.id, m.creationDate, m.modificationDate, m.sizeCompressed, m.sizeUncompressed, m.pathName.id))

        result = self.cursor.fetchone()
        if result is None: #len(result) == 0
            return False
        return m

    def folderNamePathNameExist(self, folderName : FolderName, pathName : PathName) -> bool:
        """Permet de savoir si le dossier et le chemin sont associés

        Paramètres:
            folderName (FolderName): le dossier à vérifier
            pathName (PathName): le chemin à vérifier
        
        Retourne:
            Bool : True si le dossier et le chemin sont associés
            Bool : False si le dossier et le chemin ne sont pas associés
        """
        self.cursor.execute("select folderName_id, pathName_id from folderNamePathName where folderName_id = ? and pathName_id = ?;", (folderName.id, pathName.id))
        if self.cursor.fetchone() is None:
            return False
        return True

    def folderMetadataExist(self, folder : FolderName, m : Metadata) -> bool:
        """Permet de savoir si le dossier et la metadata sont associés

        Paramètres:
            folder (FolderName): le dossier à vérifier
            m (Metadata): la metadata à vérifier

        Retourne:
            Bool : True si le dossier et la metadata sont associés
            Bool : False si le dossier et la metadata ne sont pas associés
        """
        self.cursor.execute("select folderName_id, metadata_id from folderNameMetadata where folderName_id = ? and metadata_id = ?;", (folder.id,m.id))
        if self.cursor.fetchone() is None:
            return False
        return True
    
    def folderNameIdPathNameIdExist(self, folderNameId : int, pathNameId : int) -> bool:
        """Permet de savoir si le dossier et le chemin sont associés

        Paramètres:
            folderNameId (int): l'id du dossier à vérifier
            pathNameId (int): l'id du chemin à vérifier
        
        Retourne:
            Bool : True si le dossier et le chemin sont associés
            Bool : False si le dossier et le chemin ne sont pas associés
        """
        self.cursor.execute("select folderName_id, pathName_id from folderNamePathName where folderName_id = ? and pathName_id = ?;", (folderNameId, pathNameId))
        if self.cursor.fetchone() is None:
            return False
        return True

    def folderNameIdMetadataIdExist(self, folderNameId : int, metadataId : int) -> bool:
        """Permet de savoir si le dossier et la metadata sont associés

        Paramètres:
            folderNameId (int): l'id du dossier à vérifier
            metadataId (int): l'id de la metadata à vérifier

        Retourne:
            Bool : True si le dossier et la metadata sont associés
            Bool : False si le dossier et la metadata ne sont pas associés
        """
        self.cursor.execute("select folderName_id, metadata_id from folderNameMetadata where folderName_id = ? and metadata_id = ?;", (folderNameId, metadataId))
        if self.cursor.fetchone() is None:
            return False
        return True
    #endregion

    #region Add
    def addTypes(self, types : list) -> bool:
        """Permet d'ajouter une liste de type
           Effectue une vérification pour savoir si le type existe déjà

        Paramètres:
            types (list): la liste de type à ajouter

        Retourne:
            Bool : True si la liste de type a été ajoutée
            Bool : False si la liste de type n'a pas été ajoutée
        """
        try:
            for type in types:
                self.addType(type)
            return True
        except sqlite3.Error as e:
            print(e)
            return False
    
    def addType(self, type : Type) -> bool:
        """Permet d'ajouter un type
           Effectue une vérification pour savoir si le type existe déjà

        Paramètres:
            type (Type): le type à ajouter

        Retourne:
            Bool : True si le type a été ajouté
            Bool : False si le type n'a pas été ajouté
        """
        try:
            if not self.typeExist(type):
                self.cursor.execute("insert into types (name) values (?);", (type.value,))
                self.connect.commit()
                type.id = self.cursor.lastrowid
            else:
                type = self.getTypeByName(type)

            return type

        except sqlite3.Error as e:
            print(e)
            return False

    def addExtensions(self, extensions : list) -> bool:
        """Permet d'ajouter une liste d'extension
           Effectue une vérification pour savoir si l'extension existe déjà

        Paramètres:
            extensions (list): la liste d'extension à ajouter

        Retourne:
            Bool : True si la liste d'extension a été ajoutée
            Bool : False si la liste d'extension n'a pas été ajoutée
        """
        try:
            for extension in extensions:
                self.addExtension(extension)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def addExtension(self, extension : Extension) -> bool:
        """Permet d'ajouter une extension
           Effectue une vérification pour savoir si l'extension existe déjà

        Paramètres:
            extension (Extension): l'extension à ajouter

        Retourne:
            Bool : True si l'extension a été ajoutée
            Bool : False si l'extension n'a pas été ajoutée
        """
        try:
            if not self.extensionExist(extension):
                self.cursor.execute("insert into extensions (name) values (?);", (extension.value,))
                self.connect.commit()
                extension.id = self.cursor.lastrowid
            else :
                extension = self.getExtensionByName(extension)

            return extension
        except sqlite3.Error as e:
            print(e)
            return False
    
    def addFileNames(self, fileNames : list) -> bool:
        """Permet d'ajouter une liste de nom de fichier
           Effectue une vérification pour savoir si le nom de fichier existe déjà

        Paramètres:
            fileNames (list): la liste de nom de fichier à ajouter

        Retourne:
            Bool : True si la liste de nom de fichier a été ajoutée
            Bool : False si la liste de nom de fichier n'a pas été ajoutée
        """
        try:
            for fileName in fileNames:
                self.addFileName(fileName)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def addFileName(self, fileName : FileName) -> bool:
        """Permet d'ajouter un nom de fichier
           Effectue une vérification pour savoir si le nom de fichier existe déjà
        Paramètres:
            fileName (FileName): le nom de fichier à ajouter

        Retourne:
            Bool : True si le nom de fichier a été ajouté
            Bool : False si le nom de fichier n'a pas été ajouté
        """
        try:
            if not self.fileNameExist(fileName):
                self.cursor.execute("insert into fileNames (name) values (?);", (fileName.value,))
                self.connect.commit()
                fileName.id = self.cursor.lastrowid
            else :
                fileName = self.getFileNameByName(fileName)
            
            return fileName
        except sqlite3.Error as e:
            print(e)
            return False
    
    def addFolderNameIdPathNameId(self, folderNameId : int, pathNameId : int) -> bool:
        """Permet de lier un dossier à un chemin

        Paramètres:
            folderNameId (int): l'id du folderName à lier
            pathNameId (int): l'id du pathName à lier

        Retourne:
            bool: True si le lien a été ajouté
            bool: False si le lien n'a pas été ajouté
        """
        try:
            if not self.folderNameIdPathNameIdExist(folderNameId, pathNameId):
                self.cursor.execute("insert into folderNamePathName (folderName_id, pathName_id) values (?,?);", (folderNameId, pathNameId))
                self.connect.commit()
            return True
        except sqlite3.Error as e:
            print(e)
            return False
    
    def addFolderNameIdMetadataId(self, folderId : int, mId : int) -> bool:
        """Permet de lier un dossier à une metadata
        
        Paramètres:
            folderId (int): l'id du dossier à lier
            mId (int): l'id de la metadata à lier
            
        Retourne:
            bool: True si le lien a été ajouté
            bool: False si le lien n'a pas été ajouté
        """
        try:
            if not self.folderNameIdMetadataIdExist(folderId, mId):
                self.cursor.execute("insert into folderNameMetadata (folderName_id, metadata_id) values (?,?);", (folderId, mId))
                self.connect.commit()
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def addFolderNames(self, folderNames : list) -> list:
        """Permet d'ajouter une liste de dossier
        
        Paramètres:
            folderNames (list): la liste de dossier à ajouter
        
        Retourne:
            list: la liste des dossiers ajoutés
            Bool : False si la liste de dossier n'a pas été ajoutée
        """
        try:
            folders = []
            for folderName in folderNames:
                if folderName != "":
                    folders.append(self.addFolderName(folderName))
            return folders
        except sqlite3.Error as e:
            print(e)
            return False

    def addFolderName(self, folder : FolderName) -> bool:
        """Permet d'ajouter un dossier
        Effectue une recherche pour savoir si le dossier existe déjà

        Paramètres:
            folder (FolderName): le dossier à ajouter
        
        Retourne:
            bool: True si le dossier a été ajouté
            bool: False si le dossier n'a pas été ajouté
        """    
        try:
            if not self.folderNameExist(folder):
                self.cursor.execute("insert into folderNames (name) values (?);", ([folder.value,]))
                self.connect.commit()
                folder.id = self.cursor.lastrowid
            else:
                folder = self.getFolderNameByName(folder)
            return folder
        except sqlite3.Error as e:
            print(e)
            return False
        
    def addFolderPathName(self, f : FolderName, p : FolderName) -> bool:
        """Permet de lier un dossier à un chemin
        
        Paramètres:
            f (FolderName): le dossier à lier
            p (FolderName): le chemin à lier
        
        Retourne:
            bool: True si le dossier a été lier
            bool: False si le dossier n'a pas été lier
        """
        try:
            if not self.folderNamePathNameExist(f,p):
                self.cursor.execute("insert into folderNamePathName (folderName_id, pathName_id) values (?,?);", (f.id,p.id))
                self.connect.commit()
            return True
        except sqlite3.Error as e:
            print(e)
            return False
    
    def addFolderMetadata(self, f : FolderName, m : Metadata) -> bool:
        """Permet de lier un dossier à une metadata
            
            Paramètres:
                f (FolderName): le dossier à lier
                m (Metadata): la metadata à lier
            
            Retourne:
                bool: True si le dossier a été lier
                bool: False si le dossier n'a pas été lier
            """
        try:
            if not self.folderMetadataExist(f,m):
                self.cursor.execute("insert into folderNameMetadata (folderName_id, metadata_id) values (?,?);", (f.id,m.id))
                self.connect.commit()
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def addFoldersWithPathName(self, pathName : PathName):
        """Permet d'ajouter un dossier dans la base de données.
        Effectue une vérification pour savoir si le dossier existe déjà.
        
        Paramètres:
            pathName (PathName): le pathName contenant un chemin à ajouter
        
        Retourne:
            bool: True si le dossier a été ajouté
            bool: False si le dossier n'a pas été ajouté
        """
        try:
            folders = []
            nameFolders = pathName.getFolders()
            for name in nameFolders:
                if name != '':
                    folders.append(self.addFolderName(FolderName(-1, name) ))

            return folders
        except sqlite3.Error as e:
            print(e)
            return False

    def addPathNames(self, pathNames : list) -> bool:
        """Permet d'ajouter une liste de chemin
        Effectue une vérification pour savoir si le chemin existe déjà.

        Paramètres:
            pathNames (list): la liste de chemin à ajouter

        Retourne:
            bool: True si la liste de chemin a été ajoutée
            bool: False si la liste de chemin n'a pas été ajoutée
        """
        try:
            for pathName in pathNames:
                self.addPathName(pathName)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def addPathName(self, pathName : PathName) -> bool:
        """Permet d'ajouter un chemin
           Effectue une vérification pour savoir si le chemin existe déjà.
            
            Paramètres:
                pathName (PathName): le chemin à ajouter
    
            Retourne:
                bool: True si le chemin a été ajouté
                bool: False si le chemin n'a pas été ajouté
            """
        try:
            if not self.pathNameExist(pathName):
                self.cursor.execute("insert into pathNames (pathName) values (?);", (pathName.value,))
                self.connect.commit()
                pathName.id = self.cursor.lastrowid
            else:
                pathName = self.getPathNameByPath(pathName)
            
            return pathName
        except sqlite3.Error as e:
            print(e)
            return False

    def addResources(self,Resources : list) -> bool:
        """Permet d'ajouter une liste de resource
        Effectue une vérification pour savoir si la resource existe déjà.

        Paramètres:
            Resources (list): la liste de resource à ajouter

        Retourne:
            bool: True si la liste de resource a été ajoutée
            bool: False si la liste de resource n'a pas été ajoutée
        """
        try:
            for Resource in Resources:
                self.addResource(Resource)
            return True
        except sqlite3.Error as e:
            print(e)
            return False
    
    def addResource(self,resource : Resource) -> bool:
        """Permet d'ajouter une resource

        Paramètres:
            resource (Resource): la resource à ajouter

        Retourne:
            bool: True si la resource a été ajoutée
            bool: False si la resource n'a pas été ajoutée
        """
        try:
            added = False
            if not self.resourceExist(resource):
                self.cursor.execute("insert into Resources (sha1, type_id) values (?,?);", (resource.sha1,resource.type.id))
                self.connect.commit()
                resource.id = self.cursor.lastrowid
                added = True

            return resource, added
        except sqlite3.Error as e:
            print(e)
            return False  

    def addMetadatas(self,metadatas : Resource) -> bool:
        """Permet d'ajouter une liste de metadata
        Effectue une vérification pour savoir si la metadata existe déjà.

        Paramètres:
            r (Resource): la resource à ajouter

        Retourne:
            bool: True si la resource a été ajoutée
            bool: False si la resource n'a pas été ajoutée
        """
        try:
            for m in metadatas:
                self.addMetadata(m)
            return True
        except sqlite3.Error as e:
            print(e)
            return False
    
    def addMetadata(self, metadata : Metadata, ifadded : bool = False) -> bool:
        """Permet d'ajouter une metadata
        Effectue une vérification pour savoir si la metadata existe déjà.

        Paramètres:
            metadata (Metadata): la metadata à ajouter

        Retourne:
            bool: True si la metadata a été ajoutée
            bool: False si la metadata n'a pas été ajoutée
        """
        try:
            added = False
            if not self.metadataExist(metadata):
                self.cursor.execute("insert into metadatas (fileName_id, extension_id, creationDate, modificationDate, sizeCompressed, sizeUncompressed, pathName_id, createdAt, sha1) values (?,?,?,?,?,?,?,?,?);",
                 (metadata.fileName.id, metadata.extension.id, metadata.creationDate, metadata.modificationDate, metadata.sizeCompressed, metadata.sizeUncompressed, metadata.pathName.id, metadata.createdAt, metadata.sha1))
                self.connect.commit()
                metadata.id = self.cursor.lastrowid
                added = True
            else :
                metadata = self.getMetadataByAllFields(metadata)
            
            if ifadded :
                return metadata, added
            return metadata
            
        except sqlite3.Error as e:
            print(e)
            return False

    def addResourceWithMetadata(self, resource : Resource) -> bool:
        """Permet d'ajouter une resource avec sa metadata
        Effectue une vérification pour savoir si la resource existe déjà.

        Paramètres:
            resource (Resource): la resource à ajouter avec sa metadata

        Retourne:
            bool: True si la resource a été ajoutée
            bool: False si la resource n'a pas été ajoutée
        """
        try:
            if not self.resourceExist(resource):
                self.addResource(resource)
            self.addMetadatas(resource)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    def addResourcesWithMetadata(self, resources : list) -> bool:
        """Permet d'ajouter une liste de resource avec leur metadata
        Effectue une vérification pour savoir si la resource existe déjà.

        Paramètres:
            resources (list): la liste de resource à ajouter avec leur metadata

        Retourne:
            bool: True si la liste de resource a été ajoutée
            bool: False si la liste de resource n'a pas été ajoutée
        """
        try:
            for r in resources:
                self.addResourceWithMetadata(r)
            return True
        except sqlite3.Error as e:
            print(e)
            return False

    #endregion

    #region Get

    #region Folder
    def getAllFolderNames(self) -> list:
        """Permet de récupérer tous les noms de dossier

        Retourne:
            list: la liste de tous les noms de dossier
        """
        try:
            folders = []
            self.cursor.execute("select * from folderNames")
            result = self.cursor.fetchall()    
            for r in result:
                folders.append(FolderName(r[0], r[1]))
            return folders
        except sqlite3.Error as e:
            print(e)
            return False

    def getFolderNameByName(self, folder : FolderName) -> FolderName:
        """Permet de récupérer un nom de dossier à partir de son nom

        Paramètres:
            folder (FolderName): le nom de dossier à récupérer

        Retourne:
            FolderName: le nom de dossier récupéré
        """
        try:
            self.cursor.execute("select * from folderNames where name = ?", (folder.value,))
            result = self.cursor.fetchone()
            if result != None:
                folder.id = result[0]
                return folder
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False

    def getFolderNameById(self, folder : FolderName) -> FolderName:
        """Permet de récupérer un nom de dossier à partir de son id

        Paramètres:
            folder (FolderName): le nom de dossier à récupérer

        Retourne:
            FolderName: le nom de dossier récupéré
        """
        try:
            self.cursor.execute("select name from folderNames where id = ?", (folder.id,))
            result = self.cursor.fetchone()
            if result != None:
                folder.value = result[0]
                return folder
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False
    #endregion
    
    #region File
    def getAllFileNames(self) -> list:
        """Permet de récupérer tous les noms de fichier
            
        Retourne:
            list: la liste de tous les noms de fichier
        """
        try:
            fileNames = []
            self.cursor.execute("select * from fileNames")
            result = self.cursor.fetchall()
            for r in result:
                fileNames.append(FileName(r[0], r[1]))
            return fileNames
        except sqlite3.Error as e:
            print(e)
            return False

    def getFileNameById(self, fileName : FileName) -> FileName:
        """Permet de récupérer un nom de fichier à partir de son id
            
        Paramètres:
            fileName (FileName): le nom de fichier à récupérer
    
        Retourne:
            FileName: le nom de fichier récupéré
        """
        try:
            self.cursor.execute("select name from filenames where id = ?", (fileName.id,))
            result = self.cursor.fetchone()
            if result != None:
                fileName.value = result[0]
                return fileName
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False

    def getFileNameByName(self, fileName : FileName) -> FileName:
        """Permet de récupérer un nom de fichier à partir de son nom
        
        Paramètres:
            fileName (FileName): le nom de fichier à récupérer
    
        Retourne:
            FileName: le fichier avec son nom récupéré
        """
        try:
            self.cursor.execute("select id from fileNames where name = ?;", (fileName.value,))
            fileName.id = self.cursor.fetchone()[0]
            return fileName
        except sqlite3.Error as e:
            print(e)
            return None
    #endregion
    
    #region PathName
    def getAllPathNames(self) -> list:
        """Permet de récupérer tous les noms de chemins
        
        Retourne:
            list: la liste de tous les noms de chemins
        """
        try:
            pathNames = []
            self.cursor.execute("select * from pathNames")
            result = self.cursor.fetchall()
            for r in result:
                pathNames.append(PathName(r[0], r[1]))
            return pathNames
        except sqlite3.Error as e:
            print(e)
            return False

    def getPathNameById(self, pathName : PathName) -> PathName:
        """Permet de récupérer un nom de chemin à partir de son id

        Paramètres:
            pathName (PathName): le nom de chemin à récupérer

        Retourne:
            PathName: le nom de chemin récupéré
        """
        try:
            self.cursor.execute("select pathName from pathNames where id = ?", (pathName.id,))
            result = self.cursor.fetchone()
            if result != None:
                pathName.value = result[0]
                return pathName
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False

    def getPathNameByPath(self, pathName : PathName) -> PathName:
        """Permet de récupérer un nom de chemin à partir de son nom

        Paramètres:
            pathName (PathName): le nom de chemin à récupérer

        Retourne:
            PathName: le nom de chemin récupéré
        """
        try:
            self.cursor.execute("select id from pathNames where pathName = ?;", (pathName.value,))
            pathName.id = self.cursor.fetchone()[0]
            return pathName
        except sqlite3.Error as e:
            print(e)
            return None
    #endregion
    
    #region Type
    def getAllTypes(self) -> list:
        """Permet de récupérer tous les types

        Retourne:
            list: la liste de tous les types
        """
        try:
            types = []
            self.cursor.execute("select * from types")
            result = self.cursor.fetchall()
            for r in result:
                types.append(Type(r[0], r[1]))
            return types
        except sqlite3.Error as e:
            print(e)
            return False

    def getTypeById(self, type : Type) -> Type:
        """Permet de récupérer un type à partir de son id
        
        Paramètres:
            type (Type): le type à récupérer
            
        Retourne:
            Type: le type récupéré
            Bool: False si le type n'existe pas"""
        try:
            self.cursor.execute("select name from types where id = ?", (type.id,))
            result = self.cursor.fetchone()
            if result != None:
                type.value = result[0]
                return type
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False

    def getTypeByName(self, type : Type) -> Type:
        """Permet de récupérer un type à partir de son nom
        
        Paramètres:
            type (Type): le type à récupérer
        
        Retourne:
            Type: le type récupéré
            Bool: False si le type n'existe pas
        """
        try:
            self.cursor.execute("select id, name from types where name = ?;", (type.value,))
            arrValue = self.cursor.fetchone()
            id = arrValue[0]
            name  = arrValue[1]
            return Type(id, name)
        except sqlite3.Error as e:
            print(e)
            return None
    #endregion
    
    #region Extension
    def getAllExtensions(self) -> list:
        """Permet de récupérer toutes les extensions
        
        Retourne:
            list: la liste de toutes les extensions
        """
        try:
            extensions = []
            self.cursor.execute("select * from extensions")
            result = self.cursor.fetchall()
            for r in result:
                extensions.append(Extension(r[0], r[1]))
            return extensions
        except sqlite3.Error as e:
            print(e)
            return False

    def getExtensionById(self, extension : Extension) -> Extension:
        """Permet de récupérer une extension à partir de son id
        
        Paramètres:
            extension (Extension): l'extension à récupérer
            
        Retourne:
            Extension: l'extension récupérée
            Bool: False si l'extension n'existe pas
        """
        try:
            self.cursor.execute("select name from extensions where id = ?", (extension.id,))
            result = self.cursor.fetchone()
            if result != None:
                extension.value = result[0]
                return extension
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False

    def getExtensionByName(self, extension : Extension) -> Extension:
        """Permet de récupérer une extension à partir de son nom

        Paramètres:
            extension (Extension): l'extension à récupérer

        Retourne:
            Extension: l'extension récupérée
            Bool: False si l'extension n'existe pas
        """
        try:
            self.cursor.execute("select id, name from extensions where name = ?;", (extension.value,))
            arrValue = self.cursor.fetchone()
            id = arrValue[0]
            name  = arrValue[1]
            return Extension(id, name)
        except sqlite3.Error as e:
            print(e)
            return False
    #endregion
   
    #region Metadata
    def getMetadataByAllFields(self, m : Metadata) -> Metadata:
        """Permet de récupérer les métadonnées à partir de tous les champs

        Paramètres:
            m (Metadata): la métadonnée à récupérer

        Retourne:
            Metadata: la métadonnée récupérée
            Bool: False si la métadonnée n'existe pas
        """
        try:
            self.cursor.execute("select id from metadatas where fileName_id = ? and extension_id = ? and creationDate = ? and modificationDate = ? and sizeCompressed = ? and sizeUncompressed = ? and pathName_id = ? and sha1 = ?", 
            (m.fileName.id, m.extension.id, m.creationDate, m.modificationDate, m.sizeCompressed, m.sizeUncompressed, m.pathName.id, m.sha1))
            result = self.cursor.fetchone()
            if result is not None:
                m.id = result[0]
                return m
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False

    def getAllMetadatas(self, limit : int, offset : int) -> list:
        """Permet de récupérer toutes les métadonnées
            
        Paramètres:
            limit (int): le nombre de métadonnées à récupérer
            offset (int): l'offset de la première métadonnée à récupérer
        Retourne:
            list: la liste de toutes les métadonnées
        """
        sql = ("SELECT id, fileName_id,fileName, extension_id, extension,creationDate, modificationDate, sizeCompressed, sizeUncompressed, pathName_id, pathName, createdAt, sha1"
               " FROM metadatasView"
               " LIMIT ? OFFSET ?;")
        result = pd.read_sql_query(sql, self.connect, params=(limit, offset))
        metadatas = []
        for index, row in result.iterrows():
            m : Metadata = Metadata(FileName(row["fileName_id"],row["fileName"]),Extension(row["extension_id"], row["extension"]),row["creationDate"],row["modificationDate"],row["sizeCompressed"],row["sizeUncompressed"],PathName(row["pathName_id"],row["pathName"]),row["sha1"],row["id"],row["createdAt"])
            metadatas.append(m)
        return metadatas
    
    def getMetadataById(self, id : int) -> Metadata:
        """Permet de récupérer une métadonnée à partir de son id
        
        Paramètres:
            id (int): l'id de la métadonnée à récupérer
        
        Retourne:
            Metadata: la métadonnée récupérée
            Bool: False si la métadonnée n'existe pas
        """
        try:
            sql = ("SELECT id, fileName_id,fileName, extension_id, extension,creationDate, modificationDate, sizeCompressed, sizeUncompressed, pathName_id, pathName, createdAt, sha1"
                   " FROM metadatasView"
                   " WHERE id = ?;")
            self.cursor.execute(sql, (id,))
            result = self.cursor.fetchone()
            if result != None:
                return Metadata(FileName(result[1],result[2]),Extension(result[3],result[4]),result[5],result[6],result[7],result[8],PathName(result[9],result[10]),result[12],result[0],result[11])
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False
    def getMetadatasByIds(self, ids : list) -> list:
        """Permet de récupérer une liste de métadonnées à partir de leurs ids
        
        Paramètres:
            ids (list): la liste des ids des métadonnées à récupérer
        
        Retourne:
            list: la liste des métadonnées récupérées
        """
        try:
            metadatas = []
            for id in ids:
                metadatas.append(self.getMetadataById(id))
            return metadatas
        except sqlite3.Error as e:
            print(e)
            return False
    def getMetadatasBySha1(self, sha1 : int) -> list:
        """Permet de récupérer les métadonnées à partir d'un sha1

        Paramètres:
            sha1 (int): le sha1 de la métadonnée à récupérer

        Retourne:
            list: la liste de toutes les métadonnées
        """
        result = pd.read_sql_query("SELECT * from Metadatas WHERE sha1 = ?;", self.connect, params=[(sha1),])
        metadatas = []
        for index, row in result.iterrows():
            m : Metadata = Metadata(row["fileName_id"], row["extension_id"], row["creationDate"], row["modificationDate"], row["sizeCompressed"], row["sizeUncompressed"], row["pathName_id"],row["sha1"], row["id"],row["createdAt"])
            m.fileName = self.getFileNameById(FileName(row["fileName_id"], ""))
            m.extension = self.getExtensionById(Extension(row["extension_id"], ""))
            m.pathName = self.getPathNameById(PathName(row["pathName_id"], ""))
            metadatas.append(m)
            
        return metadatas
    #endregion
    
    def getAllFolderNamePathName(self, limit: int, offset: int) -> list:
        """Permet de récupérer toutes les métadonnées lier à leur dossier
        
        Retourne:
            list: la liste de toutes les métadonnées lier à leur dossier.
        """
        try:
            folderNamesPathNames = []
            sql = ("SELECT folderName, pathName"
                   " FROM folderNamePathNameView"
                   " LIMIT ? OFFSET ?;")
            self.cursor.execute(sql, (limit, offset))
            result = self.cursor.fetchall()
            for r in result:
                arrMF = [FolderName(-1, r[0]),PathName(-1, r[1])]
                folderNamesPathNames.append(arrMF)
            return folderNamesPathNames
        except sqlite3.Error as e:
            print(e)
            return False

    def getAllFolderNameMetadata(self, limit: int, offset: int) -> list:
        """Permet de récupérer toutes les métadonnées lier à leur dossier
        
        Retourne:
            list: la liste de toutes les métadonnées lier à leur dossier.
        """
        try:
            folderMetadatas = []
            sql = ("SELECT folderName_id,folderName,metadata_id, fileName_id, fileName, extension_id, extension, creationDate, modificationDate, sizeCompressed, sizeUncompressed, pathName_id, pathName, sha1"
                   " FROM folderNameMetadataView"
                   " LIMIT ? OFFSET ?;")
            self.cursor.execute(sql, (limit, offset))
            result = self.cursor.fetchall()
            for r in result:
                arrMF = [FolderName(r[0], r[1]),Metadata(FileName(r[3], r[4]), Extension(r[5], r[6]), r[7], r[8], r[9], r[10], PathName(r[11], r[12]), r[13], r[2])]
                folderMetadatas.append(arrMF)
            return folderMetadatas
        except sqlite3.Error as e:
            print(e)
            return False
    
    def getAllResources(self, limit : int, offset : int) -> list:
        """Permet de récupérer tous les ressources

        Paramètres:
            limit (int): le nombre de ressources à récupérer
            offset (int): l'offset de la première ressource à récupérer
        
        Retourne:
            list: la liste de tous les ressources
        """
        resources = []
        sql = ("SELECT sha1, type_id, name from resourcesView"
               " LIMIT ? OFFSET ?;")
        result = pd.read_sql_query(sql, self.connect, params=[(limit), (offset)])
        for index, row in result.iterrows():
            r : Resource = Resource(row["sha1"], True, type=Type(row["type_id"], row["name"]))
            resources.append(r)
                    
        return resources

    def getAllResourcesWithMetadata(self, archive : Archive) -> list:
        """Permet de récupérer tous les ressources avec leurs métadonnées
        
        Paramètres:
            archive (Archive): l'archive à laquelle sont liées les métadonnées
            
        Retourne:
            list: la liste de tous les ressources avec leurs métadonnées"""
        resources = self.getAllResources()
        for r in resources:
            r.allMetadatas = self.getMetadatasBySha1(r.sha1)
            r.path = archive.pathArchive + "/" + r.sha1[0:2] + "/" + r.sha1

        return resources

    def getResourceBySha1WithMetadataById(self, sha1, id) -> Resource:
        """Permet de récupérer un ressource avec ses métadonnées à partir de son sha1 et de son id
        
        Paramètres:
            sha1 (int): le sha1 du ressource
            id (int): l'id de la métadonnée
            
        Retourne:
            Resource: le ressource avec ses métadonnées"""
        sql = ("SELECT sha1, type_id,typeName, id,fileName_id, fileName,extension_id, extension, pathName_id,pathName,creationDate,modificationDate, sizeCompressed, sizeUncompressed,createdAt"
               " FROM searchView r"
               " WHERE sha1 = ? AND id = ?")
        result = pd.read_sql_query(sql, self.connect, params=[str(sha1),int(id)])
        for index, row in result.iterrows():
            m : Metadata = Metadata(FileName(row["fileName_id"],row["fileName"]),Extension(row["extension_id"], row["extension"]), row["creationDate"], row["modificationDate"],row["sizeCompressed"], row["sizeUncompressed"],PathName(row["pathName_id"], row["pathName"]), row["sha1"], row["id"], row["createdAt"])
            r : Resource = Resource(row["sha1"], True, m, Type(row["type_id"], row["typeName"]))
            r.universalMetadata = m 
            return r
    
    def getResourceWithMetadataById(self, id : int) -> Resource:
        """Permet de récupérer un ressource avec ses métadonnées à partir de son id
        
        Paramètres:
            id (int): l'id du ressource
            
        Retourne:
            Resource: le ressource avec ses métadonnées
        """
        result = pd.read_sql_query("select * from Resources as r, Metadatas as m WHERE r.sha1 = m.sha1 and r.id = ?;", self.connect, params=[id,])
        for index, row in result.iterrows():
            m : Metadata = Metadata( row["name"], row["size"], row["extension"], row["creationDate"], row["modificationDate"], row["sha1"])
            r : Resource = Resource(row["sha1"], m)
            return r

    def search(self, options : dict) -> list:
        """Permet de rechercher des ressources
        
        Paramètres:
            options (dict): les options de la recherche
        
        Retourne:
            list: la liste des ressources trouvées
        """
        sql = ("SELECT sha1, id,fileName_id, fileName,extension_id, extension, pathName_id,pathName,creationDate, modificationDate, sizeCompressed, sizeUncompressed, createdAt, type_id, typeName, folder"
       " FROM searchView ")
        resources = []
        params = []
        for option in options:
            if sql.endswith("AND"):
                sqlWord = " "
            elif sql.endswith(" "):
                sqlWord = " WHERE "
            match option:
                case "fileName":
                    sql += sqlWord +"fileName LIKE ? AND"
                    params.append('%'+options[option]+'%')
                case "extension":
                    sql += sqlWord +"extension LIKE ? AND"
                    params.append('%'+options[option]+'%')
                case "pathName":
                    sql += sqlWord +"pathName LIKE ? AND"
                    params.append('%'+options[option]+'%')
                case "creationDateStart":
                    sql += sqlWord +"creationDate BETWEEN ? AND ? AND"
                    params.append(Metadata.convertDateInTimeStamp(options[option]))
                    if "creationDateEnd" in options:
                        params.append(Metadata.convertDateInTimeStamp(options["creationDateEnd"]))
                    else:
                        today = date.today()
                        today += timedelta(days=1)
                        params.append(Metadata.convertDateInTimeStamp(today.strftime("%Y/%m/%d")))
                case "modificationDateStart":
                    sql += sqlWord +"modificationDate BETWEEN ? AND ? AND"
                    params.append(Metadata.convertDateInTimeStamp(options[option]))
                    if "modificationDateEnd" in options:
                        params.append(Metadata.convertDateInTimeStamp(options["modificationDateEnd"]))
                    else:
                        today = date.today()
                        today += timedelta(days=1)
                        params.append(Metadata.convertDateInTimeStamp(today.strftime("%Y/%m/%d")))
                case "sizeStart":
                    sql += sqlWord +"sizeCompressed BETWEEN ? AND ? AND"
                    if "sizeUnit" not in options:
                        raise Exception("sizeUnit is required")
                    
                    params.append(Metadata.convertSizeToOctet(options[option],options["sizeUnit"]))
                    if "sizeEnd" in options:
                        params.append(Metadata.convertSizeToOctet(options["sizeEnd"],options["sizeUnit"]))
                    else:
                        params.append(Metadata.convertSizeToOctet(99999,"TB"))
                case "createdAtStart":
                    sql += sqlWord +"createdAt BETWEEN ? AND ? AND"
                    params.append(Metadata.convertDateInTimeStamp(options[option]))
                    if "createdAtEnd" in options:
                        params.append(Metadata.convertDateInTimeStamp(options["createdAtEnd"]))
                    else:
                        today = date.today()
                case "type":
                    sql += sqlWord +"typeName LIKE ? AND"
                    params.append('%'+options[option]+'%')
                    
                case "sha1":
                    sql += sqlWord +"m.sha1 = :sha1 AND"
                    params.append(options[option])
        
        # Remove the last AND
        if sql.endswith("AND"):
            sql = sql[:-4]
        sql = sql + ";"
        #sql += " r.sha1 = m.sha1;"
        #{"name":'%'+options["name"]+'%', "extension": '%'+options["extension"]+'%', "creationDate": options["creationDate"], "modificationDate": options["modificationDate"], "size": options["size"], "sha1": options["sha1"]}
        result = pd.read_sql_query(sql, self.connect, params=params)
        for index, row in result.iterrows():
            m : Metadata = Metadata(FileName(row["fileName_id"],row["fileName"]),Extension(row["extension_id"], row["extension"]), row["creationDate"], row["modificationDate"],row["sizeCompressed"], row["sizeUncompressed"],PathName(row["pathName_id"], row["pathName"]), row["sha1"], row["id"], row["createdAt"])
            r : Resource = Resource(row["sha1"], True, m, Type(row["type_id"], row["typeName"]))
            r.universalMetadata = m 
            resources.append(r)

                    
        return resources

    #endregion

    def attachDb(self, path : str):
        """Permet d'attacher une base de données à la base de donnée courante
        
        Paramètres:
            path (str): le chemin vers la base de données
        """
        try:
            sql = "ATTACH DATABASE '"+path+"' AS db;"
            self.connect.execute(sql)
            return "db"
        except Exception as e:
            print(e)
            raise Exception("Failed to attach database")
    
    def detachDb(self, name : str):
        """Permet de détacher une base de données de la base de données courante
        
        Paramètres:
            path (str): le chemin vers la base de données
        """
        sql = "DETACH DATABASE "+name+";"
        try:
            self.connect.execute(sql)
            self.connect.commit()
        except Exception as e:
            print(e)
            raise Exception("Failed to detach database")

    def askToInsertExtensionsWithOtherDb(self, path : str) :
        """Permet de demander les extensions enregistrées depuis une autre base de données
        
        Paramètres:
            path (str): le chemin vers la base de données étrangère
        """
        try:
            name = self.attachDb(path)
            sql = ("INSERT OR IGNORE INTO extensions (name)"
                   " SELECT name from "+name+".extensions;")
            self.connect.execute(sql)
            self.connect.commit()
            self.detachDb(name)
            
        except Exception as e:
            print(e)
            return []

    def askToInsertFileNameWithOtherDb(self, path : str):
        """Permet de demander les noms de fichiers enregistrés depuis une autre base de données
        
        Paramètres:
            path (str): le chemin vers la base de données étrangère
        """
        try:
            name = self.attachDb(path)
            sql = ("INSERT OR IGNORE INTO fileNames (name)"
                   " SELECT name from "+name+".fileNames;")
            self.connect.execute(sql)
            self.connect.commit()
            self.detachDb(name)
        except Exception as e:
            print(e)
            return []
    
    def askToInsertFolderNameWithOtherDb(self, path : str):
        """Permet de demander les noms de dossier enregistrés depuis une autre base de données
        
        Paramètres:
            path (str): le chemin vers la base de données étrangère
        """
        try:
            name = self.attachDb(path)
            sql = ("INSERT OR IGNORE INTO folderNames (name)"
                   " SELECT name from "+name+".folderNames;")
            self.connect.execute(sql)
            self.connect.commit()
            self.detachDb(name)
        except Exception as e:
            print(e)
            return []

    def askToInsertFolderNameWithOtherDb(self, path : str):
        """Permet de demander les noms de dossier enregistrés depuis une autre base de données
        
        Paramètres:
            path (str): le chemin vers la base de données étrangère
        """
        try:
            name = self.attachDb(path)
            sql = ("INSERT OR IGNORE INTO folderNames (name)"
                   " SELECT name from "+name+".folderNames;")
            self.connect.execute(sql)
            self.connect.commit()
            self.detachDb(name)
        except Exception as e:
            print(e)
            return []

    def askToInsertPathNameWithOtherDb(self, path : str):
        """Permet de demander les noms de dossier enregistrés depuis une autre base de données
        
        Paramètres:
            path (str): le chemin vers la base de données étrangère
        """
        try:
            name = self.attachDb(path)
            sql = ("INSERT OR IGNORE INTO pathNames (pathName)"
                   " SELECT pathName from "+name+".pathNames;")
            self.connect.execute(sql)
            self.connect.commit()
            self.detachDb(name)
        except Exception as e:
            print(e)
            return []

    def askToInsertTypeWithOtherDb(self, path : str):
        """Permet de demander les types enregistrés depuis une autre base de données
        
        Paramètres:
            path (str): le chemin vers la base de données étrangère
        """
        try:
            name = self.attachDb(path)
            sql = ("INSERT OR IGNORE INTO types (name)"
                   " SELECT name from "+name+".types;")
            self.connect.execute(sql)
            self.connect.commit()
            self.detachDb(name)
        except Exception as e:
            print(e)
            return []

    
