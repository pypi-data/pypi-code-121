# saving figures and gifs

from datetime import date


def auto_save(fig_obj, fig_name, close_after=True, extension='.png', custom_folder='', folder_level=3):
    '''
    Automatically save figures in an organized manner

    INPUTS:
    fig_obj: figure object, object 
    fig_name: figure name, string 
    close_after: close figure after saving, boolean 
    extension: extension for figure file, default='.png (not friendly with other formats)
    custom_folder: custom folder name to save in, default='', string
    folder_level: level for custom folder, default=3
        level 1: current folder 
        level 2: figures folder 
        level 3: date folder 
    '''

    # import needed library 
    import os 
    import datetime
    import matplotlib

    ## Local functions 
    def find_create_enter_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)
    def saveFigure(fig_obj, fig_name, extension):
        if '.png' in fig_name:
            fig_obj.savefig(fig_name, bbox_inches='tight')
        else:
            fig_obj.savefig(fig_name+extension, bbox_inches='tight')

    ## Set up 
    cwd = os.getcwd()
    today = datetime.datetime.now()
    date_dir = today.strftime("%m_%d_%Y")

    ## Go to specific location 
    if custom_folder=='':
        path_str = cwd+'/figures/'+date_dir
    else : 
        if folder_level >= 1: # working folder 
            path_str = cwd+'/'+custom_folder
        if folder_level >= 2: # figures folder 
            path_str = cwd+'/figures/'+custom_folder
        if folder_level == 3: # current date folder 
            path_str = cwd+'/figures/'+date_dir+'/'+custom_folder
    find_create_enter_folder(path_str)

    ## Save
    saveFigure(fig_obj=fig_obj, fig_name=fig_name, extension=extension)

    ## Close and return to working directory 
    if close_after: # close 
        matplotlib.pyplot.close(fig_obj)
    os.chdir(cwd)

def writeGif(filenameG, filenames, custom_folder='', folder_level=3, fps=25):
    '''
    Save figure files as gif file and delete figures used to create gif 

    INPUTS:
    filenameG: filename for .gif file 
    filenames: filenames of individual figures to be saved together as gif
    custom_folder: custom folder name to save in, default='', string
    folder_level: level for custom folder, default=3
        level 1: current folder 
        level 2: figures folder 
        level 3: date folder 
    fps: frames per second
    '''
    # import libraries 
    import imageio 
    import os 
    import datetime
    import matplotlib

    ## Local functions 
    def find_create_enter_folder(path):
        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(path)
    def saveGif(filenameG, filenames, fps):
        with imageio.get_writer(filenameG+'.gif', mode='I', fps=fps) as writer:
            for filename in filenames:
                image = imageio.imread(filename)
                writer.append_data(image) # add to gif 
                os.remove(filename) # delete individual 

    ## Set up 
    cwd = os.getcwd()
    today = datetime.datetime.now()
    date_dir = today.strftime("%m_%d_%Y")

    ## Go to specific location 
    if custom_folder=='':
        path_str = cwd+'/figures/'+date_dir
    else : 
        if folder_level >= 1: # working folder 
            path_str = cwd+'/'+custom_folder
        if folder_level >= 2: # figures folder 
            path_str = cwd+'/figures/'+custom_folder
        if folder_level == 3: # current date folder 
            path_str = cwd+'/figures/'+date_dir+'/'+custom_folder
    find_create_enter_folder(path_str)

    ## Save
    saveGif(filenameG=filenameG, filenames=filenames, fps=fps)
    
    # Get back to original folder 
    os.chdir(cwd)