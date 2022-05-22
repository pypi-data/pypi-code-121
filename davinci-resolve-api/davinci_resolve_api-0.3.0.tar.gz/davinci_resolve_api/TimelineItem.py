from __future__ import absolute_import

class TimelineItem:
    """
        All DaVinci Resolve TimelineItem Related Stuff
            require: "_timelineItem"
            exemple: Timeline.GetCurrentVideoItem()
    """

    def __init__(self, _timelineItem):
        self.item = _timelineItem

    def GetName(self):
        """
        Return Type: string
        Comment: Returns the item name.
        """
        return self.GetName()

    def GetDuration(self):
        """
            Return Type: int
            Comment: Returns the item duration.
        """
        return self.GetDuration()

    def GetEnd(self):
        """
            Return Type: int
            Comment: Returns the end frame position on the timeline.
        """
        return self.GetEnd()

    def GetFusionCompCount(self):
        """
            Return Type: int
            Comment: Returns number of Fusion compositions associated with the timeline item.
        """
        return self.GetFusionCompCount()

    def GetFusionCompByIndex(self, compIndex):
        """
            Return Type: fusionComp
            Comment: Returns the Fusion composition object based on given index. 
                1 <= compIndex <= timelineItem.GetFusionCompCount(self):
        """
        return self.GetFusionCompCount(compIndex)

    def GetFusionCompNameList(self):
        """
            Return Type: [names...]
            Comment: Returns a list of Fusion composition names associated with the timeline item.
        """
        return self.GetFusionCompNameList()

    def GetFusionCompByName(self, compName):
        """
            Return Type: fusionComp
            Comment: Returns the Fusion composition object based on given name.
        """
        return self.GetFusionCompByName(compName)

    def GetLeftOffset(self):
        """
            Return Type: int
            Comment: Returns the maximum extension by frame for clip from left side.
        """
        return self.GetLeftOffset()
    
    def GetRightOffset(self):
        """
            Return Type: int
            Comment: Returns the maximum extension by frame for clip from right side.
        """
        return self.GetRightOffset()

    def GetStart(self):
        """
            Return Type: int
            Comment: Returns the start frame position on the timeline.
        """
        return self.GetStart()

    def SetProperty(self, propertyKey, propertyValue):
        """
            Return Type: Bool
            Comment: Sets the value of property "propertyKey" to value "propertyValue"
                Refer to "Looking up Timeline item properties" for more information
        """
        return self.GetStart(propertyKey, propertyValue)

    def GetProperty(self, propertyKey):
        """
            Return Type: int/[key:value]
            Comment: returns the value of the specified key
                if no key is specified, the method returns a dictionary(python) or table(lua) for all supported keys
        """
        return self.GetStart(propertyKey)

    def AddMarker(self, frameId, color, name, note, duration, customData=None):
        """
            Return Type: Bool=
            Comment: Creates a new marker at given frameId position and with given marker information. 
                'customData' is optional and helps to attach user specific data to the marker.
        """
        return self.AddMarker(frameId, color, name, note, duration, customData)

    def GetMarkers(self):
        """
        Return Type: {markers...}
        Comment: Returns a dict (frameId -> {information}) of all markers and dicts with their information.
            Example: a value of 
            {96.0: {'color': 'Green', 'duration': 1.0, 'note': '', 'name': 'Marker 1', 'customData': ''}, ...} 
            indicates a single green marker at clip offset 96
        """
        return self.GetMarkers()

    def GetMarkerByCustomData(self, customData):
        """
            Return Type: {markers...}
            Comment: Returns marker {information} for the first matching marker with specified customData.
        """
        return self.GetMarkers(customData)

    def UpdateMarkerCustomData(self, frameId, customData):
        """
            Return Type: Bool
            Comment: Updates customData (string) for the marker at given frameId position.
                CustomData is not exposed via UI and is useful for scripting developer to 
                attach any user specific data to markers.
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
            Comment: Delete all markers of the specified color from the timeline item.
            "All" as argument deletes all color markers.
        """
        return self.DeleteMarkersByColor(color)

    def DeleteMarkerAtFrame(self, frameNum):
        """
            Return Type: Bool
            Comment: Delete marker at frame number from the timeline item.
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
            Comment: Clear flags of the specified color.
                An "All" argument is supported to clear all flags.
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

    def AddFusionComp(self):
        """
            Return Type: fusionComp
            Comment: Adds a new Fusion composition associated with the timeline item.
        """
        return self.AddFusionComp()

    def ImportFusionComp(self, path):
        """
            Return Type: fusionComp
            Comment: Imports a Fusion composition from given file path 
                by creating and adding a new composition for the item.
        """
        return self.ImportFusionComp(path)

    def ExportFusionComp(self, path, compIndex):
        """
            Return Type: Bool
            Comment: Exports the Fusion composition based on given index to the path provided.
        """
        return self.ExportFusionComp(path, compIndex)

    def DeleteFusionCompByName(self, compName):
        """
            Return Type: Bool
            Comment: Deletes the named Fusion composition.
        """
        return self.DeleteFusionCompByName(compName)

    def LoadFusionCompByName(self, compName):
        """
            Return Type: fusionComp
            Comment: Loads the named Fusion composition as the active composition.
        """
        return self.LoadFusionCompByName(compName)

    def RenameFusionCompByName(self, oldName, newName):
        """
            Return Type: Bool
            Comment: Renames the Fusion composition identified by oldName.
        """
        return self.RenameFusionCompByName(oldName, newName)

    def AddVersion(self, versionName, versionType):
        """
            Return Type: Bool
            Comment: Adds a new color version for a video clipbased on versionType (0 - local, 1 - remote).
        """
        return self.AddVersion(self, versionName, versionType)

    def GetCurrentVersion(self):
        """
            Return Type: {versionName...}
            Comment: Returns the current version of the video clip. The returned value will 
                have the keys versionName and versionType(0 - local, 1 - remote).
        """
        return self.GetCurrentVersion()

    def DeleteVersionByName(self, versionName, versionType):
        """
            Return Type: Bool
            Comment: Deletes a color version by name and versionType (0 - local, 1 - remote).
        """
        return self.DeleteVersionByName(versionName, versionType)

    def LoadVersionByName(self, versionName, versionType):
        """
            Return Type: Bool
            Comment: Loads a named color version as the active version. 
                versionType: 0 - local, 1 - remote.
        """
        return self.LoadVersionByName(versionName, versionType)

    def RenameVersionByName(self, oldName, newName, versionType):
        """
            Return Type: Bool
            Comment: Renames the color version identified 
                by oldName and versionType (0 - local, 1 - remote).
        """
        return self.RenameVersionByName(oldName, newName, versionType)

    def GetVersionNameList(self, versionType):
        """
            Return Type: [names...]
            Comment: Returns a list of all color versions 
                for the given versionType (0 - local, 1 - remote).
        """
        return self.GetVersionNameList(versionType)

    def GetMediaPoolItem(self):
        """
            Return Type: MediaPoolItem=
            Comment: Returns the media pool item corresponding to the timeline item if one exists.
        """
        return self.GetMediaPoolItem()

    def GetStereoConvergenceValues(self):
        """
            Return Type: {keyframes...}
            Comment: Returns a dict (offset -> value) of keyframe 
                offsets and respective convergence values.
        """
        return self.GetStereoConvergenceValues()

    def GetStereoLeftFloatingWindowParams(self):
        """
            Return Type: {keyframes...}
            Comment: For the LEFT eye -> returns a dict (offset -> dict) of keyframe 
                offsets and respective floating window params. 
            Value at particular offset includes the left, right, top and bottom floating window values.
        """
        return self.GetStereoLeftFloatingWindowParams()

    def GetStereoRightFloatingWindowParams(self):
        """
            Return Type: {keyframes...}
            Comment: For the RIGHT eye -> returns a dict (offset -> dict) of keyframe 
                offsets and respective floating window params. 
            Value at particular offset includes the left, right, top and bottom floating window values.
        """
        return self.GetStereoRightFloatingWindowParams()

    def SetLUT(self, nodeIndex, lutPath):
        """
            Return Type: Bool
            Comment: Sets LUT on the node mapping the node index provided, 1 <= nodeIndex <= total number of nodes.
                The lutPath can be an absolute path, or a relative path 
                    (based off custom LUT paths or the master LUT path).
                The operation is successful for valid lut paths that 
                    Resolve has already discovered (see Project.RefreshLUTList).
        """
        return self.SetLUT(nodeIndex, lutPath)

    def SetCDL(self, CDL_map=list):
        """
            Return Type: Bool
            Comment: Keys of map are: 
                "NodeIndex", "Slope", "Offset", "Power", "Saturation", where 1 <= NodeIndex <= total number of nodes.
            Example python code 
            SetCDL({"NodeIndex" : "1", "Slope" : "0.5 0.4 0.2", "Offset" : "0.4 0.3 0.2", "Power" : "0.6 0.7 0.8", "Saturation" : "0.65"})
        """
        return self.SetCDL(CDL_map)

    def AddTake(self, mediaPoolItem, startFrame, endFrame):
        """
            Return Type: Bool
            Comment: Adds mediaPoolItem as a new take. 
                Initializes a take selector for the timeline item if needed.
                By default, the full clip extents is added. startFrame (int) and endFrame (int) are 
                    optional arguments used to specify the extents.
        """
        return self.AddTake(mediaPoolItem, startFrame, endFrame)

    def GetSelectedTakeIndex(self):
        """
            Return Type: int
            Comment: Returns the index of the currently selected take, or 0 if the clip is not a take selector.
        """
        return self.GetSelectedTakeIndex()

    def GetTakesCount(self):
        """
            Return Type: int
            Comment: Returns the number of takes in take selector, or 0 if the clip is not a take selector.
        """
        return self.GetTakesCount()

    def GetTakeByIndex(self, idx):
        """
            Return Type: {takeInfo...}
            Comment: Returns a dict (keys "startFrame", "endFrame" and "mediaPoolItem") 
                with take info for specified index.
        """
        return self.GetTakeByIndex(idx)

    def DeleteTakeByIndex(self, idx):
        """
            Return Type: Bool
            Comment: Deletes a take by index, 1 <= idx <= number of takes.
        """
        return self.DeleteTakeByIndex(idx)

    def SelectTakeByIndex(self, idx):
        """
            Return Type: Bool
            Comment: Selects a take by index, 1 <= idx <= number of takes.
        """
        return self.SelectTakeByIndex(idx)

    def FinalizeTake(self):
        """
            Return Type: Bool
            Comment: Finalizes take selection.
        """
        return self.FinalizeTake()

    def CopyGrades(self, tgtTimelineItems=list):
        """
        Return Type: Bool
        Comment: Copies the current grade to all the items in tgtTimelineItems list.
            Returns True on success and False if any error occured.
        """
        return self.CopyGrades(tgtTimelineItems)