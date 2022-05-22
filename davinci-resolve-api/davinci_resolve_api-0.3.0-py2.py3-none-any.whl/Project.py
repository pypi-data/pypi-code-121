from __future__ import absolute_import
from davinci_resolve_api.DaVinci import DaVinci

class Project:
    """
    All DaVinci Resolve Project Related Stuff
    """
    
    _currentProject = DaVinci.GetCurrentProject()

    @classmethod
    def GetMediaPool(self):
        """
            Return Type: MediaPool
            Comment: Returns the Media Pool object.
        """
        return self._currentProject.GetMediaPool()

    @classmethod
    def GetTimelineCount(self):
        """
            Return Type: int
            Comment: Returns the number of timelines currently present in the project.
        """
        return self._currentProject.GetTimelineCount()

    @classmethod
    def GetTimelineByIndex(self, idx):
        """
            Return Type: Timeline
            Comment: Returns timeline at the given index, 1 <= idx <= project.GetTimelineCount(self):
        """
        return self._currentProject.GetTimelineByIndex(idx)
    
    @classmethod
    def GetCurrentTimeline(self):
        """
            Return Type: Timeline
            Comment: Returns the currently loaded timeline.
        """
        return self._currentProject.GetCurrentTimeline()
    
    @classmethod
    def SetCurrentTimeline(self, timeline):
        """
            Return Type: Bool
            Comment: Sets given timeline as current timeline for the project. Returns True if successful.
        """
        return self._currentProject.SetCurrentTimeline(timeline)
    
    @classmethod
    def GetGallery(self):
        """
            Return Type: Gallery
            Comment: Returns the Gallery object.
        """
        return self._currentProject.GetGallery()
    
    @classmethod
    def GetName(self):
        """
            Return Type: string
            Comment: Returns project name.
        """
        return self._currentProject.GetName()
    
    @classmethod
    def SetName(self, projectName):
        """
            Return Type: Bool
            Comment: Sets project name if given projectname (string) is unique.
        """
        return self._currentProject.SetName(projectName)
    
    @classmethod
    def GetPresetList(self):
        """
            Return Type: [presets...]
            Comment: Returns a list of presets and their information.
        """
        return self._currentProject.GetPresetList()
    
    @classmethod
    def SetPreset(self, presetName):
        """
            Return Type: Bool
            Comment: Sets preset by given presetName (string) into project.
        """
        return self._currentProject.SetPreset(presetName)

    @classmethod
    def AddRenderJob(self):
        """
            Return Type: string
            Comment: Adds a render job based on current render settings to the render queue. 
                Returns a unique job id (string) for the new render job.
        """
        return self._currentProject.AddRenderJob()
    
    @classmethod
    def DeleteRenderJob(self, jobId):
        """
            Return Type: Bool
            Comment: Deletes render job for input job id (string).
        """
        return self._currentProject.DeleteRenderJob(jobId)

    @classmethod
    def DeleteAllRenderJobs(self):
        """
            Return Type: Bool
            Comment: Deletes all render jobs in the queue.
        """
        return self._currentProject.DeleteAllRenderJobs()

    @classmethod
    def GetRenderJobList(self):
        """
            Return Type: [render jobs...]
            Comment: Returns a list of render jobs and their information.
        """
        return self._currentProject.GetRenderJobList()
   
    @classmethod
    def GetRenderPresetList(self):
        """
            Return Type: [presets...]
            Comment: Returns a list of render presets and their information.
        """
        return self._currentProject.GetRenderPresetList()
   
    @classmethod
    def StartRenderingJob(self, jobId=str):
        """
            Return Type: Bool
            Comment: Starts rendering job indicated by the input job id.
        """
        return self._currentProject.StartRenderingJob(jobId)
    
    @classmethod
    def StartRendering(self, jobIds=list, isInteractiveMode=False):
        """
            Return Type: Bool
            Comment: Starts rendering jobs indicated by the input job ids.
                The optional "isInteractiveMode", when set, enables error feedback in the UI during rendering.
        """
        return self._currentProject.StartRendering(jobIds, isInteractiveMode)
      
    @classmethod
    def StopRendering(self):
        """
            Return Type: None
            Comment: Stops any current render processes.
        """
        return self._currentProject.StopRendering()
   
    @classmethod
    def IsRenderingInProgress(self):
        """
            Return Type: Bool
            Comment: Returns True if rendering is in progress.
        """
        return self._currentProject.IsRenderingInProgress()
    
    @classmethod
    def LoadRenderPreset(self, presetName):
        """
            Return Type: Bool
            Comment: Sets a preset as current preset for rendering if presetName (string) exists.
        """
        return self._currentProject.LoadRenderPreset(presetName)

    @classmethod
    def SaveAsNewRenderPreset(self, presetName):
        """
            Return Type: Bool
            Comment: Creates new render preset by given name if presetName(string) is unique.
        """
        return self._currentProject.SaveAsNewRenderPreset(presetName)

    @classmethod
    def SetRenderSettings(self, settings=dict):
        """
            Return Type: Bool
            Comment: Sets given settings for rendering. Settings is a dict, with support for the keys:
                Refer to "Looking up render settings" section for information for supported settings
        """
        return self._currentProject.SetRenderSettings(settings)

    @classmethod
    def GetRenderJobStatus(self, jobId):
        """
            Return Type: {status info}
            Comment: Returns a dict with job status and completion percentage of the job by given jobId (string).
        """
        return self._currentProject.GetRenderJobStatus(jobId)
   
    @classmethod
    def GetAllSetting(self):
        """
            Return Type: string
            Comment: Returns key and value of project setting.
        """
        return self._currentProject.GetSetting('')

    @classmethod
    def GetSetting(self, settingName):
        """
            Return Type: string
            Comment: Returns value of project setting (indicated by settingName, string). 
                Check the Project.GetAllSetting() for more information.
        """
        return self._currentProject.GetSetting(settingName)

    @classmethod
    def SetSetting(self, settingName, settingValue):
        """
            Return Type: Bool
            Comment: Sets the project setting (indicated by settingName, string) to the value (settingValue, string).
                Check the Project.GetAllSetting() for more information.
        """
        return self._currentProject.SetSetting(settingName, settingValue)
   
    @classmethod
    def GetRenderFormats(self):
        """
            Return Type: {render formats..}
            Comment: Returns a dict (format -> file extension) of available render formats.
        """
        return self._currentProject.GetRenderFormats()
    
    @classmethod
    def GetRenderCodecs(self, renderFormat):
        """
            Return Type: {render codecs...}
            Comment: Returns a dict (codec description -> codec name) of 
                available codecs for given render format (string).
        """
        return self._currentProject.GetRenderCodecs(renderFormat)
   
    @classmethod
    def GetCurrentRenderFormatAndCodec(self):
        """
            Return Type: {format, codec}
            Comment: Returns a dict with currently selected format 'format' and render codec 'codec'.
        """
        return self._currentProject.GetCurrentRenderFormatAndCodec()
   
    @classmethod
    def SetCurrentRenderFormatAndCodec(self, format, codec):
        """
            Return Type: Bool
            Comment: Sets given render format (string) and render codec (string) as options for rendering.
        """
        return self._currentProject.SetCurrentRenderFormatAndCodec(format, codec)

    @classmethod
    def GetCurrentRenderMode(self):
        """
            Return Type: int
            Comment: Returns the render mode: 0 - Individual clips, 1 - Single clip.
        """
        return self._currentProject.GetCurrentRenderMode()

    @classmethod
    def SetCurrentRenderMode(self, renderMode):
        """
            Return Type: Bool
            Comment: Sets the render mode. Specify renderMode = 0 for Individual clips, 1 for Single clip.
        """
        return self._currentProject.SetCurrentRenderMode(renderMode)

    @classmethod
    def GetRenderResolutions(self, format, codec):
        """
            Return Type: [{Resolution}]
            Comment: Returns list of resolutions applicable for the given render format (string) and render codec (string). 
                Returns full list of resolutions if no argument is provided. Each element in the list is a dictionary 
                with 2 keys "Width" and "Height".
        """
        return self._currentProject.GetRenderResolutions(format, codec)

    @classmethod
    def RefreshLUTList(self):
        """
            Return Type: Bool
            Comment: Refreshes LUT List
        """
        return self._currentProject.RefreshLUTList()