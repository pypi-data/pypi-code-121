from __future__ import absolute_import
from davinci_resolve_api.DaVinci import DaVinci

class Gallery:
    """
        All DaVinci Resolve Gallery Related Stuff
            exemple: "galleryStillAlbum"

                _getCurrentStillAlbum =  (Gallery.GetCurrentStillAlbum())
                
                Gallery.GetAlbumName(_getCurrentStillAlbum)
    """
    _gallery = DaVinci.GetGallery()

    @classmethod
    def GetAlbumName(self, galleryStillAlbum):
        """
            Return Type: string 
            Comment: Returns the name of the GalleryStillAlbum object 'galleryStillAlbum'.
        """
        return self._gallery.GetAlbumName(galleryStillAlbum)

    @classmethod
    def SetAlbumName(self, galleryStillAlbum, albumName):
        """
            Return Type: Bool
            Comment: Sets the name of the GalleryStillAlbum object 'galleryStillAlbum' to 'albumName'.
        """
        return self._gallery.GetAlbumName(galleryStillAlbum, albumName)

    @classmethod
    def GetCurrentStillAlbum(self):
        """
            Return Type: galleryStillAlbum
            Comment: Returns current album as a GalleryStillAlbum object.
        """
        return self._gallery.GetCurrentStillAlbum()

    @classmethod
    def SetCurrentStillAlbum(self, galleryStillAlbum):
        """
            Return Type: Bool
            Comment: Sets current album to GalleryStillAlbum object 'galleryStillAlbum'.
        """
        return self._gallery.SetCurrentStillAlbum(galleryStillAlbum)

    @classmethod
    def GetGalleryStillAlbums(self):
        """
            Return Type: [galleryStillAlbum]
            Comment: Returns the gallery albums as a list of GalleryStillAlbum objects.
        """
        return self._gallery.GetGalleryStillAlbums()