import numpy as np
from napari.utils.events import EventedModel
from napari.viewer import current_viewer
from scipy.spatial.transform import Rotation as R
from superqt.utils import ensure_main_thread

from . import _spacemouse as sm


class Config(EventedModel):
    roll_active: bool = True
    pitch_active: bool = True
    yaw_active: bool = True
    zoom_active: bool = True
    x_active: bool = True
    z_active: bool = True
    gain_roll: float = 2
    gain_zoom: float = 2
    gain_pitch: float = 2
    gain_yaw: float = 2
    gain_x: float = 4
    gain_z: float = 4
    max_zoom = 60
    min_zoom = 0.01
    max_perspective = 90


CFG = Config()


@ensure_main_thread
def _handle_buttons(s: sm.MouseState, v=None):
    if not (v := v or current_viewer()):
        return

    # both buttons resets the viewer
    if all(s.buttons):
        v.reset_view()
    elif s.buttons[0]:
        v.dims.ndisplay = 2 if v.dims.ndisplay == 3 else 3


last_step = [0.0]


def _apply_state_to_viewer(s: sm.MouseState, v=None):

    if not (v := v or current_viewer()):
        return

    # lower-case is extrinsic, uppercase is intrinsic
    dpitch = CFG.gain_pitch * (s.pitch if CFG.pitch_active else 0)
    droll = CFG.gain_roll * (s.roll if CFG.roll_active else 0)
    dyaw = CFG.gain_yaw * (s.yaw if CFG.yaw_active else 0)
    dz = CFG.gain_z * (s.z if CFG.z_active else 0)
    dx = CFG.gain_x * (s.x if CFG.x_active else 0)
    dy = CFG.gain_zoom * (s.y if CFG.zoom_active else 0)

    # if the right button is pressed, the Y axis controls perspective
    if s.buttons[1]:
        perspective = v.camera.perspective + s.y
        v.camera.perspective = max(0, min(perspective, CFG.max_perspective))
        return

    if v.dims.ndisplay == 2:
        # if we're twisting, only change dims
        twisting_threshold = 0.01
        if np.abs(s.yaw) > twisting_threshold:
            # TODO: this could feel a bit better
            # trying to scale the frame rate based on how hard they're twisting
            elapsed = s.t - last_step[0]
            threshold = 0.2 / -np.log(1.0001 - np.abs(s.yaw))
            if elapsed > threshold:
                axis = v.dims.last_used
                v.dims.set_current_step(
                    axis, v.dims.current_step[axis] + np.sign(s.yaw)
                )
                last_step[0] = s.t
            return
        # otherwise pan
        v.camera.center = np.array(v.camera.center) - (0, -dz, dx)
    elif v.dims.ndisplay == 3:
        # determine camera rotation
        cam = R.from_euler("yzx", v.camera.angles, True)
        rot = R.from_euler("xyz", (-dpitch, droll, -dyaw), True)
        new_cam = cam * rot.inv()
        v.camera.angles = new_cam.as_euler("yzx", True)
        # determine camera centration
        # first apply the camera transform to the translation vector
        delta = new_cam.apply((-dx, 0, -dz))[::-1]
        v.camera.center = np.array(v.camera.center) + delta

    # adjust zoom
    if dy:
        # (zoom included in subtrahend to reduce speed as zoom decreases)
        zoom = v.camera.zoom - v.camera.zoom * dy / 80
        v.camera.zoom = max(min(zoom, CFG.max_zoom), CFG.min_zoom)


# troubleshoot
# start with (0,0,0) -> (Y+clockwise, Z+clockwise, X+clockwise) -< Left-handed rot.
# rotate each axis, evaluate what it moves in the image.

# right-handed rotation, rotating counter-clockwise when looking at zero from positive

# tilt away from me -> pitch goes up
# rotate (doorknob) clockwise -> yaw goes up
# tilt right -> roll goes up

# napari has right-handed coordinate system (assuming pointer finger is X)
