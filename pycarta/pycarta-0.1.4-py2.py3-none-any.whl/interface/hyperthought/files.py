import warnings

import hyperthought as ht
from .base import HyperThoughtKeyFinder
from typing import Dict, Union, Any, Optional
from warnings import warn
from pathlib import Path, PureWindowsPath
from copy import deepcopy
from tqdm import tqdm
from .setters import update_process

__all__ = ["download_file_from_node"]
__all__ = ["download_file_from_workspace"]

class _TqdmUpTo(tqdm):
    def update_to(self, percentProgress):
        return self.update(percentProgress - self.n)

class _HyperthoughtFileAgent:

    def __init__(self, auth: ht.auth.Authorization):
        self.auth = auth
        self.workspaceId = None
        self.fileId = None
        self.PATH_SEP = '/'

    def retrieve_workspace(self, node):
        workspace = node.strip(self.PATH_SEP).split(self.PATH_SEP)[0]
        workspaceApi = ht.api.workspaces.WorkspacesAPI(self.auth)
        workspaceIds = [
            ws["id"]
            for ws in workspaceApi.get_workspaces()
            if ws["name"] == workspace]
        if workspaceIds is None or len(workspaceIds) == 0:
            raise ValueError(f"Workspace {workspace} not found")
        else:
            self.workspaceId = workspaceIds[0]

    def get_destination_dir(self, filePath: str, destinationDirectoryPath: str):
        directoryPathParts = Path(destinationDirectoryPath).parts
        if len(directoryPathParts) > 1:
            return destinationDirectoryPath
        else:
            #unpacks path parts correctly for both unix and windows style paths
            filePathParts = PureWindowsPath(filePath).parts 
            if destinationDirectoryPath in filePathParts:
                subDir = ""
                start = filePathParts.index(destinationDirectoryPath)
                end = len(filePathParts)-1
                for i in range(start, end):
                    subDir += f"{self.PATH_SEP}{filePathParts[i]}"
                return subDir
            else:
                return destinationDirectoryPath

    def get_file_link(self):
        return f"/files/filesystementry/{self.fileId}/versions/0.json"

    def upload(self, filePath: str, destinationDirectoryPath: str, reportProgress: bool):        
        filesApi = ht.api.files.FilesAPI(self.auth)

        # Get destination directory UUID path
        uuidPath = ","
        fullDirPath = ""
        for folder in destinationDirectoryPath.strip(self.PATH_SEP).split(self.PATH_SEP):
            folderId = None
            contentList = filesApi.get_from_location(
                space_id = self.workspaceId, path = uuidPath, 
                start = -1, length=1E6)
            for content in contentList:
                if content['ftype'] == "Folder" and content['name'] == folder:
                    folderId = content['pk']
                    break
            if folderId is None: 
                folderId = filesApi.create_folder(
                    name = folder, space_id = self.workspaceId, path = uuidPath)
            uuidPath = f"{uuidPath}{folderId},"    

        # Upload the file
        if reportProgress: 
            with _TqdmUpTo(range(100), desc="File upload progress", unit='%') as t:
                self.fileId = filesApi.upload(
                    local_path = filePath,
                    space_id = self.workspaceId,
                    path = uuidPath,
                    progress_callback=t.update_to
            )[0]
        else:
            self.fileId = filesApi.upload(
                local_path = filePath,
                space_id = self.workspaceId,
                path = uuidPath
            )[0]

    def update_node(self, node: str, fileKey: str):
        
        # get the node
        nodeId = HyperThoughtKeyFinder(self.auth)(node)
        if nodeId is None:
            return

        # add property 
        update_process(
            self.auth,
            nodeId,
            values={fileKey : self.get_file_link()},
            add = True
        )
        
    def retrieve_file_id_from_process(self, path : str):
        fileId = None
        if len(path.strip(self.PATH_SEP).split(self.PATH_SEP)) > 3:
            pathSplit = path.strip(self.PATH_SEP).rsplit(self.PATH_SEP, 1)
            processPath = pathSplit[0]
            fileKey = pathSplit[1]
            nodeId = HyperThoughtKeyFinder(self.auth)(processPath) 
            if nodeId is not None:
                document = ht.api.workflow.WorkflowAPI(self.auth).get_document(nodeId)
                if document.get("processType") == "process":
                    fileLink = [m["value"]["link"] for m in document.get("metadata") 
                                if m["keyName"] == fileKey]
                    # File Link has the following form:
                    # ['/files/filesystementry/<file_id>/versions/0.json']
                    if len(fileLink) > 0 and fileLink[0].startswith("/files"):
                        fileParts = fileLink[0].strip(self.PATH_SEP).split(self.PATH_SEP)
                        if len(fileParts) > 2:
                            fileId = fileLink[0].strip(self.PATH_SEP).split(self.PATH_SEP)[2]
        if fileId is None:
            raise ValueError(f"File ID could not be retrieved from process key {path}")
        else:
            self.fileId = fileId

    def retrieve_file_id_from_workspace(self, path : str):
        fileId = None
        uuidPath = ","
        for f in path.strip(self.PATH_SEP).split(self.PATH_SEP):
            folderId = None
            contentList = ht.api.files.FilesAPI(self.auth).get_from_location(
                space_id = self.workspaceId, path = uuidPath, 
                start = -1, length=1E6)
            for content in contentList:
                if content['ftype'] == "Folder" and content['name'] == f:
                    folderId = content['pk']
                if content['ftype'] != "Folder" and content['name'] == f:
                    fileId = content['pk']    
            uuidPath = f"{uuidPath}{folderId}," 
        if fileId is None:
            raise ValueError(f"File ID could not be retrieved from workspace " 
                + f"{self.workspaceId} and file path {path}")
        else:
            self.fileId = fileId

    def download(self, reportProgress, directory: str = "."):
        if reportProgress:
            with _TqdmUpTo(range(100), desc="File download progress", unit='%') as t:
                ht.api.files.FilesAPI(self.auth).download(
                    file_id = self.fileId, 
                    directory=directory, 
                    progress_callback=t.update_to)
        else:
            ht.api.files.FilesAPI(self.auth).download(
                file_id = self.fileId, 
                directory=directory)

def upload_file(
    auth: ht.auth.Authorization,
    filePath: str,
    destinationDirectoryPath: str,
    node: str,
    keyName: str = None,
    reportProgress: bool = False
) -> str:
    """
    Upload a file to HyperThought.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Authorization agent that handles communication with the HyperThought
        server.
    filePath: str
        Local file path of file to upload. 
    destinationDirectoryPath : str 
        Directory on Hyperthought under which file should be stored. 
        If set to a single directory name, and that directory is nested in the 
        filePath, the destination directory will be constructed from the 
        filePath with the given directory name as root.
    node : str 
        Workspace name or Process path; if a process path, the workspace will 
        be retrieved from the path, and the process will be updated with a link 
        to the file.
    keyName : str (optional)
        An optional key name to store the file under, if node is set to a 
        Process path. If not specified, the key name will be set to the file 
        stem (the file name sans directory path and file extension)
    reportProgress: bool (optional)
        Defaults to false. If true, file upload progress will be reported as
        percentage.
    Returns
    -------
    :return: The HyperThought file link.
    :rtype: str
    """
    agent = _HyperthoughtFileAgent(auth)
    agent.retrieve_workspace(node)
    destinationDir = agent.get_destination_dir(filePath, destinationDirectoryPath)
    agent.upload(filePath, destinationDir, reportProgress)
    if keyName is None:
        keyName = Path(filePath).stem
    agent.update_node(node, keyName)
    return agent.get_file_link()


def download_file_from_workspace(
    auth: ht.auth.Authorization,
    workspaceName: str,
    filePath: str,
    directory: str = ".",
    reportProgress: bool = False
):
    """
    Download a file from HyperThought.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Authorization agent that handles communication with the HyperThought
        server.
    workspaceName: str
        Name of the workspace under which the file is stored.
    filePath: str
        Full file path of file to be downloaded.
    directory: str
        Local directory to which file should be downloaded. 
        Defaults to the current directory.
    reportProgress: bool (optional)
        Defaults to false. If true, file download progress will be reported as
        percentage.    
    Returns
    -------
    None
    """
    agent = _HyperthoughtFileAgent(auth)
    agent.retrieve_workspace(workspaceName)
    agent.retrieve_file_id_from_workspace(filePath)
    agent.download(reportProgress, directory)

def download_file_from_node(
    auth: ht.auth.Authorization,
    fileKeyPath: str,
    directory: str = ".",
    reportProgress: bool = False
):
    """
    Download a file from HyperThought.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Authorization agent that handles communication with the HyperThought
        server.
    fileKeyPath: str
        Process node path ending with the name of the key under which the file
        has been stored
    directory: str
        Local directory to which file should be downloaded. 
        Defaults to the current directory.
    reportProgress: bool (optional)
        Defaults to false. If true, file download progress will be reported as
        percentage.
    Returns
    -------
    None
    """
    agent = _HyperthoughtFileAgent(auth)
    agent.retrieve_file_id_from_process(fileKeyPath)
    agent.download(reportProgress, directory)