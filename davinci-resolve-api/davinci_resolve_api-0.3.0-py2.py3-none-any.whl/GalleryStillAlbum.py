from __future__ import absolute_import

class GalleryStillAlbum:
    """
        All DaVinci Resolve GalleryStillAlbum Related Stuff
            require: "_galleryStillAlbum"
            exemple:

                DaVinci.GetGallery().GetCurrentStillAlbum() ---> item

                DaVinci.GetGallery().GetCurrentStillAlbums() ---> List of items
    """

    def __init__(self, _galleryStillAlbum):
        self._galleryStillAlbum = _galleryStillAlbum

    def GetStills(self):
        """
            Return Type: [galleryStill]
            Comment: Returns the list of GalleryStill objects in the album.
        """
        return self.GetStills()

    def GetLabel(self, galleryStill):
        """
            Return Type: string
            Comment: Returns the label of the galleryStill.
        """
        return self.GetLabel(galleryStill)

    def SetLabel(self, galleryStill, label):
        """
            Return Type: Bool
            Comment: Sets the new 'label' to GalleryStill object 'galleryStill'.
        """
        return self.SetLabel(galleryStill, label)

    def ExportStills(self, galleryStill, folderPath, filePrefix, format):
        """
        Return Type: Bool
        Comment: Exports list of GalleryStill objects 
            '[galleryStill]' to directory 'folderPath', 
                with filename prefix 'filePrefix', 
                using file format 'format' (supported formats: dpx, cin, tif, jpg, png, ppm, bmp, xpm).
        """
        return self.SetLabel(galleryStill, folderPath, filePrefix, format)

    def DeleteStills(self, galleryStill):
        """
            Return Type: Bool
            Comment: Deletes specified list of GalleryStill objects '[galleryStill]'.
        """
        return self.DeleteStills(galleryStill)