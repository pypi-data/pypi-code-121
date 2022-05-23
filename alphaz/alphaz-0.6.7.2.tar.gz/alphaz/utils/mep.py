from .libs import config_lib

def launch_cmds_web(cmds,base_href):
    if len(cmds) == 0:
        return
    root    = '/home/truegolliath/svntools/GolliathPublic/front/GolliathApp/'
    os.chdir(root)
    source, target  = 'dist/GolliathApp/', '/var/www/html/'
    print('Launching %s'%' '.join(cmds))
    cmd = ' '.join(cmds)
    os.system(cmd)
    if base_href != '':
        print('Copy from %s to %s'%(source, target + base_href))
        copy_files(source,target + base_href,[],action=not args.test)  
    os.chdir(current_folder) 

def send_files(ftp,target, source, folder_list,root_ftp=''):
    path_from       = target + os.sep + os.sep.join(folder_list)
    print(target, source, folder_list, root_ftp,path_from)

    path_to     = source + os.sep + root_ftp + os.sep + os.sep.join(folder_list)
    ftp.makedirs(path_to)

    files           = glob.glob(path_from + os.sep + '*')

    to_upload = []
    for file in files:
        filename    = file.replace(path_from,'')[1:]        
        filepath    = file.replace(path_from,path_to)

        if os.path.isfile(file):
            ext         = file.split('.')[1] if len(file.split('.')) > 1 else ''
            #print('         ext',ext)
            if not ext in EXTS_EXLCUDES:
                to_upload.append({'sourcepath':file,'remotepath':filepath})
        else:
            if not filename in DIR_EXCLUDES:
                new_folders = copy.copy(folder_list)
                new_folders.append(filename)
                send_files(ftp,target, source, new_folders,root_ftp=root_ftp)

    ftp.uploads(to_upload)

def upload(target, source, folder_list, root_ftp=''):
    ftp         = common.GolliathFtp(
        host=core.config.get('ftp/public/host'),
        port=core.config.get('ftp/public/port'),
        user=core.config.get('ftp/public/user')
        key =core.config.get('ftp/public/key')
    )
    send_files(ftp,target, source, folder_list,root_ftp=root_ftp)

def mep_web(configuration,base_href=''):
    cmds = ['npm','run','ng-medium-memory','--','build']
    cmds.append('--prod')
    if base_href != '': 
        cmds.append('--base-href=/%s/'%base_href)

    if configuration is not None and configuration != 'normal':
        cmds.append('--configuration=%s'%configuration)

    launch_cmds_web(cmds,base_href)

def get_zips(base):
    ty          = root_backup + base + '*.zip'
    zips        = [x for x in glob.glob(ty) if os.path.isfile(x)]
    zips_times  = {}
    for zip_file in zips:
        zips_times[zip_file]    = os.path.getmtime(zip_file)
    zips_times  = {k: v for k, v in sorted(zips_times.items(), key=lambda item: item[1],reverse=True)}
    return zips_times

def mep(config_name,restore=False,action=True):
    folders = folders_configs[config_name]

    for folder_list in folders:
        source,target = root_dev, root_prod 

        folder_path = os.sep.join(folder_list).replace(os.sep,'-')
        date_str    = str(datetime.datetime.now()).replace(' ','-').split('.')[0]

        base        = '%s_%s_'%(config_name,folder_path)
        zip_name    = '%s%s.zip'%(base,date_str)
        zips_times  = get_zips(base)

        source_path = os.sep.join(folder_list)
        
        if not restore:
            cmd                 = "zip -r %s %s"%(root_backup + zip_name, source_path)
            current_folder      = os.getcwd()
            os.chdir(root_prod)
            infos = copy_files(source,target,folder_list,action=False,infos={})

            if infos['nb'] != 0:
                answer = input('Move files ? [Y/N]')
                if 'Y' in answer.upper():
                    print('zip %s to %s'%(source_path,root_backup + zip_name))
                    get_output(os.system,[cmd],{})
                    print('\n')
                    copy_files(source,target,folder_list,action=action)
            else:
                print('   {:40} Nothing to update ...'.format(folder_path))

            os.chdir(current_folder)
        else:
            backup_zip_file     = list(zips_times.keys())[0]
            unzip_repository    = root_prod
            cmd                 = 'unzip -o -d %s %s'%(unzip_repository,backup_zip_file)
            os.system(cmd)
        
        if config_name == 'api':
            upload(target,Core.WEB_API_PATH,folder_list,root_ftp='')

    if config_name == 'api':
        config_lib.upgrade_api_build(DB,Constants,CoreW)
        restart_api()