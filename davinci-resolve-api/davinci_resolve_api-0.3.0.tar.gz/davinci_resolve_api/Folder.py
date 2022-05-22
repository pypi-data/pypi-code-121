from __future__ import absolute_import

class Folder:
    """
        All DaVinci Resolve Folder Related Stuff
            require: "_folder"
            exemple: MediaPool.GetCurrentFolder()
    """
    
    def __init__(self, _folder):
        self.item = _folder


    def GetClipList(self):
        """
            Return Type: [clips...]
            Comment: Returns a list of clips (items) within the folder.
        """
        return self.GetClipList()

    def GetName(self):
        """
            Return Type: string
            Comment: Returns the media folder name.
        """
        return self.GetName()

    def GetSubFolderList(self):
        """
            Return Type: [folders...]
            Comment: Returns a list of subfolders in the folder.
        """
        return self.GetSubFolderList()