
from moviepy.editor import *
from Component import Component

def create_image(list_comp_data,path_img, t=0):
    arr_comps = []
    for comp_data in list_comp_data:
        comp_data["job_id"] = 1
        comp_data["mf_server"] = "http://api-magicframe.automusic.win/"
        if comp_data['type'] == "compilation" or comp_data['type'] == "lyric" :
            continue
        arr_comps.append(Component.convert(comp_data).make())
    CompositeVideoClip(arr_comps).save_frame(path_img, t)
    return path_img
