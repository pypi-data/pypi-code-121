import imageio 
#import imp
import os,sys 
import click
import re
import random
from pathlib import Path
from . import encrypt as enpt
from io import StringIO
import subprocess
import shutil
from multiprocessing import Pool
from . import yxsfile
import time
from pypinyin import lazy_pinyin
import ffmpeg
from .video import video_operator

# import yxsfile
#给一个视频文件夹产生html网页

poster_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html" />
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>{title}</title>
<meta name="description" content="" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=0, minimum-scale=1.0, maximum-scale=1.0">

<link rel="stylesheet" type="text/css" href="builtin_kube.css" />
<link rel="stylesheet" type="text/css" href="builtin_style.css" />
    <style>

            .masonry2 {{ 
                column-count:4;
                column-gap: 1px;
                width: 100%;
                margin:1px auto;
            }}
            .item {{ 
                margin-bottom: 1px;
                min-height:200px;
            }}
            @media screen and (max-width: 1400px) {{ 
                .masonry2 {{ 
                    column-count: 3; // two columns on larger phones 
                }} 
            }} 

			@media screen and (max-width: 1000px) {{ 
                .masonry2 {{ 
                    column-count: 2; // two columns on larger phones 
                }} 
            }} 
            @media screen and (max-width: 600px) {{ 
                .masonry2 {{ 
                    column-count: 1; // two columns on larger phones 
                }} 
            }}

    </style>
<body  class="custom-background">
<div class="container">
  
    <div class="mainleft" id="mainleft">
   
              <ul id="post_container" class="masonry clearfix">
'''				
        
poster_html2 = '''	    	</ul>
        <div class="clear"></div><div class="last_page tips_info"></div>
        </div>
    </div>
    <!-- 下一页 -->
    <!-- <div class="navigation container"><div class='pagination'><a href='' class='current'>1</a><a href=''>2</a><a href=''>3</a><a href=''>4</a><a href=''>5</a><a href=''>6</a><a href="" class="next">下一页</a><a href='' class='extend' title='跳转到最后一页'>尾页</a></div></div> -->
<div class="clear"></div>
<script src="builtin_jquery.min.js"></script>
<script>
start();
$(window).on('scroll', function() {
start();
})

function start() {
//.not('[data-isLoaded]')选中已加载的图片不需要重新加载
$('.container img').not('[data-isLoaded]').each(function() {
var $node = $(this);
if (isShow($node)) {
loadImg($node);
}
})
}

//判断一个元素是不是出现在窗口(视野)
function isShow($node) {
return $node.offset().top <= $(window).height() + $(window).scrollTop();
}
//加载图片
function loadImg($img) {
//.attr(值)
//.attr(属性名称,值)
$img.attr('src', $img.attr('data-src')); //把data-src的值 赋值给src
$img.attr('data-isLoaded', 1); //已加载的图片做标记
}
</script>
</body></html>'''
poster_dir_name = 'generate_poster_dir'
user_poster_dir = 'user_poster_dir'
video_set = {'.mp4','.avi','.mkv','.flv','.mov','.ogg','.webm','.f4v','.mpxs'}
jpg_set = {'.jpxs','.jpg','.jpeg','.webp','.png'}
Pure_Name = re.compile('\.\[[^\]]+\]')
# html_lib_p = Path(__file__).parent / 'html_lib'
root_path = None
global_setting = {}

def sort_pinyin(a):
    t = [(lazy_pinyin(i)[0].lower(),i) for i in a]
    t.sort(key=lambda x:x[0])
    t = [i[1] for i in t]
    return t

def key_pinyin(a):
    return lazy_pinyin(a)[0].lower()

def relative_link(source,target):
    s1 = source.absolute().parts
    if target.is_dir():
        target = target / source.name
    if target.parent.is_symlink():
        target = target.parent.resolve() / target.name
    if target.is_file():
        print('file already exists!!',target)
        return
    t1 = target.absolute().parts
    diffp = 0
    for i,(a,b) in enumerate(zip(s1,t1)):
        if a != b:
            diffp = i 
            break 
    k = len(t1) - diffp
    if k>1:
        ff = Path('../'*(k-1)) / os.sep.join(s1[diffp:])
    else:
        ff = Path(s1[-1])
    try:
        target.symlink_to(ff)
    except Exception as e:
        print(target)
        print(ff)
        print(e)

def get_frame(vfile,ts):
    if vfile.suffix == '.mpxs':
        vfile_fp = open(vfile,'rb')
        vfile_fp.read(2048)
        vfile_format = 'mp4'
        t = imageio.read(vfile_fp,format=vfile_format)
    else:
        t = imageio.read(vfile)
    meta = t.get_meta_data()
    nn = t.count_frames()
    frame = t.get_data(min(int(ts * 60 * meta['fps']),int(nn/5)))

    return frame

def get_frame_out(vfile,ts,output):
    if vfile.suffix == '.mpxs':
        yf = yxsfile.yxsFile(vfile)
        mp4name = yf.to_pureFile()
        print("convert to pure file:",mp4name)
    else:
        mp4name = vfile
    probe = ffmpeg.probe(mp4name)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream:
        duration = float(video_stream['duration'])
        if ts>duration-60:
            ts = int(duration/2)
    try:
        (
            ffmpeg
            .input(str(mp4name), ss=ts)
            .output(str(output), vframes=1)
            .run(quiet=True,overwrite_output=True)
        )
    except Exception as e:
        print(e)
   
    if vfile.name != mp4name.name:
        os.remove(mp4name)
  
def time_check(dirname,dt=3600):
    if time.time() - Path(dirname).stat().st_mtime < dt or global_setting['force_update']:
        return True 
    else:
        return False

def convert_dir_files(pname,is_encrypt):

    for i in pname.glob('*'):
        xsfile = yxsfile.yxsFile(i)
        if is_encrypt:
            if xsfile.is_pureFile:
                xsfile.to_yxsFile()
                os.remove(i)
        else:
            if not xsfile.is_pureFile:
                xsfile.to_pureFile()
                os.remove(i)
def generate_poster(dirname,ts,shuffle,enable_yxsfile=False):
    if not time_check(dirname):
        return
    def is_renamed_jpg(jname):
        name = Pure_Name.sub('',jname.name)
        
        for jpg in jname.parent.glob('*.jpg'):
            j0 = Pure_Name.sub('',jpg.name )
            if j0 == name:
                print('rename: ',jpg,jname)
                os.rename(jpg,jname)
                return True
        return False
    p = Path(dirname)
    if p.name == user_poster_dir:
        convert_dir_files(p,enable_yxsfile)
        return
    if p.name == poster_dir_name:
        return
    # print('set poster',dirname)
    
    post_dir = p / poster_dir_name
    upost_dir= p / user_poster_dir
    is_first = False

    error_file = []

    for vfile in p.glob('*'):
        try:
            suffix = vfile.suffix.lower()
            if not vfile.is_file() or vfile.is_symlink():
                continue
            jpg_name = post_dir/vfile.with_suffix('.jpg').name
            jpxs_name = jpg_name.with_suffix('.jpxs')

            xsfile = yxsfile.yxsFile(vfile)
            if suffix in video_set and suffix != '.mpxs':
                # if is_renamed_jpg(jpg_name):
                #     continue
                
                if not jpg_name.is_file() and not jpxs_name.is_file():

                    if not is_first:                    
                        is_first = True
                        if not post_dir.is_dir():
                            os.mkdir(post_dir)
                    ujpg_name = upost_dir / jpg_name.name 
                    if ujpg_name.is_file():
                        relative_link(ujpg_name,jpg_name)
                    if not jpg_name.is_file():
                        print(vfile,ts)
                     
                        frame = get_frame_out(vfile,ts,jpg_name)
                      

                    if enable_yxsfile :
                        name_as_video = yxsfile.yxsFile(vfile).decode_filename().with_suffix('.jpg').name
                        name_as_video = jpg_name.parent / name_as_video
                        eyname = yxsfile.yxsFile(name_as_video).encode_filename()

                        ujpxs_name = upost_dir / eyname.name
                        if ujpxs_name.is_file():
                            relative_link(ujpxs_name,eyname)
                        if jpg_name.is_file():
                            if not eyname.is_file():
                                if not name_as_video.is_file():
                                    os.rename(jpg_name,name_as_video)
                                yxsfile.yxsFile(name_as_video).to_yxsFile()
                                os.remove(name_as_video)
                    
                        if jpg_name.is_file():
                            os.remove(jpg_name)
                if suffix not in ('.mp4','.mpxs'):
                    # convert video to mp4 format
                    video_operator.convert2mp4((vfile,),False,True,False)
                    mp4f = vfile.with_suffix('.mp4')
                    if mp4f.is_file() and mp4f.stat().st_size/vfile.stat().st_size > 0.8:
                        print('delete file',vfile)
                        os.remove(vfile)
                        suffix = '.mp4'
                        vfile = mp4f
                        xsfile = yxsfile.yxsFile(vfile)
                    else:
                        error_file.append(vfile)
                        continue
            if enable_yxsfile:
                #转换视频文件
                if suffix == '.mp4' or suffix == '.jpg' or suffix=='.webp':
                    print('convert file:',vfile)
                    t = xsfile.to_yxsFile()
                    os.remove(vfile)
                    print('delete',vfile)
                    vfile = t 

                if jpg_name.is_file():
                    jxsf = yxsfile.yxsFile(jpg_name)
                    t = jxsf.to_yxsFile()
                    os.remove(jpg_name)
                    print('delete',jpg_name)
                    continue 
                if jpxs_name.is_file():
                    continue
            else:
                #转换视频文件
                if suffix == '.mpxs' or suffix == '.jpxs':
                    t = xsfile.to_pureFile()
                    os.remove(vfile)
                    print('delete',vfile)
                    vfile = t

                if jpxs_name.is_file():
                    jxsf = yxsfile.yxsFile(jpxs_name)
                    t = jxsf.to_pureFile()
                    os.remove(jpxs_name)
                    print('delete',jpxs_name)
                    continue
                if jpg_name.is_file():
                    continue
        except Exception as e:
            print('error **************************************\n',vfile,'\n',e)
            continue
        
    # generate_index_html(dirname,shuffle)

def generate_index_html(dirname,shuffle=False,encrypt=False):
    p = Path(dirname).absolute()
    if not time_check(p):
        return
    if p.name == poster_dir_name or p.name == user_poster_dir:
        return

    content_html = '<li class="post box row fixed-hight"><div class="post_hover"><div class="thumbnail boxx"><a href="{infohtml}" class="zoom click_img" rel="bookmark" title="{videoname}"><img src="" data-src="{infojpg}" width="300" height="200" alt="{videoname}"/> </a></div><div class="article"><h2>  <a class="click_title" href="{infohtml}" rel="bookmark" title="{videoname}">{videoname}</a></h2></div></div></li>\n'	
    html_file = p / 'index.html'
    nd = len(html_file.parts) - len(root_path.parts) - 1

    fp = StringIO()
    fp.write(poster_html.format(title=p.name))
    exist_video = False
    video_list  = list(p.glob('*'))
    if shuffle:
        random.shuffle(video_list)
    else:
        video_list.sort(key = lambda x:key_pinyin(yxsfile.yxsFile(x.name).decode_filename().name))
    fimage = '<div class="item"><img src="" alt=" " data-src="{infojpg}"/></div>\n'	
    jpg_list = []
    dir_list = []
    for vfile in video_list:
        suffix = vfile.suffix.lower()
        if suffix in video_set:
            exist_video = True
            name = vfile.name
            stem = vfile.stem
            infojpg = f'./{poster_dir_name}/{stem}.jpg'
            user_poster = f'./{user_poster_dir}/{stem}.jpg'
            if (p/user_poster).is_file():
                infojpg = user_poster
            if vfile.suffix == '.mpxs':
                user_infojpg = Path(user_poster).with_suffix('.jpxs')
                if (p/user_infojpg).is_file():
                    infojpg = str(user_infojpg)
                else:
                    infojpg = str(Path(infojpg).with_suffix('.jpxs'))
            vstem = yxsfile.yxsFile(vfile).decode_filename().stem
            t = content_html.format(infohtml = name,videoname = vstem.replace('.fast',''),infojpg=infojpg)
            fp.write(t)
        elif suffix in jpg_set:
            jpg_list.append(vfile)
        elif vfile.is_dir() :
            dname = vfile.name 
            if not (dname.startswith('__') or dname.endswith('_dir')):
                dir_list.append(vfile)
    for dd in dir_list:
        exist_video = True
        dstem = yxsfile.yxsFile(dd).decode_filename().stem
        t = content_html.format(infohtml = dd.name,videoname = dstem,infojpg=f'{dd.name}/__poster_dir__.jpxs')
        fp.write(t)
    jpgid = [0,0]
    for fpath in jpg_list:
        if fpath.name.startswith('__'):
            continue
        exist_video = True
        jpgid[0] += 1
        if jpgid[0] % 8 == 1:
            ti = '<div class="masonry2">'
            if jpgid[1] == 1:
                ti = '</div>'+ti 
            jpgid[1] = 1
        else:
            ti = ''
        t = ti + fimage.format(infojpg=fpath.name)
        fp.write(t)
    if jpgid[1]>0:
        fp.write('</div>')
    if not exist_video:
        # fp.close()
        del fp
        # os.remove(html_file)
        return
    
    fp.write(poster_html2)
    
    fp.seek(0,0)
    ffp = open(html_file,'w')
    data = fp.read()
    if encrypt:
        b64data = enpt.b64encode(data.encode('utf-8'),passwd=enpt.get_default_passwd()).decode('utf-8')
        ffp.write('SP_ENCRYPT')
        ffp.write(b64data)
        ffp.close()
    else:
        ffp.write(data)
    ffp.close()

def delete_useless_link(dirname,delete_all_links=False):
    # 删除无用链接
    p = Path(dirname).absolute()
    if not time_check(p):
        return
    for vfile in p.glob('*'):
        if delete_all_links:
            try:
                is_link = vfile.is_symlink()
                if is_link:
                    vfile.unlink()
            except:
                vfile.unlink()
            continue
            
        if vfile.is_symlink() and (not vfile.exists()):
            print('remove link:',vfile)
            vfile.unlink()
def establish_link(dirname,roots,roots_videos):
    p = Path(dirname).absolute()
    add_new_dir = 0
    if not time_check(p):
        return add_new_dir
    if p.name == poster_dir_name:
        return add_new_dir
    post_dir = p / poster_dir_name
    is_first = True
    yxs_suffix = False
    ktags = [(i,i.lower().replace('-','').replace('_','')) for i in roots.keys()]
    for vfile in p.glob('*'):
        suffix = vfile.suffix.lower()
        try:
            is_link = vfile.is_symlink()
        except:
            is_link = False
        if suffix not in video_set or is_link:
            continue
        if is_first:
            is_first = False
            jpg_name = post_dir/vfile.with_suffix('.jpg').name
            if jpg_name.is_file():
                yxs_suffix = '.jpg' 
            else:
                yxs_suffix = '.jpxs'
        jpg_name = post_dir/vfile.with_suffix(yxs_suffix).name
        dname_stem = yxsfile.yxsFile(vfile).decode_filename().stem
        vstat = vfile.stat()
        vsize = vstat.st_size
        tags = ['ALL']
        if vsize<100000000:
            tags.append('ShortVideo')
        if vsize>4000000000:
            tags.append('HD')
        dname_stem_lower = dname_stem.lower().replace('-','').replace('_','')
        for i,ti in ktags:
            if dname_stem_lower.find(ti) != -1:
                tags.append(i)
        tags = set(tags)
        for t in tags:
            if t not in roots:
                dname = vfile.parent.parent / t
                os.makedirs(dname)
                os.makedirs(dname / poster_dir_name)
                roots[t] = dname
                print('make dir ',dname)
                add_new_dir += 1
            else:
                dname = roots[t]
            jpg_dir = dname / poster_dir_name
            if not jpg_dir.is_dir():
                os.makedirs(jpg_dir)
            videos = roots_videos.get(t)
            if not videos:
                videos = [i.name for i in dname.glob('*') if i.suffix in video_set]
                roots_videos[t] = videos
            if vfile.name not in videos:
                print('create link:',dname/vfile.name)
                # subprocess.call('ln -s "{}" "{}"'.format(vfile,dname/vfile.name),shell=True) 
                relative_link(vfile,dname/vfile.name)
                # subprocess.call('ln -s "{}" "{}"'.format(jpg_name,dname/poster_dir_name/jpg_name.name),shell=True) 
                relative_link(jpg_name,dname.resolve()/poster_dir_name/jpg_name.name)
                videos.append(vfile.name)
    return add_new_dir
def deal_with_subtitle(root,encrypt):
    p = Path(root).absolute()
    if not time_check(p):
        return
    suffixs = ('.ass','.srt')
    suffixs2 = ('.ass','.srt','.vtt')
    for i in p.glob('*'):
        if i.is_file() and i.suffix in suffixs:
            vtt_i = i.with_suffix('.vtt')
            if not vtt_i.is_file():
                os.system(f'ffmpeg -i "{i}" "{vtt_i}" -y')
            if encrypt:
                yxsfile.yxsFile(i).to_yxsFile()
                os.remove(i)
                if vtt_i.is_file():
                    yxsfile.yxsFile(vtt_i).to_yxsFile()
                    os.remove(vtt_i)
        if not encrypt:
            di = yxsfile.yxsFile(i).decode_filename()
            if di.suffix in suffixs2:
                yxsfile.yxsFile(i).to_pureFile()
                os.remove(i)
def generate_poster_all(dirname,time_interval,shuffle,delete_all_links,encrypt,no_links):

    for root,_,_ in os.walk(str(dirname),followlinks=True):
        generate_poster(root,time_interval,shuffle,encrypt)
        deal_with_subtitle(root,encrypt)
    run_del_link = True 
    if no_links:
        run_del_link = False 
    if delete_all_links:
        run_del_link = True
    if run_del_link:
        for root,_,_ in os.walk(str(dirname),followlinks=True):
            delete_useless_link(root,delete_all_links)
    deal_with_dirname(dirname,encrypt)
    roots = {yxsfile.yxsFile(root).decode_filename().name:Path(root).absolute() for root,_,_ in os.walk(str(dirname),followlinks=True)}
    roots.pop(Path(dirname).name)
    roots_videos = dict()
    add_new_dirs = 0
    run_link = True 
    if no_links or delete_all_links:
        run_link = False 
    if run_link:
        for root,_,_ in os.walk(str(dirname),followlinks=True):
            add_new_dirs += establish_link(root,roots,roots_videos)
    if add_new_dirs == 0 or not encrypt:
        for root,_,_ in os.walk(str(dirname),followlinks=True):
            if yxsfile.yxsFile(root).decode_filename().name == 'ALL':
                shuffle_t = False
            else: 
                shuffle_t = shuffle
            generate_index_html(root,shuffle_t,encrypt)
        # rootss = [root for root,_,_ in os.walk(str(dirname),followlinks=True)]
        # for root in reversed(rootss):
        #     pr = Path(root)
        #     mps = list(pr.glob('*.mpxs'))+list(pr.glob('*.mp4'))
        #     if not pr.name.endswith('_dir') and not mps:
        #         generate_root_index_html(root,encrypt)
        generate_root_index_html(dirname,encrypt)
    return add_new_dirs
def generate_root_index_html(dirname,encrypt):
    def useful_ablum(album):
        pa = yxsfile.yxsFile(album).decode_filename()
        name = pa.name
        if name.endswith('_dir') or (name.startswith('__') and name.endswith('__')):
            return False 
        else:
            return True
    p = Path(dirname)
    content_html = '<li class="post box row fixed-hight"><div class="post_hover"><div class="thumbnail boxx"><a href="{infohtml}/" class="zoom click_img" rel="bookmark" title="{videoname}"><img src="{infojpg}" data-src="{infojpg}" width="300" height="200" alt="{videoname}"/> </a></div><div class="article"><h2>  <a class="click_title" href="{infohtml}/" rel="bookmark" title="{videoname}">{videoname}</a></h2></div></div></li>\n'	
    html_file = p / 'index.html'
    nd = len(html_file.parts) - len(root_path.parts) - 1

    fp = StringIO()
    fp.write(poster_html.format(title=p.name ))
    albums = [(yxsfile.yxsFile(i).decode_filename().stem,i) for i in p.glob('*') if i.is_dir() and useful_ablum(i)]
    albums.sort(key = lambda x:key_pinyin(x[0]))
    puser = p/user_poster_dir
    if not puser.is_dir():
        os.makedirs(puser)
    njpg = len(list(puser.glob('*')))
    for alb in albums:
        name = yxsfile.yxsFile(alb[1]).decode_filename().name
        real_name = alb[1].name

        user_cover = alb[1] / user_poster_dir / 'cover.jpg'
        infojpg = ''
        if user_cover.is_file():
            infojpg = f'{real_name}/{user_poster_dir}/cover.jpg'
        if not infojpg:
            k = alb[1] / user_poster_dir
            l = alb[1] / poster_dir_name
            jpgs = list(k.glob('*')) + list(l.glob('*')) + list(alb[1].glob('*.jpg')) +list(alb[1].glob('*.jpxs')) 
            if jpgs:
                mt = jpgs[0]
                infojpg = str(Path( mt.parent.parent.name)/mt.parent.name / mt.name)
        if njpg == 0 and jpgs:
            njpg = 1
            shutil.copy(jpgs[0],puser/Path(infojpg).name)
        t = content_html.format(infohtml = real_name,videoname = name,infojpg=infojpg)
        fp.write(t)
    fp.write(poster_html2)
    fp.seek(0,0)
    data = fp.read()
    ffp = open(html_file,'w')
    if encrypt:
        b64data = enpt.b64encode(data.encode('utf-8'),passwd=enpt.get_default_passwd()).decode('utf-8')
        ffp.write('SP_ENCRYPT')
        ffp.write(b64data)
        ffp.close()
    else:
        ffp.write(data)
    ffp.close()

def deal_with_dirname(dirname,endir):

    roots = [root for root,_,_ in os.walk(str(dirname),followlinks=True)][1:]
    for root in reversed(roots):
        i = Path(root)
        if i.is_dir() and not i.name.endswith('_dir'):
            xdir = yxsfile.yxsFile(i)
            if endir:
                xname = xdir.encode_filename()
            else: 
                xname = xdir.decode_filename()
            if xname.name != i.name:
                os.rename(i,xname)
@click.command()
@click.argument('dirname')
@click.option('--time_interval','-t',default=15.0,help="视频截图时间戳")
@click.option('--shuffle',           default=False,help="打乱文件顺序",is_flag=True)
@click.option('--update',       '-u',default=False,help="强制更新",is_flag=True)
@click.option('--delete_all_links',  default=False,help="删除所有link文件",is_flag=True)
@click.option('--no_links',          default=False,help="不建立link",is_flag=True)
@click.option('--fix_ffmpeg',   '-f',default=False,help="修复ffmpeg问题",is_flag=True)
@click.option('--no_encrypt',        default=False,help="加密文件",is_flag=True)
@click.option('--endir',             default=False,is_flag=True,help="加密文件夹名")
@click.option('--dedir',             default=False,is_flag=True,help="解密文件夹名")
def main(dirname,time_interval,shuffle=False,delete_all_links=False,no_encrypt=False,endir=False,dedir=False,fix_ffmpeg=True,no_links=False,update=False):
    global_setting['fix_ffmpeg'] = fix_ffmpeg
    global_setting['force_update'] = update
    global root_path 
    root_path = Path(dirname).absolute()
    # generate_root_index_html(Path(dirname).absolute(),True)
    # return
    if dirname:
        if endir or dedir:
            deal_with_dirname(dirname,endir)
        else:
            encrypt = not no_encrypt
            if encrypt:
                for root,ds,fs in os.walk(str(dirname),followlinks=True):
                    for fname in ds+fs:
                        if fname.endswith('._tt'):
                            raise Exception(f'wrong name "{fname}" in {root} !')
            add_new_dirs = generate_poster_all(dirname,time_interval,shuffle,delete_all_links,encrypt,no_links)
            if add_new_dirs != 0 and encrypt:
                generate_poster_all(dirname,time_interval,shuffle,delete_all_links,encrypt,no_links)
if __name__=='__main__':
    main(None,None)
