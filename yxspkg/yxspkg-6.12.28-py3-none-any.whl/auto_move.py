from email.policy import default
import time,os,sys
import subprocess
from pathlib import Path
import click
import ftplib
import threading
from rich.progress import track

global_info = [0,0]
global_setting = {'rsync_type':'rsync','ftp_server':None}
def makedirs_ftp(ftp_server,dirs):
    rr = []
    for _ in range(10):
        try:
            ftp_server.cwd(str(dirs))
            break 
        except Exception as e:
            rr.append(str(dirs))
            dirs = dirs.parent
    rr.reverse()
    for i in rr:
        ftp_server.mkd(i)
def get_ftp_server(username,host,password):
   
    ftp_server = global_setting['ftp_server']
    try:
        ftp_server.pwd()
    except:
        ftp_server = ftplib.FTP()
        ftp_server.encoding = 'utf-8'
        ftp_server.connect(host)
        ftp_server.login(username,password)
        global_setting['ftp_server'] = ftp_server
    return global_setting['ftp_server'] 
def rsync_file(filename,target_file,username,ip):
    if global_setting['rsync_type'] == 'rsync':
        cmd = f'rsync --protect-args -avPh "{filename}" "{username}@{ip}:{target_file}"'
        print("##",cmd)
        a = subprocess.call(cmd,shell=True)
        if a != 0:
            rsync_dir(global_info[0],global_info[1],username,ip)
            print("##",cmd)
            a = subprocess.call(cmd,shell=True) 
        return a
    elif global_setting['rsync_type'] == 'ftp':
        ftp_server = get_ftp_server(username,ip,global_setting['password'])
        tpath = Path(target_file)
        tdir = tpath.parent
        try:
            ftp_server.cwd(str(tdir))
        except:
            makedirs_ftp(ftp_server,tdir)
            ftp_server.cwd(str(tdir))
        def process_bar(buf):
            try:
                next(pp_bar)
            except:
                pass
        bufsize = 1024*1024
        fp = open(filename,'rb')
        tname = tpath.name
        try:
            size = Path(filename).stat().st_size 
            nn = max(1,int(size/bufsize))
            mb = size/(1024*1024)
            if mb > 1024:
                mb = f'{mb/1024:.2f}GB'
            else:
                mb = f'{mb:.2f}MB'
            pp_bar = track(range(nn),description=f'Upload({mb}):')
            # help(ftp_server.storbinary)
            a = ftp_server.storbinary(f'STOR {tname}',fp,blocksize=bufsize,callback=process_bar)
            result = 0
        except Exception as e:
            print(e)
            result = -1

        while True:
            try:
                next(pp_bar)
            except:
                break 
        
        fp.close()
        ftp_server.quit()

        return result


def rsync_dir(dirname,target_dir,username,ip):
    cmd = f'rsync --protect-args -av --include="*/" --exclude="*" "{dirname}"  "{username}@{ip}:{target_dir}"'
    print("##",cmd)
    return subprocess.call(cmd,shell=True)


def auto_move(dirname,target_dir,username,ip,temp_suffix=['.js','.tail'],interval=600):
    info = dict()
    pdir = Path(target_dir)
    length_dirname = len(dirname)
    if dirname[-1] == '/':
        length_dirname -= 1
        dirname = dirname[:-1]

    global_info[0] = dirname+'/'
    if target_dir[-1] != '/':
        target_dir += '/'
    global_info[1] = target_dir
    wait_max = min(interval*5,300)
    rr=False
    resolve = str(Path(dirname).resolve().absolute())
    
    wait_start = time.time()

    min_size = global_setting['min_size']

    def update_info():
        while True:
            tt = time.time()
            for root,ds,fs in os.walk(dirname):
                pr = Path(root)
                for i in fs:
                    if not global_setting['hidden']:
                        if i[0] == '.':
                            continue
                    suffix = Path(i).suffix
                    if suffix in temp_suffix:
                        continue
                    iname = i 
                    fname = pr/iname
                    size = fname.stat().st_size
                    sname = str(fname)

                    if sname in info:
                        info[sname]['size_old'] = info[sname]['size']
                        info[sname]['size'] = size 
                        info[sname]['time'] = tt
                        if size != info[sname]['size_old']:
                            info[sname]['time_old'] = tt
                    else:
                        info[sname] = {'size':size,'time':tt,'time_old':tt,'size_old':size,'create_time':tt}
            if global_setting['delete']:
                fsize = get_volume(resolve)
                if fsize/1e9 < min_size:
                    print('剩余空间过小：',fsize/1e9)
                    delete_small_file(info,min_size - fsize/1e9,temp_suffix)

            sys.stdout.flush()
            time.sleep(interval)
    update_thread = threading.Thread(target=update_info)
    update_thread.start()
    time.sleep(2)
    while True:
        tt = time.time()
        for filename in list(info.keys()):
            if temp_suffix:
                temp_exist = False 
                for its in temp_suffix:
                    temp_file = Path(filename+its)
                    t2 = temp_file.with_name('.'+temp_file.name)
                    if temp_file.is_file() or t2.is_file():
                        temp_exist = True
                        break
                if temp_exist:
                    continue
                pf = Path(filename)
                df = info[filename]
                if df['size']>1:
                    if not pf.is_file():
                        info.pop(filename)
                        continue
                else:
                    info.pop(filename)
                    continue

                if pf.is_file() and pf.stat().st_size>1 and tt-df['time_old']>wait_max and df['size']==df['size_old']:
                    print('\nmove file:',filename)
                    pure_name = filename[length_dirname+1:]
                    tfname = pdir/pure_name
                    a = rsync_file(filename,tfname,username,ip)
                    if a==0:
                        print('received file:',filename)
                        fp = open(filename,'w')
                        fp.close()
                    else:
                        print('rsync file error')
                    wait_start = time.time()
            else:
                raise Exception('temp_suffix error')
        wait_span = int(time.time() - wait_start )
        if wait_span>3600:
            waits = f'{wait_span/3600:.2f}h    '
        elif wait_span>60:
            waits = f'{wait_span/60:.2f}m   '
        else:
            waits = f'{int(wait_span)}s    '
        print(f'wait: {waits}    \r',end='')

        sys.stdout.flush()
        time.sleep(interval)
        if Path('stop').is_file():
            rr = True 
            break
    update_thread.join()
    return rr
def delete_small_file(info,total,temp_suffix):
    rr = []
    min_size = global_setting['min_size']
    for filename in list(info.keys()):
        p = Path(filename)
        if p.is_file():
            ifd = info[filename]
            psize = p.stat().st_size
            if p.is_file() and psize/1e6>100:
                # 记录大于100MB的文件
                rr.append((p,psize,ifd['time'] - ifd['time_old'],ifd['create_time']))

    rmt = [i for i in rr if i[2]>3600]
    for pf,psize,dtime,create_time in rmt:
        if not pf.is_file():
            continue
        temp_exist = False 
        for its in temp_suffix:
            temp_file = pf.with_name(pf.name+its)
            t2 = temp_file.with_name('.'+temp_file.name)
            if temp_file.is_file() or t2.is_file():
                temp_exist = True

        if not temp_exist:
            continue

        print(f'删除:{pf},{psize/1e9:5.2f}GB,{dtime/3600:5.1f}h')
        open(pf,'wb').close()
        time.sleep(5)
        os.remove(pf)
        break
def get_volume(fname):
    t = subprocess.getoutput('df ')
    rr = list()
    for i in t.split('\n'):
        m = i.split()
        if fname.startswith(m[-1]):
            rr.append(m)
    rr.sort(key=lambda x:len(x[-1]))

    size = rr[-1][3]
    d = {'T':1e12,'G':1e9,'M':1e6,'K':1e3}
    if size[-1] in d:
        p = float(size[:-1]) * d[size[-1]]
    else:
        p = float(size)*1e3
    return p
@click.command()
@click.option('--input_dir','-i',help='输入文件夹名称')
@click.option('--output_dir','-o',help='输出文件夹名称')
@click.option('--username','-u',default='',help='用户名')
@click.option('--host','-h',default='',help='节点')
@click.option('--suffix_temp','-s',default='.js,.tail',help='临时文件后缀')
@click.option('--time_wait','-t',default=600,help='时间间隔')
@click.option('--password','-p',default='',help='ftp所用密码')
@click.option('--delete','-d',default=False,help='剩余空间小于1G时自动删除小文件',is_flag=True)
@click.option('--ftp',default=False,help='是否使用ftp',is_flag=True)
@click.option('--min_size',default=1.2,help='磁盘最小保留空间（GB）')
@click.option('--hidden',default=False,help='统计隐藏文件',is_flag=True)
def main(input_dir,output_dir,username,host,suffix_temp,time_wait,password,ftp,delete,min_size,hidden):
    global_setting['password'] = password
    global_setting['min_size'] = min_size
    global_setting['hidden'] = hidden
    temp_suffix = suffix_temp
    if Path('stop').is_file():
        os.remove('stop')
    if temp_suffix.find(',') != -1:
        temp_suffix = [i.strip() for i in temp_suffix.split(',')]
    else:
        temp_suffix = temp_suffix.split()
    ipos = output_dir.find('@')

    if ipos !=-1:
        username = output_dir[:ipos]
        host,output_dir = output_dir[ipos+1:].split(':')
    used_ftp = False
    global_setting['delete'] = delete
    if ftp:
        global_setting['rsync_type'] = 'ftp'
        used_ftp = True 
    print(f'in: {input_dir}\nout: {output_dir}\nusername: {username}\nhost: {host}\ntime_wait: {time_wait}\nsuffix_temp: {temp_suffix}\nftp:  {used_ftp}')
    print(f'delete: {delete}\nmin_size: {min_size}\n')
    while True:
        try:
            a = auto_move(input_dir,output_dir,username,host,temp_suffix,time_wait)
            if a:
                break 
        except Exception as e:
            print(e)
if __name__=='__main__':
    main()