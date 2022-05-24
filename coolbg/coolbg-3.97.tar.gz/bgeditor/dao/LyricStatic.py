import time

import requests, os, uuid
from bgeditor.common.utils import cache_file, download_file, upload_file, upload_static_file, get_dir
from moviepy.editor import *
from PIL import Image


def create_lyric_static(arr_comp, mix_data, font_url, lyric_lines=2):
    path_img = os.path.join(get_dir('coolbg_ffmpeg'), str(uuid.uuid4()) + "-comp-static-img.png")
    CompositeVideoClip(arr_comp).save_frame(path_img, 0)
    im = Image.open(path_img)
    rgb_im = im.convert('RGB')
    ejpg = path_img.replace(".png", ".jpg")
    rgb_im.save(ejpg)
    im.close()
    rgb_im.close()
    rs_static_img = upload_static_file(ejpg)
    arr_lyric_video_id=[]
    if "success" in rs_static_img and rs_static_img['success'] == 1:
        mix_data.pop(0)
        for item in mix_data:
            data = {}
            data['audio_url'] = item['audio_url']
            data['lyric_sync'] = item['lyric_sync']
            data['group_number'] = lyric_lines
            data['bg_image'] = rs_static_img['url']
            data['artist_name'] = item['artist_name']
            data['song_name'] = item['song_name']
            data['font_url'] = font_url
            obj = requests.post("http://api-magicframe.automusic.win/static-lyric/add", json=data).json()
            if "id" in obj:
                arr_lyric_video_id.append(obj['id'])
    return arr_lyric_video_id


def load_lyric_video(arr_id, wait_time=10*60):
    util_time=time.time()+wait_time
    arr_video_path=[]
    arr_id_downloaded=[]
    while time.time() < util_time and len(arr_video_path) < len(arr_id):
        for idx in arr_id:
            if idx not in arr_id_downloaded:
                try:
                    obj = requests.get(f"http://api-magicframe.automusic.win/static-lyric/load/{idx}").json()
                    if "id" in obj and int(obj['status']) == 3:
                        arr_id_downloaded.append(idx)
                        path_video=download_file(obj['result'])
                        arr_video_path.append(path_video)
                        if len(arr_video_path) == len(arr_id):
                            break
                except:
                    pass
        time.sleep(10)
    return arr_video_path