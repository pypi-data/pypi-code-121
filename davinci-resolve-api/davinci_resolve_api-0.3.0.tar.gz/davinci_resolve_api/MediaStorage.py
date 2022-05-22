from __future__ import absolute_import
from davinci_resolve_api.DaVinci import DaVinci

class MediaStorage:
    """
    All DaVinci Resolve MediaStorage Related Stuff
    """

    _mediaStorage = DaVinci.GetMediaStorage()

    @classmethod
    def GetMountedVolumeList(self):
        """
            Return Type: [paths...]
            Comment: Returns list of folder paths corresponding to mounted volumes displayed in Resolve's Media Storage.
        """
        return self._mediaStorage.GetMountedVolumeList()

    @classmethod
    def GetSubFolderList(self, folderPath):
        """
            Return Type: [paths...]
            Comment: Returns list of folder paths in the given absolute folder path.
        """
        return self._mediaStorage.GetSubFolderList(folderPath)
   
    @classmethod
    def GetFileList(self, folderPath):
        """
            Return Type: [paths...]
            Comment: Returns list of media and file listings in the given absolute folder path. 
                Note that media listings may be logically consolidated entries.
        """
        return self._mediaStorage.GetFileList(folderPath)
   
    @classmethod
    def RevealInStorage(self, path):
        """
            Return Type: Bool
            Comment: Expands and displays given file/folder path in Resolve's Media Storage.
        """
        return self._mediaStorage.RevealInStorage(path)
  
    @classmethod
    def AddItemListToMediaPool(self, items=list):
        """
            Return Type: [clips...]
            Comment: Adds specified file/folder paths from Media Storage into current Media Pool folder. 
                Input is one or more file/folder paths. Returns a list of the MediaPoolItems created.
        """
        return self._mediaStorage.AddItemListToMediaPool(items)

    @classmethod
    def AddClipMattesToMediaPool(self, MediaPoolItem, paths=list, stereoEye=any):
        """
            Return Type: Bool   
            Comment: Adds specified media files as mattes for the specified MediaPoolItem. 
                StereoEye is an optional argument for specifying which eye to add the matte 
                to for stereo clips ("left" or "right"). Returns True if successful.
        """
        return self._mediaStorage.AddClipMattesToMediaPool(MediaPoolItem, paths, stereoEye)

    @classmethod
    def AddTimelineMattesToMediaPool(self, paths=list):
        """
            Return Type: [MediaPoolItems]
            Comment: Adds specified media files as timeline mattes in current media pool folder. 
                Returns a list of created MediaPoolItems.
        """
        return self._mediaStorage.AddTimelineMattesToMediaPool(paths)