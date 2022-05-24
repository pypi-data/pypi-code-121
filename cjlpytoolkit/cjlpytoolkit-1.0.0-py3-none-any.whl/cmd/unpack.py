import os
import re
import argparse
from datetime import datetime

__CONTEXT__ = os.getcwd()

__ICONS__ = 'icons'

__RES__ = [
    'C://LinkedProjects/phnix-plus/lib_resource/src/main/res',  # 芬尼APP
    'C://LinkedProjects/linked-go/lib_base/src/main/res',  # 零狗APP
    'C://LinkedProjects/control-screen/app/src/main/res'  # 十寸屏
]


def get_params():
    desc = 'This command is used to extract and classify image resources into corresponding project files'
    parser = argparse.ArgumentParser(prog='unpack', description=desc)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p',
                       '--phnix',
                       action='store_const',
                       const=True,
                       help='phnix project')
    group.add_argument('-l',
                       '--linked',
                       action='store_const',
                       const=True,
                       help='linkedgo project')
    group.add_argument('-c',
                       '--control',
                       action='store_const',
                       const=True,
                       help='control screen project')
    parser.add_argument('file',
                        type=str,
                        help='icon resource compressed file(.zip)')
    parser.add_argument('-d',
                        '--dir',
                        type=str,
                        help='destination folder',
                        metavar='dir')

    args = parser.parse_args()

    if not args.file.endswith('.zip'):
        print('Illegal file, please enter (.zip) compressed file')
        return None
    if args.phnix:  # 芬尼APP
        return 0, args.file, args.dir
    elif args.linked:  # 零狗APP
        return 1, args.file, args.dir
    elif args.control:  # 十寸屏
        return 2, args.file, args.dir
    else:
        return None


def unpack_icons():
    param = get_params()
    if param is None:
        return
    start = datetime.now()
    print(f"start at {start.strftime('%Y-%m-%d %H:%M:%S')}")
    index, zip_file, direct_dir = param
    if direct_dir is None:
        direct_dir = __RES__[index]
    direct_dir = os.path.abspath(direct_dir)
    if not os.path.exists(direct_dir):
        os.makedirs(direct_dir)
    if os.path.exists(__ICONS__):
        os.system(f'rm -rf {__ICONS__}')
    os.system(f"unzip {zip_file} -d {__ICONS__}")
    mipmaps = os.listdir(__ICONS__)
    os.chdir(__ICONS__)
    for mipmap in mipmaps:
        direct_mipmap = os.path.join(direct_dir, mipmap)
        if not os.path.exists(direct_mipmap):
            os.makedirs(direct_mipmap)
        print(f'{mipmap}: ', end='\n')
        for icon in os.listdir(mipmap):
            if re.match(r'.*-.*|.*\s.*', icon):  # 查找图片名字是否含有空格或横杆
                new_icon = re.sub(r'-+|\s+', '_', icon)  # 替换空格和横杆为下划线
                cmd = f"mv '{mipmap}/{icon}' '{mipmap}/{new_icon}'"
                os.system(cmd)
                print(cmd)
                icon = new_icon
            cmd = f'cp {mipmap}/{icon} {direct_mipmap}'
            os.system(cmd)
            print(cmd)
        print('\n')
    stop = datetime.now()
    sec = stop.timestamp() - start.timestamp()
    print(f"stop at {stop.strftime('%Y-%m-%d %H:%M:%S')}, use time = {sec:.3f}s")
