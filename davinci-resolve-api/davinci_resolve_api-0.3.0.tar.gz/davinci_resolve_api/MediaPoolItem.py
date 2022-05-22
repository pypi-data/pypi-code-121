from __future__ import absolute_import

class MediaPoolItem():
    """
        All DaVinci Resolve MediaPoolItem Related Stuff
            require: "_mediaPoolItem"
            exemple: TimelineItem.GetMediaPoolItem()
    """

    def __init__(self, _mediaPoolItem):
        self._mediaPoolItem = _mediaPoolItem
         
    def GetName(self):
        """
            Return Type: string
            Comment: Returns the clip name.
        """
        return self.GetName()

    def GetMetadata(self, metadataType=None):
        """
            Return Type: string|dict
            Comment: Returns the metadata value for the key 'metadataType'.
            Comment: If no argument is specified, a dict of all set metadata properties is returned.
        """
        return self.GetMetadata(metadataType)

    def SetMetadata(self, metadataType, metadataValue):
        """
            Return Type: Bool
            Comment: Sets the given metadata to metadataValue (string). Returns True if successful.
        """
        return self.SetMetadata(metadataType, metadataValue)

    def SetMetadataDict(self, metadata=dict):
        """
            Return Type: Bool
            Comment: Sets the item metadata with specified 'metadata' dict. 
                Returns True if successful.
        """
        return self.SetMetadata(metadata)

    def GetMediaId(self):
        """
            Return Type: string
            Comment: Returns the unique ID for the MediaPoolItem.
        """
        return self.GetMediaId()

    def AddMarker(self, frameId, color, name, note, duration, customData):
        """
            Return Type: Bool
            Comment: Creates a new marker at given frameId position and with given marker information. 
                'customData' is optional and helps to attach user specific data to the marker.
        """
        return self.AddMarker(frameId, color, name, note, duration, customData)

    def GetMarkers(self):
        """
            Return Type: {markers...}
            Comment: Returns a dict (frameId -> {information}) of all markers and dicts with their information.
            Example of output format: 
                {96.0: {'color': 'Green', 'duration': 1.0, 'note': '', 'name': 'Marker 1', 'customData': ''}, ...}
            In the above example - there is one 'Green' marker at offset 96 (position of the marker)
        """
        return self.GetMarkers()

    def GetMarkerByCustomData(self, customData):
        """
            Return Type: {markers...}
            Comment: Returns marker {information} for the first matching marker with specified customData.
        """
        return self.GetMarkerByCustomData(customData)

    def UpdateMarkerCustomData(self, frameId, customData):
        """
            Return Type: Bool
            Comment: Updates customData (string) for the marker at given frameId position.
            CustomData is not exposed via UI and is useful for 
                scripting developer to attach any user specific data to markers.
        """
        return self.UpdateMarkerCustomData(frameId, customData)

    def GetMarkerCustomData(self, frameId):
        """
            Return Type: string
            Comment: Returns customData string for the marker at given frameId position.
        """
        return self.GetMarkerCustomData(frameId)

    def DeleteMarkersByColor(self, color):
        """
            Return Type: Bool
            Comment: Delete all markers of the specified color from the media pool item.
                "All" as argument deletes all color markers.
        """
        return self.DeleteMarkersByColor(color)

    def DeleteMarkerAtFrame(self, frameNum):
        """
            Return Type: Bool
            Comment: Delete marker at frame number from the media pool item.
        """
        return self.DeleteMarkerAtFrame(frameNum)

    def DeleteMarkerByCustomData(self, customData):
        """
            Return Type: Bool
            Comment: Delete first matching marker with specified customData.
        """
        return self.DeleteMarkerByCustomData(customData)

    def AddFlag(self, color):
        """
            Return Type: Bool
            Comment: Adds a flag with given color (string).
        """
        return self.AddFlag(color)

    def GetFlagList(self):
        """
            Return Type: [colors...]
            Comment: Returns a list of flag colors assigned to the item.
        """
        return self.GetFlagList()

    def ClearFlags(self, color):
        """
            Return Type: Bool
            Comment: Clears the flag of the given color if one exists.
                An "All" argument is supported and clears all flags.
        """
        return self.ClearFlags(color)

    def GetClipColor(self):
        """
            Return Type: string
            Comment: Returns the item color as a string.
        """
        return self.GetClipColor()

    def SetClipColor(self, colorName):
        """
            Return Type: Bool
            Comment: Sets the item color based on the colorName (string).
        """
        return self.SetClipColor(colorName)

    def ClearClipColor(self):
        """
            Return Type: Bool
            Comment: Clears the item color.
        """
        return self.ClearClipColor()

    def GetClipProperty(self, propertyName=None):
        """
            Return Type: string|dict
            Comment: Returns the property value for the key 'propertyName'. 
                If no argument is specified, a dict of all clip properties is returned. 
                Check the section below for more information.
        """
        return self.GetClipProperty(propertyName)

    def SetClipProperty(self, propertyName, propertyValue):
        """
            Return Type: Bool
            Comment: Sets the given property to propertyValue (string). 
                Check the section below for more information.
        """
        return self.SetClipProperty(propertyName, propertyValue)

    def LinkProxyMedia(self, proxyMediaFilePath):
        """        
            Return Type: Bool               
            Comment: Links proxy media located at path specified by arg 'proxyMediaFilePath' 
                with the current clip. 'proxyMediaFilePath' should be absolute clip path.
        """
        return self.LinkProxyMedia(proxyMediaFilePath)

    def UnlinkProxyMedia(self):   
        """
            Return Type: Bool
            Comment: Unlinks any proxy media associated with clip.
        """
        return self.UnlinkProxyMedia()

    def ReplaceClip(self, filePath):
        """
            Return Type: Bool
            Comment: Replaces the underlying asset and metadata of 
                MediaPoolItem with the specified absolute clip path.
        """
        return self.ReplaceClip(filePath)