from __future__ import absolute_import
from davinci_resolve_api.DaVinci import DaVinci

class MediaPool:
    """
    All DaVinci Resolve MediaPool Related Stuff
    """

    _mediaPool = DaVinci.GetMediaPool()

    @classmethod
    def GetRootFolder(self):
        """
            Return Type: Folder
            Comment: Returns root Folder of Media Pool
        """
        return self._mediaPool.GetRootFolder()

    @classmethod
    def AddSubFolder(self, folder, name):
        """
            Return Type: Folder
            Comment: Adds new subfolder under specified Folder object with the given name.
        """
        return self._mediaPool.AddSubFolder(folder, name)
   
    @classmethod
    def CreateEmptyTimeline(self, name):
        """
            Return Type: Timeline
            Comment: Adds new timeline with given name.
        """
        return self._mediaPool.CreateEmptyTimeline(name)
    
    @classmethod
    def AppendToTimelineClip(self, clip):
        """
            Return Type: [TimelineItem]
            Comment: Appends specified MediaPoolItem objects in the current timeline. 
                Returns the list of appended timelineItems.
        """
        return self._mediaPool.AppendToTimeline(clip)
    
    @classmethod
    def AppendToTimelineClips(self, clips=list):
        """
            Return Type: [TimelineItem]
            Comment: Appends specified MediaPoolItem objects in the current timeline. 
                Returns the list of appended timelineItems.
        """
        return self._mediaPool.AppendToTimeline(clips)
   
    @classmethod
    def AppendToTimelineClipInfo(self, clipInfo):
        """        
            Return Type: [TimelineItem]
            Comment: Appends list of clipInfos specified as dict of 
                "mediaPoolItem", "startFrame" (int), "endFrame" (int), (optional) "mediaType" 
                (int; 1 - Video only, 2 - Audio only). Returns the list of appended timelineItems.
                [{clipInfo}, ...]
        """
        return self._mediaPool.AppendToTimeline(clipInfo)

    @classmethod
    def CreateTimelineFromClip(self, name, clip):
        """
            Return Type: Timeline
            Comment: Creates new timeline with specified name, and appends the specified MediaPoolItem objects.
        """
        return self._mediaPool.CreateTimelineFromClips(name, clip)
    
    @classmethod
    def CreateTimelineFromClips(self, name, clips=list):
        """
            Return Type: Timeline
            Comment: Creates new timeline with specified name, and appends the specified MediaPoolItem objects.
        """
        return self._mediaPool.CreateTimelineFromClips(name, clips)
    
    @classmethod
    def CreateTimelineFromClipInfo(self, name, clipInfo):
        """
        Return Type: Timeline
        Comment: Creates new timeline with specified name, appending the list of 
            clipInfos specified as a dict of "mediaPoolItem", "startFrame" (int), "endFrame" (int).
            [{clipInfo}]
        """
        return self._mediaPool.CreateTimelineFromClipInfo(name, clipInfo)
    
    @classmethod
    def ImportTimelineFromFile(self, filePath, importOptions=dict):
        """
        Return Type: Timeline
        Comment: Creates timeline based on parameters within given 
        file and optional importOptions dict, with support for the keys:
            - "timelineName": string, specifies the name of the timeline to be created
            - "importSourceClips": Bool, specifies whether source clips should be imported, True by default
            - "sourceClipsPath": string, specifies a filesystem path to search for source clips if 
                    the media is inaccessible in their original path and if "importSourceClips" is True
            - "sourceClipsFolders": List of Media Pool folder objects to search for source clips if
                    the media is not present in current folder and if "importSourceClips" is False
            - "interlaceProcessing": Bool, specifies whether to enable interlace processing on the 
                    imported timeline being created. valid only for AAF import
        """
        return self._mediaPool.ImportTimelineFromFile(filePath, importOptions)
    
    @classmethod
    def DeleteTimelines(self, timeline=list):
        """
            Return Type: Bool
            Comment: Deletes specified timelines in the media pool.
        """
        return self._mediaPool.DeleteTimelines(timeline)
    
    @classmethod
    def GetCurrentFolder(self):
        """
            Return Type: Folder
            Comment: Returns currently selected Folder.
        """
        return self._mediaPool.GetCurrentFolder()
    
    @classmethod
    def SetCurrentFolder(self, Folder):
        """
            Return Type: Bool
            Comment: Sets current folder by given Folder.
        """
        return self._mediaPool.SetCurrentFolder(Folder)
    
    @classmethod
    def DeleteClips(self, clips=list):
        """
            Return Type: Bool
            Comment: Deletes specified clips or timeline mattes in the media pool
        """
        return self._mediaPool.DeleteClips(clips)
    
    @classmethod
    def DeleteFolders(self, subfolders=list):
        """
            Return Type: Bool
            Comment: Deletes specified subfolders in the media pool
        """
        return self._mediaPool.DeleteFolders(subfolders)
    
    @classmethod
    def MoveClips(self, clips=list, targetFolder=any):
        """
            Return Type: Bool
            Comment: Moves specified clips to target folder.
        """
        return self._mediaPool.MoveClips(clips, targetFolder)
    
    @classmethod
    def MoveFolders(self, folders=list, targetFolder=any):
        """
            Return Type: Bool
            Comment: Moves specified folders to target folder.
        """
        return self._mediaPool.MoveFolders(folders, targetFolder)
    
    @classmethod
    def GetClipMatteList(self, MediaPoolItem):
        """
            Return Type: [paths]
            Comment: Get mattes for specified MediaPoolItem, as a list of paths to the matte files.
        """
        return self._mediaPool.GetClipMatteList(MediaPoolItem)
    
    @classmethod
    def GetTimelineMatteList(self, Folder):
        """
            Return Type: [MediaPoolItems]
            Comment: Get mattes in specified Folder, as list of MediaPoolItems.
        """
        return self._mediaPool.GetTimelineMatteList(Folder)

    @classmethod
    def pMattes(self, MediaPoolItem, paths=list):
        """
            Return Type: Bool
            Comment: Delete mattes based on their file paths, 
                for specified MediaPoolItem. Returns True on success.
        """
        return self._mediaPool.pMattes(MediaPoolItem, paths)
    
    @classmethod
    def RelinkClips(self, MediaPoolItem=list, folderPath=any):
        """
            Return Type: Bool
            Comment: Update the folder location of specified media pool clips with the specified folder path.
        """
        return self._mediaPool.RelinkClips(MediaPoolItem, folderPath)
    
    @classmethod
    def UnlinkClips(self, MediaPoolItem=list):
        """
            Return Type: Bool
            Comment: Unlink specified media pool clips.
        """
        return self._mediaPool.UnlinkClips(MediaPoolItem)
   
    @classmethod
    def ImportMedia(self, items=list):
        """        
        Return Type: [MediaPoolItems]   
        Comment: Imports specified file/folder paths into current Media Pool folder. 
            Input is an array of file/folder paths. Returns a list of the MediaPoolItems created.
        """
        return self._mediaPool.ImportMedia(items)

    @classmethod
    def ImportMediaClipInfo(self, clipInfo):
        """
            Return Type: [MediaPoolItems]
            Comment: Imports file path(s) into current Media Pool folder as specified in list of clipInfo dict. 
                Returns a list of the MediaPoolItems created.
                Each clipInfo gets imported as one MediaPoolItem unless 'Show Individual Frames' is turned on.
            Example: 
                    ImportMedia([{"FilePath":"file_%03d.dpx", "StartIndex":1, "EndIndex":100}]) 
                    would import clip "file_[001-100].dpx".
                    [{clipInfo}]
        """
        return self._mediaPool.ImportMedia(clipInfo)
    
    @classmethod
    def ExportMetadata(self, fileName, clips=list):
        """
            Return Type: Bool
            Comment: Exports metadata of specified clips to 'fileName' in CSV format.
                If no clips are specified, all clips from media pool will be used.
        """
        return self._mediaPool.ExportMetadata(fileName, clips)