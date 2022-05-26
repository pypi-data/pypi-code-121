import json
import Famcy
import markdown

class pgm_viewer(Famcy.FamcyBlock):
    """
    Represents the block to display
    pgm_viewer. 
    """
    def __init__(self, **kwargs):
        self.value = pgm_viewer.generate_template_content()
        super(pgm_viewer, self).__init__(**kwargs)
        self.init_block()

    @classmethod
    def generate_template_content(cls, fblock_type=None):
        """
        This is the function that
        returns the template content 
        for the given fblock. 
        - Return a content dictionary
        """
        return {
            "title": "",
            "pgm_file_path": "/",
            "map_info_path": None,
            "position_files": [],
            "color_list": [],
            "tool_bar": True,
            "scaling_rate": 1.2
        }

    def init_block(self):
        self.body = Famcy.div()
        self.body["id"] = self.id
        self.body["className"] = "pgm_viewer"

        h3_temp = Famcy.h3()

        tool_div = Famcy.div()
        tool_div["className"] = "pgm_tool_bar"

        reset_btn = Famcy.button()
        # reset_btn.innerHTML = "reset"
        reset_btn["className"] = "bx bx-reset"
        reset_btn["onclick"] = "resetElement('%s')" % (self.id+"_canvas")

        drag_btn = Famcy.button()
        # drag_btn.innerHTML = "drag item"
        drag_btn["className"] = "bx bx-move"
        drag_btn["onclick"] = "dragElement(this, '%s')" % (self.id+"_canvas")

        zoom_in_btn = Famcy.button()
        # zoom_in_btn.innerHTML = "zoom in"
        zoom_in_btn["className"] = "bx bx-zoom-in"

        zoom_out_btn = Famcy.button()
        # zoom_out_btn.innerHTML = "zoom out"
        zoom_out_btn["className"] = "bx bx-zoom-out"

        draw_btn = Famcy.button()
        # draw_btn.innerHTML = "draw line"
        draw_btn["className"] = "bx bx-edit-alt"
        draw_btn["onclick"] = "drawArrowOnElement(this, '%s')" % (self.id+"_canvas")

        xy_btn = Famcy.button()
        # xy_btn.innerHTML = "get point value"
        xy_btn["className"] = "bx bx-crosshair"

        route_btn = Famcy.button()
        # route_btn.innerHTML = "display route"
        route_btn["className"] = "bx bx-trip"

        
        tool_div.addElement(reset_btn)
        tool_div.addElement(drag_btn)
        tool_div.addElement(zoom_in_btn)
        tool_div.addElement(zoom_out_btn)
        tool_div.addElement(draw_btn)
        tool_div.addElement(xy_btn)
        tool_div.addElement(route_btn)


        div_temp = Famcy.div()
        div_temp.style["position"] = "relative"
        div_temp.style["overflow"] = "hidden"
        div_temp["className"] = "pgm_canvas_holder"
        canvas_temp = Famcy.canvas()
        canvas_temp["id"] = self.id+"_canvas"
        canvas_temp["scale_rate"] = "1"
        canvas_temp["drag_flag"] = "false"
        canvas_temp["draw_flag"] = "false"
        canvas_temp["click_flag"] = "false"
        canvas_temp.style["position"] = "absolute"
        div_temp.addElement(canvas_temp)

        script = Famcy.script()

        self.body.addElement(h3_temp)
        self.body.addElement(tool_div)
        self.body.addElement(div_temp)
        self.body.addElement(script)

        static_script = Famcy.script()
        static_script["src"] = "/static/js/pgm_handler.js"
        self.body.addStaticScript(static_script, position="head")

        static_style = Famcy.style()
        static_style.innerHTML = """
        .pgm_viewer .pgm_tool_bar {
            width: 100%;
        }
        .pgm_viewer .pgm_tool_bar button {
            background-color: #ffffff;
            color: #2d2d2d;
            border: 1px #d1d1d1 solid;
            box-shadow: none;
            font-size: 20px;
        }

        .pgm_canvas_holder {
            border: 1px #d1d1d1 solid;
        }

        .pgm_btn_pressed {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        """
        self.body.addStaticScript(static_style, position="head")

    def read_pgm(self, pgmf):
        """Return a raster of integers from a PGM as a list of lists."""
        _ = pgmf.readline()
        _comment = pgmf.readline()
        (width, height) = [int(i) for i in pgmf.readline().split()]
        depth = int(pgmf.readline())

        raster = []
        for y in range(height):
            row = []
            for y in range(width):
                row.append(ord(pgmf.read(1)))
            raster.append(row)
        return width, height, raster

    def render_inner(self):
        extra_js = ""
        c_id = self.body.children[2].children[0]["id"]
        self.body.children[0].innerHTML = self.value["title"]

        if not self.value["tool_bar"]:
            self.body.children[1].style["display"] = "none"
        else:
            self.body.children[1].children[2]["onclick"] = "scaleElement('%s', %s)" % (self.id+"_canvas", str(self.value["scaling_rate"]))
            self.body.children[1].children[3]["onclick"] = "scaleElement('%s', %s)" % (self.id+"_canvas", str(1/self.value["scaling_rate"]))


        f = open(self.value["pgm_file_path"], 'rb')
        w, h, data = self.read_pgm(f)
        json_pgm_data = json.dumps(data)

        if self.value["map_info_path"]:
            map_info = Famcy.FManager.read(self.value["map_info_path"])
            resolution = map_info["resolution"]
            origin = map_info["origin"]
            json_map_origin = json.dumps(origin)

            extra_js += "function displayRobotRoute(){"

            for file_path, color in zip(self.value["position_files"], self.value["color_list"]):
                _yaml_data = Famcy.FManager.read(file_path)
                json_points_info = json.dumps(_yaml_data)
                extra_js += "displayRoute(%s, '%s', %s, %s, %s, %s, '%s');" % (json_points_info, c_id, resolution, json_map_origin, str(w), str(h), color)

            extra_js += "}"
            self.body.children[1].children[6]["onclick"] = "displayRobotRoute()"
            self.body.children[1].children[5]["onclick"] = "getPointXYValue(this, '%s', %s, %s, %s)" % (self.id+"_canvas", origin[0], origin[1], resolution)

        self.body.children[2].style["width"] = str(w)+"px"
        self.body.children[2].style["height"] = str(h)+"px"

        self.body.children[2].children[0]["width"] = str(w)
        self.body.children[2].children[0]["height"] = str(h)


        self.body.children[3].innerHTML = 'displayContents(%s, "%s");%s' % (json_pgm_data, c_id, extra_js)
        
        return self.body
        