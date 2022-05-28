import argparse
import os
import re
import time

import torch

import cvee

try:
    import open3d as o3d
    import open3d.visualization.gui as gui
    import open3d.visualization.rendering as rendering
except:
    pass

file_exts = {"point_cloud": "ply", "mesh": "ply", "line_set": "ply"}


class VisO3D:
    def __init__(self, vis_dir=None):
        self.scene_idx = int(0)
        self.default_scene_num = 1
        self.vis_dir = vis_dir
        self.save_num = 0

    def __len__(self):
        return self.default_scene_num

    def _init_ui(self):
        app = gui.Application.instance
        self.window = app.create_window("vis - O3D", 1200, 800)
        w = self.window  # to make the code more concise

        # 3D widget
        self._3d = gui.SceneWidget()
        self._3d.scene = rendering.Open3DScene(self.window.renderer)

        ibl_name = gui.Application.instance.resource_path + "/" + "default"
        self._3d.scene.scene.enable_indirect_light(True)
        self._3d.scene.scene.set_indirect_light(ibl_name)
        self._3d.scene.scene.set_indirect_light_intensity(45000)

        self._3d.scene.scene.enable_sun_light(True)
        self._3d.scene.scene.set_sun_light([0.577, 0.577, 0.577], [1.0, 1.0, 1.0], 45000)
        self._3d.set_on_sun_direction_changed(self._on_sun_dir)

        self._3d.enable_scene_caching(True)
        self._3d.scene.show_axes(True)
        self._3d.set_on_key(self._on_key_3d)

        # Right Panel
        # Rather than specifying sizes in pixels, which may vary in size based
        # on the monitor, especially on macOS which has 220 dpi monitors, use
        # the em-size. This way sizings will be proportional to the font size,
        # which will create a more visually consistent size across platforms.
        em = w.theme.font_size

        # Widgets are laid out in layouts: gui.Horiz, gui.Vert,
        # gui.CollapsableVert, and gui.VGrid. By nesting the layouts we can
        # achieve complex designs. Usually we use a vertical layout as the
        # topmost widget, since widgets tend to be organized from top to bottom.
        # Within that, we usually have a series of horizontal layouts for each
        # row. All layouts take a spacing parameter, which is the spacing
        # between items in the widget, and a margins parameter, which specifies
        # the spacing of the left, top, right, bottom margins. (This acts like
        # the 'padding' property in CSS.)
        self._right_panel = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))

        # Create a collapsable vertical widget, which takes up enough vertical
        # space for all its children when open, but only enough for text when
        # closed. This is useful for property pages, so the user can hide sets
        # of properties they rarely use.
        view_ctrls = gui.CollapsableVert("View controls", 0.25 * em, gui.Margins(em, 0, 0, 0))

        self._show_axes = gui.Checkbox("Show axes")
        self._show_axes.checked = True
        self._show_axes.set_on_checked(self._on_show_axes)
        view_ctrls.add_child(self._show_axes)
        view_ctrls.set_is_open(False)

        self._right_panel.add_child(view_ctrls)

        self._left_panel = gui.Vert(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        info_horiz = gui.Horiz(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        info_horiz.add_child(gui.Label("Info:"))
        info_horiz.add_fixed(0.25 * em)
        self._info = gui.Label("")
        info_horiz.add_child(self._info)
        self._left_panel.add_child(info_horiz)

        view_objs = gui.CollapsableVert("Objects", 0.25 * em, gui.Margins(em, 0, 0, 0))
        self._objects_tree = gui.TreeView()
        view_objs.add_child(self._objects_tree)
        view_objs.set_is_open(False)
        self._left_panel.add_child(view_objs)

        self._bottom_panel = gui.Horiz(0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        self._bottom_panel.add_fixed(em * 0.5)
        self._bottom_panel.add_child(gui.Label("Scene:"))
        self._bottom_panel.add_fixed(em * 0.25)

        self._seq_idx_edit = gui.NumberEdit(gui.NumberEdit.INT)
        self._seq_idx_edit.set_limits(0, len(self) - 1)
        self._seq_idx_edit.set_on_value_changed(self._on_value_changed_seq_idx)
        self._bottom_panel.add_child(self._seq_idx_edit)
        self._bottom_panel.add_fixed(em * 0.5)

        self._seq_slider = gui.Slider(gui.Slider.INT)
        self._seq_slider.set_limits(0, len(self) - 1)
        self._seq_slider.set_on_value_changed(self._on_value_changed_seq_idx)
        self._bottom_panel.add_child(self._seq_slider)
        self._bottom_panel.add_fixed(em * 0.5)

        self._play = gui.Button("Play")
        self._play.vertical_padding_em = 0
        self._play.set_on_clicked(self._on_start_animation)
        self._bottom_panel.add_child(self._play)
        self._bottom_panel.add_fixed(em * 0.5)

        # Normally our user interface can be children of all one layout (usually
        # a vertical layout), which is then the only child of the window. In our
        # case we want the scene to take up all the space and the settings panel
        # to go above it. We can do this custom layout by providing an on_layout
        # callback. The on_layout callback should set the frame
        # (position + size) of every child correctly. After the callback is
        # done the window will layout the grandchildren.
        w.set_on_layout(self._on_layout)
        w.add_child(self._3d)
        w.add_child(self._right_panel)
        w.add_child(self._left_panel)
        w.add_child(self._bottom_panel)

    def _on_layout(self, layout_context):
        # The on_layout callback should set the frame (position + size) of every
        # child correctly. After the callback is done the window will layout
        # the grandchildren.
        r = self.window.content_rect
        self._3d.frame = r

        bp_height = int(1.75 * layout_context.theme.font_size)
        self._bottom_panel.frame = gui.Rect(0, r.get_bottom() - bp_height, r.get_right(), bp_height)

        width = 15 * layout_context.theme.font_size
        height = min(
            r.height - bp_height,
            self._right_panel.calc_preferred_size(layout_context, gui.Widget.Constraints()).height,
        )
        self._right_panel.frame = gui.Rect(r.get_right() - width, r.y, width, height)
        height = min(
            r.height - bp_height,
            self._left_panel.calc_preferred_size(layout_context, gui.Widget.Constraints()).height,
        )
        self._left_panel.frame = gui.Rect(0, r.y, width, height)

    def _on_show_axes(self, show):
        self._3d.scene.show_axes(show)
        self._3d.force_redraw()

    def _on_value_changed_seq_idx(self, new_value):
        new_value = min(len(self) - 1, max(0, new_value))
        new_value = int(new_value)
        self._seq_idx_edit.set_value(new_value)
        self._seq_slider.int_value = new_value
        if self.scene_idx != new_value:
            self.scene_idx = new_value
            self.show_scene()

    def _on_start_animation(self):
        def on_tick():
            return self._on_animate()

        self._last_animation_time = 0.0
        self._play.text = "Stop"
        self._play.set_on_clicked(self._on_stop_animation)
        self._is_playing = True
        self.window.set_on_tick_event(on_tick)

    def _on_animate(self):
        now = time.time()
        if now >= self._last_animation_time + self._animation_delay_secs:
            idx = (self._seq_slider.int_value + 1) % (len(self))
            idx = int(idx)
            self._seq_slider.int_value = idx
            self._on_value_changed_seq_idx(idx)
            self._last_animation_time = now
            return True
        return False

    def _on_stop_animation(self):
        self.window.set_on_tick_event(None)
        self._play.text = "Play"
        self._is_playing = False
        self._play.set_on_clicked(self._on_start_animation)

    def _on_key_3d(self, event):
        if event.type == gui.KeyEvent.DOWN:
            if event.key == gui.KeyName.R:
                self._setup_camera()
            elif event.key == gui.KeyName.SPACE:
                if self._is_playing:
                    self._on_stop_animation()
                else:
                    self._on_start_animation()
            elif event.key == gui.KeyName.RIGHT:
                self._on_value_changed_seq_idx(self.scene_idx + 1)
            elif event.key == gui.KeyName.LEFT:
                self._on_value_changed_seq_idx(self.scene_idx - 1)
            return gui.Widget.EventCallbackResult.HANDLED
        return gui.Widget.EventCallbackResult.IGNORED

    def _on_sun_dir(self, sun_dir):
        self._3d.scene.scene.set_sun_light(sun_dir, [1.0, 1.0, 1.0], 45000)

    def _get_material(self, geometry_type):
        if geometry_type == o3d.geometry.Geometry.TriangleMesh:
            material = rendering.MaterialRecord()
            material.base_color = [0.9, 0.9, 0.9, 1.0]
            material.shader = "defaultLit"
        elif geometry_type == o3d.geometry.Geometry.LineSet:
            material = rendering.MaterialRecord()
            material.base_color = [0.0, 0.0, 0.0, 1.0]
            material.shader = "unlitLine"
            material.line_width = 2
        elif geometry_type == o3d.geometry.Geometry.PointCloud:
            material = rendering.MaterialRecord()
            material.base_color = [0.9, 0.9, 0.9, 1.0]
            # material.base_color = [0.0, 0.0, 0.0, 1.0]
            material.shader = "defaultLit"
            material.point_size = 5
        else:
            material = rendering.MaterialRecord()
            material.base_color = [0.9, 0.9, 0.9, 1.0]
            material.shader = "defaultLit"

        return material

    def _setup_camera(self):
        if (
            self.scene_idx not in self.cached_scenes
            or self.cached_scenes[self.scene_idx] is None
            or len(self.cached_scenes[self.scene_idx]) == 1
        ):
            default_bounds = o3d.geometry.AxisAlignedBoundingBox([1, 1, 1], [-1, -1, -1])
            self._3d.setup_camera(60, default_bounds, default_bounds.get_center())
            # self._3d.scene.camera.look_at([0, 0, 0], [-2, 0, 0], [0, 0, 1])
        else:
            min_val = [1e30, 1e30, 1e30]
            max_val = [-1e30, -1e30, -1e30]
            for name in self.cached_scenes[self.scene_idx]:
                if name == "info":
                    continue
                max_bound = self.cached_scenes[self.scene_idx][name].get_max_bound()
                min_bound = self.cached_scenes[self.scene_idx][name].get_min_bound()
                for i in range(3):
                    max_val[i] = max(max_val[i], max_bound[i])
                    min_val[i] = min(min_val[i], min_bound[i])
            bounds = o3d.geometry.AxisAlignedBoundingBox(min_val, max_val)
            self._3d.setup_camera(60, bounds, bounds.get_center())

    def _make_on_checked(self, scene_idx, name):
        def on_checked(checked):
            self.selected_names[name] = checked
            glb_name = f"{scene_idx}_{name}"
            self._3d.scene.show_geometry(glb_name, checked)
            self._3d.force_redraw()

        return on_checked

    def to_mesh(self, verts, faces):
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(verts)
        mesh.triangles = o3d.utility.Vector3iVector(faces)
        mesh.compute_vertex_normals()
        return mesh

    def to_lineset(self, verts, faces):
        mesh = self.to_mesh(verts, faces)
        return o3d.geometry.LineSet.create_from_triangle_mesh(mesh)

    def to_point_cloud(self, points):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        return pcd

    def show_scene(self):
        if (self.scene_idx not in self.cached_scenes) or self.no_cache:
            if self.load_from_file:
                geometries = self.load_scene(self.scene_idx)  # key: geometry_name, value: geometry
            else:
                geometries = self.get_scene(self.scene_idx)  # key: geometry_name, value: geometry
            self.cached_scenes[self.scene_idx] = geometries

            if geometries is not None:
                if "info" not in geometries:
                    geometries["info"] = ""
                else:
                    if not isinstance(geometries["info"], str):
                        raise TypeError("info should be a str")
                for name in geometries:
                    if name == "info":
                        continue
                    glb_name = f"{self.scene_idx}_{name}"
                    material = self._get_material(geometries[name].get_geometry_type())
                    self._3d.scene.add_geometry(glb_name, geometries[name], material)

        self._objects_tree.clear()
        parent = self._objects_tree.get_root_item()
        if self.cached_scenes[self.scene_idx] is not None:
            for name in self.cached_scenes[self.scene_idx]:
                if name == "info":
                    continue
                if name not in self.selected_names:
                    self.selected_names[name] = True
                cell = gui.CheckableTextTreeCell(
                    name, self.selected_names[name], self._make_on_checked(self.scene_idx, name)
                )
                treeid = self._objects_tree.add_item(parent, cell)

        for scene_idx in self.cached_scenes:
            if self.cached_scenes[scene_idx] is not None:
                for name in self.cached_scenes[scene_idx]:
                    if name == "info" and (scene_idx == self.scene_idx):
                        text = self.cached_scenes[scene_idx][name]
                        self._info.text = text[:]
                        # We are sizing the info label to be exactly the right size,
                        # so since the text likely changed width, we need to
                        # re-layout to set the new frame.
                        self.window.set_needs_layout()
                        continue
                    glb_name = f"{scene_idx}_{name}"
                    if_show = (scene_idx == self.scene_idx) and self.selected_names[name]
                    self._3d.scene.show_geometry(glb_name, if_show)

        self._3d.force_redraw()

    def get_scene(self, scene_idx):
        raise NotImplementedError("Please implement this function if the vis data is not loaded from files")

    def load_scene(self, scene_idx):
        geometries = {}
        scene_dir = os.path.join(self.vis_dir, f"{scene_idx:05d}")
        if os.path.exists(scene_dir):
            subdirs = os.listdir(scene_dir)
            for subdir in subdirs:
                for filename in os.listdir(os.path.join(scene_dir, subdir)):
                    data_path = os.path.join(scene_dir, subdir, filename)
                    name = os.path.splitext(filename)[0]
                    if subdir == "point_cloud":
                        points = cvee.load(data_path)
                        geometries[name] = self.to_point_cloud(points)
                    elif subdir == "mesh":
                        verts, faces = cvee.load(data_path)
                        geometries[name] = self.to_mesh(verts, faces)
            return geometries
        else:
            return None

    def visualize(self, load_from_file=False, no_cache=False):
        self.scene_idx = int(0)

        self.load_from_file = load_from_file
        self.no_cache = no_cache

        self._last_animation_time = time.time()
        self._animation_delay_secs = 0.25
        self._is_playing = False

        if self.load_from_file:
            scene_dirs = os.listdir(self.vis_dir)
            for scene_dir in scene_dirs:
                if re.match("^[0-9]{5}$", scene_dir):
                    self.default_scene_num = max(int(scene_dir) + 1, self.default_scene_num)

        self.cached_scenes = {}
        self.selected_names = {}

        gui.Application.instance.initialize()
        self._init_ui()

        self.show_scene()

        self._setup_camera()
        self._3d.scene.show_axes(True)
        gui.Application.instance.run()

    def set_scene_idx(self, idx):
        self.scene_idx = int(idx)
        self.save_num = 0
        if self.vis_dir is None:
            raise RuntimeError("Please set vis_dir if you want to save data to files")
        os.makedirs(os.path.join(self.vis_dir, f"{self.scene_idx:05d}"), exist_ok=True)

    def get_output_path(self, type, name=None):
        if name is None:
            name = str(self.save_num)
            self.save_num += 1

        if self.vis_dir is None:
            raise RuntimeError("Please set vis_dir if you want to save data to files")
        output_path = os.path.join(self.vis_dir, f"{self.scene_idx:05d}", type, f"{name}.{file_exts[type]}")
        return output_path

    def save_mesh(self, verts, faces, name=None):
        output_path = self.get_output_path("mesh", name)

    def save_point_cloud(self, points, name=None):
        output_path = self.get_output_path("point_cloud", name)
        if isinstance(points, torch.Tensor):
            points = points.detach().cpu().numpy()
        if not (points.ndim == 2 and points.shape[1] == 3):
            raise RuntimeError("points wrong shape")
        cvee.save(output_path, points, auto_mkdirs=True)


def cli():
    parser = argparse.ArgumentParser(description="VisO3D")
    parser.add_argument("--vis_dir", type=str, default=".", help="Visualize directory.")
    args = parser.parse_args()

    vis = VisO3D(vis_dir=args.vis_dir)
    vis.visualize(load_from_file=True)
