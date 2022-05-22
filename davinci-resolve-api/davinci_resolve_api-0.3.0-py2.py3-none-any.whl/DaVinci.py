from __future__ import absolute_import
import imp
import sys

library = 'C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\fusionscript.dll'

try:
   _bmd = imp.load_dynamic('fusionscript', library)
except ImportError:
   sys.exit ('Unable to import Resolve API library.')

class DaVinci:

    @classmethod
    def Fusion(self):
        """
            Return Type: Fusion
            Comment: Returns the Fusion object. Starting point for Fusion scripts.
        """
        if not _bmd.scriptapp('Fusion'):
            sys.exit ('Fusion Not Found')
        return _bmd.scriptapp('Fusion')

    @classmethod
    def Resolve(self):
        """
            Return Type: Resolve
            Comment: Returns the Resolve object. Starting point for Resolve scripts.
        """
        if not _bmd.scriptapp('Resolve'):
            sys.exit ('Resolve Not Found')
        return _bmd.scriptapp('Resolve')

    @classmethod
    def GetMediaStorage(self):
        """
            Return Type: MediaStorage
            Comment: Returns the media storage object to query and act on media locations.
        """
        return self.Resolve().GetMediaStorage()

    @classmethod
    def GetProjectManager(self):
        """
            Return Type: ProjectManager
            Comment: Returns the project manager object for currently open database.
        """
        return self.Resolve().GetProjectManager()

    @classmethod
    def GetCurrentProject(self):
        """
            Return Type: CurrentProject
            Comment: Returns the Current Project object for currently open database.
        """
        return self.GetProjectManager().GetCurrentProject()

    @classmethod
    def GetCurrentTimeline(self):
        """
            Return Type: CurrentTimeline
            Comment: Returns the Current Timeline object for currently open database.
        """
        return self.GetCurrentProject().GetCurrentTimeline()

    @classmethod
    def GetMediaPool(self):
        """
            Return Type: Gallery
            Comment: Returns the Gallery object.
        """
        return self.GetCurrentProject().GetMediaPool()

    @classmethod
    def GetGallery(self):
        """
            Return Type: MediaPool
            Comment: Returns the MediaPool object for currently open database.
        """
        return self.GetCurrentProject().GetGallery()

    @classmethod
    def OpenPage(self, pageName):
        """
            Return Type: Bool
            Comment: Switches to indicated page in DaVinci Resolve. Input can be one of 
                ("media", "cut", "edit", "fusion", "color", "fairlight", "deliver").
        """
        return self.Resolve().OpenPage(pageName)

    @classmethod
    def GetCurrentPage(self):
        """
            Return Type: String
            Comment: Returns the page currently displayed in the main window. Returned value can be one of 
                ("media", "cut", "edit", "fusion", "color", "fairlight", "deliver", None).
        """
        return self.Resolve().GetCurrentPage()

    @classmethod
    def GetProductName(self):
        """
            Return Type: string
            Comment: Returns product name.
        """
        return self.Resolve().GetProductName()

    @classmethod
    def GetVersion(self):
        """
            Return Type: [version fields]
            Comment: Returns list of product version fields in [major, minor, patch, build, suffix] format.
        """
        return self.Resolve().GetVersion()

    @classmethod
    def GetVersionString(self):
        """
            Return Type: string
            Comment: Returns product version in "major.minor.patch[suffix].build" format.
        """
        return self.Resolve().GetVersionString()

    @classmethod
    def LoadLayoutPreset(self, presetName):
        """
            Return Type: Bool
            Comment: Loads UI layout from saved preset named 'presetName'.
        """
        return self.Resolve().LoadLayoutPreset(presetName)

    @classmethod
    def UpdateLayoutPreset(self, presetName):
        """
            Return Type: Bool
            Comment: Overwrites preset named 'presetName' with current UI layout.
        """
        return self.Resolve().UpdateLayoutPreset(presetName)

    @classmethod
    def ExportLayoutPreset(self, presetName, presetFilePath):
        """
            Return Type: Bool
            Comment: Exports preset named 'presetName' to path 'presetFilePath'.
        """
        return self.Resolve().ExportLayoutPreset(presetName, presetFilePath)

    @classmethod
    def DeleteLayoutPreset(self, presetName):
        """
            Return Type: Bool
            Comment: Deletes preset named 'presetName'.
        """
        return self.Resolve().DeleteLayoutPreset(presetName)

    @classmethod
    def SaveLayoutPreset(self, presetName):
        """
            Return Type: Bool
            Comment: Saves current UI layout as a preset named 'presetName'.
        """
        return self.Resolve().SaveLayoutPreset(presetName)

    @classmethod
    def ImportLayoutPreset(self, presetFilePath, presetName):
        """
            Return Type: Bool
            Comment: Imports preset from path 'presetFilePath'. The optional argument 'presetName' specifies how the preset shall be named. If not specified, the preset is named based on the filename.
        """
        return self.Resolve().ImportLayoutPreset(presetFilePath, presetName)

    @classmethod
    def Quit(self):
        """
            Return Type: None
            Comment: Quits the Resolve App.
        """
        return self.Resolve().Quit()