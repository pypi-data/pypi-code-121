from src.darktable_lut_generator.estimate_lut import make_lut_identity_normed, write_cube, main
import numpy as np
from PIL import ImageFilter, Image

def get_lut_pillow(
        # [r,g,b,channel(RGB)]
        lut_np
):
    lut_bgr = np.swapaxes(lut_np, 0, 2)
    return ImageFilter.Color3DLUT(size=lut_bgr.shape[0], table=lut_bgr.flatten())


path_ref_test = '/samples/exported/ref.png'
path_raw_test = '/samples/exported/raw.png'
level = 3

paths = [
    (
        path_ref_test,
        path_raw_test,
    )
]

path_samples = '/samples/provia'

cube_out = '/home/bjoern/Pictures/hald-clut/HaldCLUT/own/provia.cube'

identity = make_lut_identity_normed(16)
# write_hald(identity, file_out)

lut = main(path_samples, cube_out, level=3, n_pixels_sample=1000000)

# lut = estimate_lut(paths, size=level ** 2, n_pixels_sample=1000)
# lut = identity

ref = Image.open(path_ref_test)
raw = Image.open(path_raw_test)

lut_pil = get_lut_pillow(lut)
transformed = raw.filter(lut_pil)

ref.show('reference')
transformed.show('transformed')

# write_hald(lut, 'hald.png', 8)
# write_hald(lut, file_out, 8)

write_cube(lut, cube_out)

# image_lut = Image.open(file_out)
# lut_loaded = pillow_lut.load_hald_image(image_lut, target_mode='RGB')
# lut_cube = pillow_lut.load_cube_file(cube_out)
#
# transformed = raw.filter(lut_loaded)
# transformed_cube = raw.filter(lut_cube)

# transformed.show('transformed from file')
# transformed_cube.show('transformed from cube')
# raw.show('raw')
