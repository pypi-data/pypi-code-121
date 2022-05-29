from scull.render import *

class TKRenderer(Renderer):
    def render_lines(self, skeleton, options={}):
        i = self.register(skeleton)
        base = {"color": "black", "width": 1}
        default = options.get("default", base)
        for name, bone in skeleton.bones.items():
            opt = options.get(name, default)
            self.target.create_line(bone.get_points(),
                fill=opt.get("color", default.get("color", base["color"])),
                width=opt.get("width", default.get("width", base["width"])),
                tag=skeleton.name + "_" + name + "_line")
    def clear_lines(self, skeleton):
        i = self.register(skeleton)
        for name in skeleton.bones.keys():
            self.target.delete(skeleton.name + "_" + name + "_line")
