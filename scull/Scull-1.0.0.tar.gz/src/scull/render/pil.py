from PIL import Image, ImageTk, ImageDraw, ImageOps
from scull.render.tk import *

class PILRenderer(TKRenderer):
    def __init__(self, target):
        self.target = target
        self.images = {}
        self.cache = {}
    
    def render_images(self, skeleton, options={}):
        images = self.images.get(skeleton.name, [])
        if skeleton.name not in self.images:
            self.images[skeleton.name] = images
        base = {"image": None, "effects": {}}
        default = options.get("default", base)
        for name, bone in skeleton.bones.items():
            opt = options.get(name, default)
            img = opt.get("image", default.get("image", base["image"]))
            effects = opt.get("effects", default.get("effects", base["effects"]))
            st = f"{img}{effects}{bone.length}"
            if st in self.cache:
                image = self.cache[st]
            else:
                image = Image.open(img).resize((bone.length, bone.length), 4)
                if effects != {}:
                    draw = ImageDraw.Draw(image)
                    width = image.size[0]
                    height = image.size[1]
                    pix = image.load()
                for effect, value in effects.items():
                    if effect == "shadow":
                        for i in range(width):
                            for j in range(height):
                                if pix[i, j][3] != 0:
                                    a = pix[i, j][0] - value
                                    b = pix[i, j][1] - value
                                    c = pix[i, j][2] - value
                                    if a < 0:
                                        a = 0
                                    if b < 0:
                                        b = 0
                                    if c < 0:
                                        c = 0
                                    draw.point((i, j), (a, b, c))
                    elif effect == "mirror":
                        if value:
                            image = ImageOps.flip(image)
                self.cache[st] = image
            image = image.rotate(-bone.get_rotation(), expand=True)
            center = bone.get_center()
            images.append(ImageTk.PhotoImage(image))
            self.target.create_image(center[0], center[1], image=images[-1], anchor="center", tag=skeleton.name + "_" + name + "_image")
    def clear_images(self, skeleton):
        for name in skeleton.bones.keys():
            self.target.delete(skeleton.name + "_" + name + "_image")
        self.images[skeleton.name] = []
