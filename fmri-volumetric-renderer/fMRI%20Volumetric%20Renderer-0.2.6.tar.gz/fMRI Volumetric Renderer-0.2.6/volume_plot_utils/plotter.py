import ipywidgets as widgets
from string import Template
from importlib import resources
import io

def displayVolume(vol, brightness=1, threshold=1, theta=0, phi=0, radius=False, origin=False, fps=1) :
  #expects tensor data in shape [frames, height, depth, width] with an integer range 0-255
  if not origin : origin = [vol.shape[3]/2,vol.shape[2]/2,vol.shape[1]/2]
  if not radius : radius = vol.shape[1]
  htmlStats = {"INSERT_VOLUME_WIDTH_HERE":vol.shape[3],
             "INSERT_VOLUME_DEPTH_HERE":vol.shape[2],
             "INSERT_VOLUME_HEIGHT_HERE":vol.shape[1],
             "INSERT_FRAME_COUNT_HERE":vol.shape[0],
             "INSERT_FPS_HERE":fps,
             "INSERT_BRIGHTNESS_HERE":brightness,
             "INSERT_THRESHOLD_HERE":threshold,
             "INSERT_RADIUS_HERE":radius,
             "INSERT_THETA_HERE":theta,
             "INSERT_PHI_HERE":phi,
             "INSERT_ORIGIN_HERE":origin,
             "INSERT_FRAMES_HERE": f"[{','.join(map(str,map(int,(255.0*vol.flatten()/vol.max().item()).round().tolist())))}]" }

  htmlTemplate = resources.read_text("volume_plot_utils", "template.html.txt")

  htmlTxt = Template(htmlTemplate).safe_substitute(htmlStats)
  html = widgets.HTML(value=htmlTxt, placeholder="error renderer widget not loaded", description="renderer widget")
  html.layout.min_height = "500px"

  display(html)
  
  
  
  
  
  
  
