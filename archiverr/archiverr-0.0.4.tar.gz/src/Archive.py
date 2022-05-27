"""
AUTEUR : Théo Hurlimann
  LIEU : CFPT Informatique Genève
  DATE : avril 2022
  PROJET: ARCHIVER
  VERSION : 1.0
  FICHIER : Archive.py: 
    - Possède les méthodes pour créer une archive et la gérer.
"""
from importlib_metadata import metadata
import src.Constants as Constants
from src.FolderImport import FolderImport
from src.Utilities import Utilities
from src.Resource import Resource
from src.Metadata import Metadata
from src.Bdd import Bdd
from src import myConfig
import src.Archive as Archive
import pickle 
import stat
from os import makedirs, chmod, path, remove
import shutil, os, py7zr, datetime, orjson
from progress.bar import Bar

class Archive :
    def __init__(self, name : str) -> None:
        """Constructeur de la classe Archive

        Paramètres:
            name (String): le nom d'archive

        Retourne:
            Bonne question ?
        """
        
        
        self.compressFiles = []
        self.name = name
        p = Utilities.getPathOfArchive(name)

        if path.exists(p):

            self.pathArchive = p
            self.myDb = Bdd(self.pathArchive)
        else:
            self.pathArchive = p 
            self.createDirectoryArchive(self.pathArchive)
            self.myDb = Bdd(self.pathArchive)
            
        #if not p.endswith("/"):
        #    self.pathArchive = p+"/"
        pass
    
    def __add__(self, archive : Archive) -> Archive:
        return self.mergeTwoArchive(archive)

    def createDirectoryArchive(self, path :str) -> bool:
        """Permet de Créer le dossier de l'archive

        Paramètres:
            path (String) : chemin de l'archive

        Retourne:
            bool: True si le dossier a été créé
            bool: False si le n'a dossier pas été créé
        """
        try :
            makedirs(path)
            return True
        except Exception as e:
            print(e)
            return False

    def archiveFolder(self, FolderImport : FolderImport) -> bool:
        """Permet d'archiver un dossier

        Paramètres:
            FolderImport (FolderImport) : dossier à archiver

        Retourne:
            bool: True si le dossier a été créé
            bool: False si le n'a dossier pas été créé
        """
        try:
            bar = Bar('Processing', max=FolderImport.nbResource, suffix='%(index).0f/%(max).0f fichiers archivés') 
            for Resource in FolderImport.resources:
                self.compressFiles.append(self.archiveResource(Resource))
                bar.next()
                pass
            bar.finish()
            self.cleanTemp()
            return True
        except Exception as e:
            print(e)
            return False

    def writeMetadataInJson(self, m : Metadata, newArchive : Archive= None) -> None:
        """Permet d'écrire les métadonnées dans un fichier json

        Paramètres:
            m (Metadata): métadonnées à écrire
            newArchive (Archive): archive où écrire les métadonnées

        Retourne:
            
        """
        #m = r.universalMetadata
        if newArchive is None:
            pathOfJson = self.pathArchive + "/"+ m.sha1[0:2] +"/"+ m.sha1 + ".json"
        else:
            pathOfJson = newArchive.pathArchive + "/"+ m.sha1[0:2] +"/"+ m.sha1 + ".json"
        
        if not path.exists(pathOfJson):
            f= open(pathOfJson,"w+")
            f.write("[")
            f.write(m.toJson())
            f.write("]")
            f.close()
        else:
            arrayM = []
            with open(pathOfJson, "r") as f:
                data = orjson.loads(f.read())
            for d in data:
                m_json = Metadata.jsonDecoder(d)
                arrayM.append(m_json)
            arrayM.append(m)
            f = open(pathOfJson,"w+")
            f.write("[")
            for m in arrayM:
                f.write(m.toJson())
                
                # if it is not the last metadata
                if m != arrayM[-1]:
                    f.write(",")
    
            f.write("]")
            f.close()
        

    def archiveResource(self, resource : Resource) -> bool:
        """Permet d'archiver une ressource

        Paramètres:
            resource (Resource): ressource à archiver

        Retourne:
            bool: True si la ressource a été créé
            
        """
        #print("On commence l'archive de "+resource.path)
        self.verifTemp()
        e = self.myDb.addExtension(resource.extension)
        fn = self.myDb.addFileName(resource.fileName)
        t = self.myDb.addType(resource.type)
        pn = self.myDb.addPathName(resource.pathName)

        resource.universalMetadata.extension = e
        resource.universalMetadata.fileName = fn
        resource.universalMetadata.pathName = pn
        resource.type = t

        if not self.myDb.resourceExist(resource): 
            self.compressResource(resource)
            self.myDb.addResource(resource)
            self.addResourceToArchive(resource)
        
        if not self.myDb.metadataExist(resource.universalMetadata):
            resource.universalMetadata = self.myDb.addMetadata(resource.universalMetadata)
            self.writeMetadataInJson(resource.universalMetadata) 
        else:
            resource.universalMetadata = self.myDb.getMetadataByAllFields(resource.universalMetadata)
        
        folders = self.myDb.addFoldersWithPathName(resource.universalMetadata.pathName)
        self.myDb.addFolderMetadata(folders[-1],resource.universalMetadata)
        for folder in folders:
            self.myDb.addFolderPathName(folder,resource.universalMetadata.pathName)

        return True

    def addResourceToArchive(self, r : Resource) -> bool:
        """Permet de déplacer une ressource dans l'archive

        Paramètres:
            r (Resource): ressource à déplacer

        Retourne:
            bool: True si la ressource a été créé          
        """

        dirResource = self.createDirectoryResource(r)
        newPath = dirResource+"/"+r.sha1+myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_DEFAULT_EXTENSION_COMPRESSION)
        oldPath = self.pathArchive+"/temp/"+r.sha1+ myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_DEFAULT_EXTENSION_COMPRESSION)

        #print("On commence le moove vers le dossier archive")
        shutil.move(oldPath, newPath)
        #print("moove fini")

        return True

    def createDirectoryResource(self, resource : Resource) -> str:
        """Créer le dossier pour la ressource dans l'archive

        Paramètres:
            resource (Resource): ressource où on a besoin de créer son dossier

        Retourne:
            String: chemin du dossier de la ressource
        """
        pathResource = Archive.createPathRessourceInArchive(self.pathArchive, resource) #self.pathArchive+"/"+Resource.sha1[0:2]
        if not path.exists(pathResource):
            makedirs(pathResource)
        return pathResource
        
    def cleanTemp(self) -> bool:
        """Permet de nettoyer le dossier temp

        Retourne:
            bool: True si le dossier a été nettoyé
            bool: False si le dossier n'a pas été nettoyé
        
        """
        try :
            shutil.rmtree(self.pathArchive+"/temp")
            return True
        except Exception as e:
            print(e)
            return False

    def compressResource(self, Resource : Resource) -> bool:
        """Permet de compresser une ressource

        Paramètres:
            Resource (Resource): ressource à compresser

        Retourne:
            bool: True si la ressource a été créé
            
        """
        self.pathTmp = self.pathArchive+"/temp/"

        # Pour ne pas perdre le fichier
        shutil.copy(Resource.path,self.pathTmp+Resource.sha1+Resource.extension.value)
        
        dirWork = myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_DEFAULT_ARCHIVE_DIR)
        os.chdir(dirWork+"/"+self.name+"/temp/")
       
        with py7zr.SevenZipFile(Resource.sha1+myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE,Constants.NAME_OF_DEFAULT_EXTENSION_COMPRESSION), 'w') as archive:
            archive.writeall(Resource.sha1+Resource.extension.value)
        pass
    
        os.chdir(dirWork)
        return True
    
    def verifTemp(self):
        """Permet de vérifier si le dossier temp existe
           Appelle la fonction mkdirs si le dossier n'existe pas
        """
        #print(self.pathArchive+"/temp/")
        if not path.exists(self.pathArchive+"/temp/"):
            makedirs(self.pathArchive+"/temp/")
            chmod(self.pathArchive+"/temp/", 0o777)

    def extractResources(self, metadatas : list[Metadata], path : str) -> bool:
        """Permet d'extraire une liste de ressources
        
        Paramètres:
            ressources (list): liste de métadonné à extraire
            
            Retourne:
                bool: True si la liste a été extraite
                bool: False si la liste n'a pas été extraite
        """
        fileNames = []
        bar = Bar('Processing', max=len(metadatas), suffix='%(index).0f/%(max).0f fichiers extraits')
        for m in metadatas:
            if m.fileName.value in fileNames:
                m.fileName.value = m.fileName.value+"_"+str(fileNames.count(m.fileName.value) + 1)
            if not self.extractResource(m, path):
                return False
            fileNames.append(m.fileName.value)
            bar.next()
        bar.finish()
        return True

    def extractResource(self, m : Metadata, path : str) -> bool:
        """Permet d'extraire une ressource
        
        Paramètres:
            r (Resource): ressource à extraire
            
            Retourne:
                bool: True si la ressource a été extraite
                bool: False si la ressource n'a pas été extraite
        """
        try:
            pathOfResource = self.pathArchive+"/"+m.sha1[0:2]+"/"+m.sha1+myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_DEFAULT_EXTENSION_COMPRESSION)
       
            with py7zr.SevenZipFile(pathOfResource, 'r') as archive:
                archive.extractall(path)

            #change the name of the file
            os.rename(path+"/"+m.sha1+m.extension.value, path+"/"+m.fileName.value+m.extension.value)

            Metadata.addMetadataInRessource(path+"/"+m.sha1+m.extension.value, m)
            return True
        except Exception as e:
            print(e)
            return False
            
    def duplicateResourceToOtherArchive(self, Resource : Resource, Archive : Archive) -> bool:
        """Duplique le fichier depuis l'archive source vers l'archive destination
        
        Paramètres:
            Resource (Resource): ressource à dupliquer
            Archive (Archive): archive destination
            
        Retourne:
            bool: True si la ressource a été dupliquée
            bool: False si la ressource n'a pas été dupliquée
        """
        try:
            pathOldFile = self.pathArchive+"/"+Resource.sha1[0:2]+"/"+Resource.sha1+myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_DEFAULT_EXTENSION_COMPRESSION)
            pathNewDirectory = Archive.pathArchive+"/"+Resource.sha1[0:2]
            pathNewFile = pathNewDirectory+"/"+Resource.sha1+myConfig.getOption(Constants.NAME_OF_SECTION_ARCHIVE, Constants.NAME_OF_DEFAULT_EXTENSION_COMPRESSION)
            if not path.exists(pathNewDirectory):
                makedirs(pathNewDirectory)
                chmod(pathNewDirectory, 0o777)
            
            shutil.copy(pathOldFile, pathNewFile)
            return True
        except Exception as e:
            print(e)
            return False
    
    def mergeTwoArchive(self, archive : Archive) -> Archive:
        """Permet de fusionner deux archives
        
        Paramètres:
            archive (Archive): archive à fusionner
            
        Retourne:
            Archive: archive fusionnée
        """
        resources = []
        metadatas = []
        LIMIT = 10
        offset = 0

        bddA : Bdd = self.myDb
        bddB : Bdd = archive.myDb

        bddA.askToInsertExtensionsWithOtherDb(bddB.pathFile)
        bddA.askToInsertFileNameWithOtherDb(bddB.pathFile)
        bddA.askToInsertFolderNameWithOtherDb(bddB.pathFile)
        bddA.askToInsertPathNameWithOtherDb(bddB.pathFile)
        bddA.askToInsertTypeWithOtherDb(bddB.pathFile)

        # Ajout des ressources        
        resources = bddB.getAllResources(LIMIT, offset)
        while len(resources) > 0:
            
            for r in resources:
                # Récupération du nouveau type_id
                r.type = self.myDb.getTypeByName(r.type)
                r.path = archive.pathArchive + "/" + r.sha1[0:2] + "/" + r.sha1
                r, added = bddA.addResource(r)
                if added:
                    archive.duplicateResourceToOtherArchive(r, self)


            offset += LIMIT
            resources = bddB.getAllResources(LIMIT, offset)

        # Ajout des métadonnées
        offset = 0
        metadatas = bddB.getAllMetadatas(LIMIT, offset)
        while len(metadatas) > 0:
            for m in metadatas:
                m = self.getNewIdsMetadata(m)
                m, added = bddA.addMetadata(m,True)
                if added:
                    archive.writeMetadataInJson(m, self)
                    
            offset += LIMIT
            metadatas = bddB.getAllMetadatas(LIMIT, offset)
        
        # Ajout des liaisons folderName metadata
        offset = 0
        folderNameMetadata = bddB.getAllFolderNameMetadata(LIMIT, offset)
        while len(folderNameMetadata) > 0:
            for fn, m in folderNameMetadata:
                fn = bddA.getFolderNameByName(fn)
                m = self.getNewIdsMetadata(m)
                m = bddA.getMetadataByAllFields(m)
                bddA.addFolderNameIdMetadataId(fn.id, m.id)
            offset += LIMIT
            folderNameMetadata = bddB.getAllFolderNameMetadata(LIMIT, offset)
                

        # Ajout des liaisons folderName PathName
        offset = 0
        folderNamePathName = bddB.getAllFolderNamePathName(LIMIT, offset)
        while len(folderNamePathName) > 0:
            for fn, pn in folderNamePathName:
                fn = bddA.getFolderNameByName(fn)
                pn = bddA.getPathNameByPath(pn)
                bddA.addFolderNameIdPathNameId(fn.id, pn.id)
            offset += LIMIT
            folderNamePathName = bddB.getAllFolderNamePathName(LIMIT, offset)
    
    def getNewIdsMetadata(self, m : Metadata) -> Metadata:
        """Permet de récupérer les nouvelles ids contenu dans la classe Metadata

        Paramètres:
            m (Metadata): La metadata à traiter

        Returns:
            Metadata: La metadata avec les nouvelles ids
        """
        m.extension = self.myDb.getExtensionByName(m.extension)
        m.pathName = self.myDb.getPathNameByPath(m.pathName)
        m.fileName = self.myDb.getFileNameByName(m.fileName)
        return m 

    def search(self, options : dict) -> list:
        """Permet de rechercher des ressources dans l'archive
        
        Paramètres:
            options (dict): options de recherche
            
        Retourne:
            list: liste des ressources trouvées
        """          
        return self.myDb.search(options)

    def saveToExtract(self, ressources : list) -> bool:
        """Permet de sauvegarder des ressources pour l'extraction
        
        Paramètres:
            ressources (list): liste des ressources à sauvegarder pour l'extraction
            
        Retourne:
            Bool : True si la sauvegarde a réussi
            Bool : False si la sauvegarde a échoué
        """
        try:
            
            arrayToStore = []
            for r in ressources:
                arrayToStore.append(r.universalMetadata.id)
            
            file_to_store = open(self.pathArchive+"/ressourcesToExtract.txt", "wb")
            pickle.dump(arrayToStore, file_to_store)
            file_to_store.close()
            
            return True
        except Exception as e:
            print(e)
            return False
    
    def loadFromFileToExtract(self) -> list:
        """Permet de charger les ressources à extraire depuis le fichier ressourcesToExtract.pickle
        
        Retourne:
            list: liste des ressources à extraire
            list: liste vide si impossible de charger le fichier
        """
        try:
            file_to_load = open(self.pathArchive+"/ressourcesToExtract.txt", "rb")
            metadataIds = pickle.load(file_to_load)
            file_to_load.close()
            # delete the file
            remove(self.pathArchive+"/ressourcesToExtract.txt")
            return metadataIds
        except Exception as e:
            print(e)
            return []

    def getResourceBySha1WithMetadataById(self, sha1 : str, id : int) -> Resource:
        """Permet de récupérer une ressource avec ses métadonnées à partir de son sha1 et de son id
        
        Paramètres:
            sha1 (str): sha1 de la ressource
            id (int): id de la metadata
            
        Retourne:
            Resource: ressource trouvée
        """
    
        return self.myDb.getResourceBySha1WithMetadataById(sha1, id)

    @staticmethod
    def createPathRessourceInArchive(pathOfArchive : str, Resource : Resource) -> str:
        """Crée le chemin d'accès à la ressource dans l'archive
        
        Paramètres:
            pathOfArchive (str): chemin d'accès à l'archive
            Resource (Resource): ressource à créer
            
        Retourne:
            str: chemin d'accès à la ressource
        """
        return pathOfArchive+"/"+Resource.sha1[0:2]


