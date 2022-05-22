from __future__ import absolute_import
from davinci_resolve_api.DaVinci import DaVinci

class ProjectManager:
    """
        All DaVinci Resolve Project Manager Related Stuff
    """
    
    _projectManager = DaVinci.GetProjectManager()

    @classmethod
    def CreateProject(self, projectName):
        """
            Return Type: Project
            Comment: Creates and returns a project if projectName (string) is unique, and None if it is not.
        """
        return self._projectManager.CreateProject(projectName)

    @classmethod
    def DeleteProject(self, projectName):
        """
            Return Type: Bool
            Comment: Delete project in the current folder if not currently loaded
        """
        return self._projectManager.DeleteProject(projectName)

    @classmethod
    def LoadProject(self, projectName):
        """
            Return Type: Project
            Comment: Loads and returns the project with name = 
                projectName (string) if there is a match found, and None if there is no matching Project.
        """
        return self._projectManager.LoadProject(projectName)

    @classmethod
    def GetCurrentProject(self):
        """
            Return Type: Project
            Comment: Returns the currently loaded Resolve project.
        """
        return self._projectManager.GetCurrentProject()

    @classmethod
    def SaveProject(self):
        """
            Return Type: Bool
            Comment: Saves the currently loaded project with its own name. Returns True if successful.
        """
        return self._projectManager.SaveProject()

    @classmethod
    def CloseProject(self, project):
        """
            Return Type: Bool
            Comment: Closes the specified project without saving.
        """
        return self._projectManager.CloseProject(project)

    @classmethod
    def CreateFolder(self, folderName):
        """
            Return Type: Bool
            Comment: Creates a folder if folderName (string) is unique.
        """
        return self._projectManager.CreateFolder(folderName)
    
    @classmethod
    def DeleteFolder(self, folderName):
        """
            Return Type: Bool
            Comment: Deletes the specified folder if it exists. Returns True in case of success.
        """
        return self._projectManager.DeleteFolder(folderName)
    
    @classmethod
    def GetProjectListInCurrentFolder(self):
        """
            Return Type: [project names...]
            Comment: Returns a list of project names in current folder.
        """
        return self._projectManager.GetProjectListInCurrentFolder()

    @classmethod
    def GetFolderListInCurrentFolder(self):
        """
            Return Type: [folder names...]
            Comment: Returns a list of folder names in current folder.
        """
        return self._projectManager.GetFolderListInCurrentFolder()

    @classmethod
    def GotoRootFolder(self):
        """
            Return Type: Bool
            Comment: Opens root folder in database.
        """
        return self._projectManager.GotoRootFolder()
    
    @classmethod
    def GotoParentFolder(self):
        """
            Return Type: Bool
            Comment: Opens parent folder of current folder in database if current folder has parent.
        """
        return self._projectManager.GotoParentFolder()
   
    @classmethod
    def GetCurrentFolder(self):
        """
            Return Type: string
            Comment: Returns the current folder name.
        """
        return self._projectManager.GetCurrentFolder()

    @classmethod
    def OpenFolder(self, folderName):
        """
            Return Type: Bool
            Comment: Opens folder under given name.
        """
        return self._projectManager.OpenFolder(folderName)
    
    @classmethod
    def ImportProject(self, filePath):
        """
            Return Type: Bool
            Comment: Imports a project from the file path provided. Returns True if successful.
        """
        return self._projectManager.ImportProject(filePath)
    
    @classmethod
    def ExportProject(self, projectName, filePath, withStillsAndLUTs=True):
        """
        Return Type: Bool
        Comment: Exports project to provided file path, including stills and LUTs if withStillsAndLUTs is True 
            (enabled by default). Returns True in case of success.
        """
        return self._projectManager.ImportProject(projectName, filePath, withStillsAndLUTs)
    
    @classmethod
    def RestoreProject(self, filePath):
        """
            Return Type: Bool
            Comment: Restores a project from the file path provided. Returns True if successful.
        """
        return self._projectManager.RestoreProject(filePath)
    
    @classmethod
    def GetCurrentDatabase(self):
        """
        Return Type: {dbInfo}
        Comment: Returns a dictionary (with keys 'DbType', 'DbName' and optional 'IpAddress') 
            corresponding to the current database connection
        """
        return self._projectManager.GetCurrentDatabase()

    @classmethod
    def GetDatabaseList(self):
        """
        Return Type: [{dbInfo}]
        Comment: Returns a list of dictionary items (with keys 'DbType', 'DbName' and optional 'IpAddress') 
            corresponding to all the databases added to Resolve
        """
        return self._projectManager.GetDatabaseList()
    
    @classmethod
    def SetCurrentDatabase(self, dbInfo=dict):
        """
        Return Type: Bool
        Comment: Switches current database connection to the database specified by the keys below, and closes any open project.
            - 'DbType': 'Disk' or 'PostgreSQL' (string)
            - 'DbName': database name (string)
            - 'IpAddress': IP address of the PostgreSQL server (string, optional key - defaults to '127.0.0.1')
        """
        return self._projectManager.SetCurrentDatabase(dbInfo)