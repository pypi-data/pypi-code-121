
#TODO: Make a static folder in RP which is for pip imports, with a list of pip versions to module name translations for every package. That folder is baked internally, and doesn't affect the rest of rp (to make refactoring less dangerous). Also, make this baker add these new files (or get rid of old files) from setup.py 
#Oven.py bakes modules into directories
from rp import *
def bake(this_module_name:str,module_names:str):
    module_names=module_names.split()
    if not input_yes_no('Warning: This function might change every python file in this directory recursively. Is this ok?'):
        return
    #You shouldn't modify anything in the baked modules folder, because they might be overridden later by this function if rebaked
    current_directory=get_current_directory()
    #this_module_name=get_folder_name(current_directory)
    baked_folder_name='baked' # This is where all the baked modules go
    baked_folder_path=path_join(current_directory,baked_folder_name)
    print('Destination directory: '+repr(baked_folder_path))
    
    #Initialize or re-initialize the baked folder such that it's empty
    if folder_exists(baked_folder_path):
        #Always start fresh with a new baked folder. However, don't delete the old one.
        #Instead, just create a backup copy.
        old_baked_folder_name='old_'+baked_folder_name+'_'+str(get_current_date())
        rename_directory(baked_folder_path,path_join('..',old_baked_folder_name))
    assert not folder_exists(baked_folder_path),'This is an internal assertion and should never fail'
    make_folder(baked_folder_path)
    
    #Copy all the modules to the baked folder
    for module_name in module_names:
        module_path=get_module_path_from_name(module_name)
        if module_path.endswith('__init__.py'):
            #If the module root is a folder, it will be in a folder called  '__init__.py' 
            #However, we just want the folder's path, so we remove the __init__.py off the end of module_path
            module_path=get_parent_directory(module_path)
            
        baked_module_path=path_join(baked_folder_path,module_name)
        
        #if path_exists(baked_module_path):
            #print('Deleting old copy of '+repr(module_name)+' from '+repr(module_path))
            #delete_path(baked_folder_path)
            
        copy_path(module_path,baked_module_path,extract=True)
        print('Copied module '+repr(module_name)+' from '+repr(module_path))
        
    #Refactor all python files in the current project to reflect the new baked module names
    bowler=pip_import('bowler')#Runs only on python 3.6 and up
    for module_name in module_names:
        baked_module_name='.'.join([this_module_name,baked_folder_name,module_name])
        bowler.Query().select_module(module_name).rename(baked_module_name).write(interactive=False)
        print('Baked module '+module_name+' to '+baked_module_name)

#TEST (Don't run it here, run it in some other empty folder...)
# pip_import('pudb').set_trace()
# bake('rp','xonsh','IPython','prompt_toolkit')
