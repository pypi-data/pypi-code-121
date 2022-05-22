class VPost:
    def __init__(self):
        self.id = "0"
        self.title = None
        self.images = []
        self.url = None
        self.is_gallery = False


class GalleryAsVPost(VPost):
    def __init__(self, url):
        VPost.__init__(self)
        self.url = url
        self.is_gallery = True
