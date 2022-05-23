import os
import yarl
import numpy as np
from deeplabel.label.gallery.images import Image

def url_to_name(url):
    return yarl.URL(url).name

def url_to_extension(url):
    """Return file's extension from url
    eg.
        .txt, .png, .jpg
    Note: Returns with presiding '.'
    """
    return os.path.splitext(url_to_name(url))[1]


def image_to_name(image:Image):
    """Image object to <image_id>.<image_extension>
    takes care of appropriate extension, i.e., jpg/png/etc
    """
    return image.image_id+url_to_extension(image.image_url)

def pascal_voc_color_map(N=256, normalized=False):
    """ Copied from: https://gist.github.com/wllhf/a4533e0adebe57e3ed06d4b50c8419ae
    And tested by doing Image.open('<some img from pascal dataset>').getpalette()
    """
    def bitget(byteval, idx):
        return ((byteval & (1 << idx)) != 0)

    dtype = 'float32' if normalized else 'uint8'
    cmap = np.zeros((N, 3), dtype=dtype)
    for i in range(N):
        r = g = b = 0
        c = i
        for j in range(8):
            r = r | (bitget(c, 0) << 7-j)
            g = g | (bitget(c, 1) << 7-j)
            b = b | (bitget(c, 2) << 7-j)
            c = c >> 3

        cmap[i] = np.array([r, g, b])

    cmap = cmap/255 if normalized else cmap
    return cmap