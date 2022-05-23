from typing import Tuple, Optional
from urllib import request as ulreq
from PIL import ImageFile
 
def img_shape_from_url(uri)->Tuple[Optional[int],Optional[int]]:
    """return width, height of the image"""
    # get file size *and* image size (None if not known)
    file = ulreq.urlopen(uri)
    size = file.headers.get("content-length")
    if size: 
        size = int(size)
    p = ImageFile.Parser()
    while True:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return p.image.size
            break
    file.close()
    return None, None

if __name__=='__main__':
    print(img_shape_from_url("https://st2.depositphotos.com/3837271/8400/i/950/depositphotos_84002888-stock-photo-any-questions-written-on-a.jpg"))