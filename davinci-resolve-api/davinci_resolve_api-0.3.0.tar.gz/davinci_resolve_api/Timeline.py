from __future__ import absolute_import
from davinci_resolve_api.DaVinci import DaVinci

class Timeline:
    """
        All DaVinci Resolve Timeline Related Stuff
    """

    _timeline = DaVinci.GetCurrentTimeline()

    @classmethod
    def GetName(self):
        """        
            Return Type: string
            Comment: Returns the timeline name.
        """
        return self._timeline.GetName()

    @classmethod
    def SetName(self, timelineName):
        """
            Return Type: Bool               
            Comment: Sets the timeline name if timelineName (string) is unique. Returns True if successful.
        """
        return self._timeline.SetName(timelineName)

    @classmethod
    def GetStartFrame(self):
        """
            Return Type: int
            omment:  Returns the frame number at the start of timeline.
        """
        return self._timeline.GetStartFrame()

    @classmethod
    def GetEndFrame(self):        
        """
            Return Type: int
            Comment: Returns the frame number at the end of timeline.
        """
        return self._timeline.GetEndFrame()

    @classmethod
    def SetStartTimecode(self, timecode):
        """
        Return Type: Bool
        Comment: Set the start timecode of the timeline to the string 'timecode'. 
            Returns true when the change is successful, false otherwise.
        """
        return self._timeline.SetStartTimecode(timecode)
   
    @classmethod
    def GetStartTimecode(self):
        """
            Return Type: string
            Comment: Returns the start timecode for the timeline.
        """
        return self._timeline.GetStartTimecode()

    @classmethod
    def GetTrackCount(self, trackType):
        """
            Return Type: int
            Comment: Returns the number of tracks for the given track type ("audio", "video" or "subtitle").
        """
        return self._timeline.GetTrackCount(trackType)

    @classmethod
    def GetItemListInTrack(self, trackType, index):
        """        
            Return Type: [items...]
            Comment: Returns a list of timeline items on that track (based on trackType and index). 
            1 <= index <= GetTrackCount(trackType).
        """
        return self._timeline.GetItemListInTrack(trackType, index)

    @classmethod
    def AddMarker(self, frameId, color, name, note, duration, customData=None):
        """
            Return Type: Bool
            Comment: Creates a new marker at given frameId position and with given marker information. 
            'customData' is optional and helps to attach user specific data to the marker.
        """
        return self._timeline.GetItemListInTrack(frameId, color, name, note, duration, customData)

    @classmethod
    def GetMarkers(self):
        """
        Return Type: {markers...}
        Comment: Returns a dict (frameId -> {information}) of all markers and dicts with their information.
            Example: 
            a value of {96.0: {'color': 'Green', 'duration': 1.0, 'note': '', 'name': 'Marker 1', 'customData': ''}, ...} 
            indicates a single green marker at timeline offset 96
        """
        return self._timeline.GetMarkers()

    @classmethod
    def GetMarkerByCustomData(self, customData):
        """
            Return Type: {markers...}
            Comment: Returns marker {information} for the first matching marker with specified customData.
        """
        return self._timeline.GetMarkerByCustomData(customData)

    @classmethod
    def UpdateMarkerCustomData(self, frameId, customData):
        """
            Return Type: Bool
            Comment: Updates customData (string) for the marker at given frameId position. 
                CustomData is not exposed via UI and is useful for scripting developer 
                to attach any user specific data to markers.
        """
        return self._timeline.UpdateMarkerCustomData(frameId, customData)

    @classmethod
    def GetMarkerCustomData(self, frameId):
        """
            Return Type: string
            Comment: Returns customData string for the marker at given frameId position.
        """
        return self._timeline.GetMarkerCustomData(frameId)

    @classmethod
    def DeleteMarkersByColor(self, color):
        """
            Return Type: Bool
            Comment: Deletes all timeline markers of the specified color. 
                An "All" argument is supported and deletes all timeline markers.
        """
        return self._timeline.DeleteMarkersByColor(color)

    @classmethod
    def DeleteMarkerAtFrame(self, frameNum):
        """
            Return Type: Bool
            Comment: Deletes the timeline marker at the given frame number.
        """
        return self._timeline.DeleteMarkerAtFrame(frameNum)

    @classmethod
    def DeleteMarkerByCustomData(self, customData):
        """
            Return Type: Bool
            Comment: Delete first matching marker with specified customData.
        """
        return self._timeline.DeleteMarkerByCustomData(customData)

    @classmethod
    def ApplyGradeFromDRX(self, path, gradeMode, items=list):
        """
            Return Type: Bool
            Comment: Loads a still from given file path (string) and applies grade to 
                Timeline Items with gradeMode 
                (int): 0 - "No keyframes", 1 - "Source Timecode aligned", 2 - "Start Frames aligned".
        """
        return self._timeline.ApplyGradeFromDRX(path, gradeMode, items)

    @classmethod
    def GetCurrentTimecode(self):
        """
            Return Type: string
            Comment: Returns a string timecode representation for the current playhead position, 
                while on Cut, Edit, Color, Fairlight and Deliver pages.
        """
        return self._timeline.GetCurrentTimecode()

    @classmethod
    def SetCurrentTimecode(self, timecode):
        """
            Return Type: Bool
            Comment: Sets current playhead position from input timecode for Cut, Edit, Color, Fairlight and Deliver pages.
        """
        return self._timeline.SetCurrentTimecode(timecode)

    @classmethod
    def GetCurrentVideoItem(self):
        """
            Return Type: item
            Comment: Returns the current video timeline item.
        """
        return self._timeline.GetCurrentVideoItem()

    @classmethod
    def GetCurrentClipThumbnailImage(self):
        """
            Return Type: {thumbnailData}
            Comment: Returns a dict (keys "width", "height", "format" and "data") with data containing raw thumbnail 
                image data (RGB 8-bit image data encoded in base64 format) for current media in the Color Page.
                An example of how to retrieve and interpret thumbnails is provided in 
                6_get_current_media_thumbnail.py in the Examples folder.
        """
        return self._timeline.GetCurrentClipThumbnailImage()

    @classmethod
    def GetTrackName(self, trackType, trackIndex):
        """"
            Return Type: string
            Comment: Returns the track name for track indicated by trackType ("audio", "video" or "subtitle") and index. 
                1 <= trackIndex <= GetTrackCount(trackType).
        """
        return self._timeline.GetTrackName(trackType, trackIndex)

    @classmethod
    def SetTrackName(self, trackType, trackIndex, name):
        """
            Return Type: Bool
            Comment: Sets the track name (string) for track indicated by trackType ("audio", "video" or "subtitle") and index. 
                1 <= trackIndex <= GetTrackCount(trackType).
        """
        return self._timeline.GetTrackName(trackType, trackIndex, name)

    @classmethod
    def DuplicateTimeline(self, timelineName):
        """
            Return Type: timeline
            Comment: Duplicates the timeline and returns the created timeline, with the (optional) timelineName, on success.
        """
        return self._timeline.DuplicateTimeline(timelineName)

    @classmethod
    def CreateCompoundClip(self, timelineItems=list, clipInfo=dict):
        """
        Return Type: timelineItem
        Comment: Creates a compound clip of input timeline items with an optional clipInfo map: 
            {"startTimecode" : "00:00:00:00", "name" : "Compound Clip 1"}. It returns the created timeline item.
        """
        return self._timeline.CreateCompoundClip(timelineItems, clipInfo)

    @classmethod
    def CreateFusionClip(self, timelineItems=list):
        """
            Return Type: timelineItem
            Comment: Creates a Fusion clip of input timeline items. It returns the created timeline item.
        """
        return self._timeline.CreateFusionClip(timelineItems)

    @classmethod
    def ImportIntoTimeline(self, filePath, importOptions=dict):
        """
            Return Type: Bool
            Comment: Imports timeline items from an AAF file and optional importOptions dict 
                into the timeline, with support for the keys:
            - "autoImportSourceClipsIntoMediaPool": 
                    - Bool, specifies if source clips should be imported into media pool, True by default
            - "ignoreFileExtensionsWhenMatching": 
                    - Bool, specifies if file extensions should be ignored when matching, False by default
            - "linkToSourceCameraFiles": 
                    - Bool, specifies if link to source camera files should be enabled, False by default
            - "useSizingInfo": 
                    - Bool, specifies if sizing information should be used, False by default
            - "importMultiChannelAudioTracksAsLinkedGroups": 
                    - Bool, specifies if multi-channel audio tracks should be imported as linked groups, False by default
            - "insertAdditionalTracks": 
                    - Bool, specifies if additional tracks should be inserted, True by default
            - "insertWithOffset": 
                    - string, specifies insert with offset value in timecode format - 
                    defaults to "00:00:00:00", applicable if "insertAdditionalTracks" is False
            - "sourceClipsPath": 
                    - string, specifies a filesystem path to search for source clips if the media is 
                    inaccessible in their original path and if "ignoreFileExtensionsWhenMatching" is True
            - "sourceClipsFolders": 
                    - string, list of Media Pool folder objects to search for source clips if the media 
                    is not present in current folder
        """
        return self._timeline.ImportIntoTimeline(filePath, importOptions)

    @classmethod
    def Export(self, fileName, exportType, exportSubtype):
        """
            Return Type: Bool
            Comment: Exports timeline to 'fileName' as per input exportType & exportSubtype format.
                Refer to section "Looking up timeline exports properties" for information on the parameters.
        """
        return self._timeline.Export(fileName, exportType, exportSubtype)

    @classmethod
    def GetAllSettings(self):
        """
            Return Type: string
            Comment: Returns name and value of all timeline setting : string). 
        """
        return self._timeline.GetSetting('')

    @classmethod
    def GetSetting(self, settingName):
        """
            Return Type: string
            Comment: Returns value of timeline setting (indicated by settingName : string). 
                Check the Timeline.GetAllSettings() for more information.
        """
        return self._timeline.GetSetting(settingName)

    @classmethod
    def SetSetting(self, settingName, settingValue):
        """
            Return Type: Bool
            Comment: Sets timeline setting (indicated by settingName : string) to the value (settingValue : string). 
                Check the Timeline.GetAllSettings() for more information.
        """
        return self._timeline.SetSetting(settingName, settingValue)

    @classmethod
    def InsertGeneratorIntoTimeline(self, generatorName):
        """
            Return Type: TimelineItem
            Comment: Inserts a generator (indicated by generatorName : string) into the timeline.
        """
        return self._timeline.InsertGeneratorIntoTimeline(generatorName)

    @classmethod
    def InsertFusionGeneratorIntoTimeline(self, generatorName):
        """
            Return Type: TimelineItem
            Comment: Inserts a Fusion generator (indicated by generatorName : string) into the timeline.
        """
        return self._timeline.InsertFusionGeneratorIntoTimeline(generatorName)

    @classmethod
    def InsertFusionCompositionIntoTimeline(self):
        """
            Return Type: TimelineItem
            Comment: Inserts a Fusion composition into the timeline.
        """
        return self._timeline.InsertFusionCompositionIntoTimeline()

    @classmethod
    def InsertOFXGeneratorIntoTimeline(self, generatorName):
        """
            Return Type: TimelineItem
            Comment: Inserts an OFX generator (indicated by generatorName : string) into the timeline.
        """
        return self._timeline.InsertOFXGeneratorIntoTimeline(generatorName)

    @classmethod
    def InsertTitleIntoTimeline(self, titleName):
        """
            Return Type: TimelineItem
            Comment: Inserts a title (indicated by titleName : string) into the timeline.
        """
        return self._timeline.InsertTitleIntoTimeline(titleName)

    @classmethod
    def InsertFusionTitleIntoTimeline(self, titleName):
        """
            Return Type: TimelineItem
            Comment: Inserts a Fusion title (indicated by titleName : string) into the timeline.
        """
        return self._timeline.InsertFusionTitleIntoTimeline(titleName)

    @classmethod
    def GrabStill(self):
        """
            Return Type: galleryStill
            Comment: Grabs still from the current video clip. Returns a GalleryStill object.
        """
        return self._timeline.GrabStill()

    @classmethod
    def GrabAllStills(self, stillFrameSource):
        """
            Return Type: [galleryStill]
            Comment: Grabs stills from all the clips of the timeline at 'stillFrameSource' 
                (1 - First frame, 2 - Middle frame). Returns the list of GalleryStill objects.
        """
        return self._timeline.GrabAllStills(stillFrameSource)