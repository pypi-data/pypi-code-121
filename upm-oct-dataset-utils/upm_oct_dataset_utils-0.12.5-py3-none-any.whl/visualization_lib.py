
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from mpl_toolkits.axes_grid1 import make_axes_locatable

def show_image(image, title:list[str]=None, subplot_size:tuple[int,int]=None, 
                    cmap:str='jet', colorbar:bool=None, multi:bool=False, show:bool=True):
    # Procesamos el fichero y obtenemos sus datos
    if not multi:
        images = [image]; titles = [title]
    else:
        images = image; titles = title
    if subplot_size is None:
        subplot_size = (1, len(images))
    canvas = []
    for i, im in enumerate(images):
        plt.subplot(subplot_size[0], subplot_size[1], i+1)
        if titles is not None and i < len(titles):
            plt.title(titles[i])
        if colorbar is not None:
            # -- Hace que la colorbar se vea de la misma altura que la imagen --
            #--------------------- copiado de internet -------------------------
            ax = plt.gca()
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            # create an axes on the right side of ax. The width of cax will be 5%
            # of ax and the padding between cax and ax will be fixed at 0.05 inch.
            # ------------------------------------------------------------------
            colormap = plt.get_cmap(cmap)
            frame = ax.imshow(im, cmap=colormap)
            plt.colorbar(frame, cax=cax) 
        else:
            frame = plt.imshow(im, cmap=cmap)
        canvas.append(frame)
    
    if show: plt.show()
    
    return canvas
        
def animate_volume(volume, figure=None, title:list[str]=None, subplot_size:tuple[int,int]=None, 
                    cmap:str='jet', colorbar:bool=None, multi:bool=False, t_milisec:int=4000, repeat=True):
    if not multi:
        volumes = [volume]; titles = [title]
    else:
        volumes = volume; titles = title
    
    if figure is None: 
        figure = plt.figure()
    
    def _get_volume_length(vol):
        type
        if type(vol) is list:
            return len(vol)
        else:
            return vol.shape[0]
    
    first_frames = []; max_length = 0
    for vol in volumes:
        first_frames.append(vol[0])
        vol_len = _get_volume_length(vol)
        if vol_len > max_length: max_length = vol_len
        
    canvas = show_image(
        first_frames, title=titles, subplot_size=subplot_size, cmap=cmap, 
            colorbar=colorbar, multi=True, show=False
        )
        
    frames = []
    for i in range(max_length):
        frame_group = []
        for vol in volumes:
            vol_len = _get_volume_length(vol)
            ratio = int(max_length/vol_len)
            if i%ratio == 0:
                frame_group.append(vol[int(i/ratio)])
            else:
                frame_group.append(None)
                
        frames.append((len(frames)+1, frame_group))
    
    def _update_frames(frames:tuple, *fargs, **kwarg):
        frame_num, frames = frames
        total_frames = fargs[0]
        figure.suptitle(f'Frame {frame_num}/{total_frames}', fontsize=15)
        for i, frame in enumerate(frames):
            if frame is not None:
                canvas[i].set_data(frame)
        return canvas
            
    t_animation = t_milisec # Milisegundos
    num_slices = max_length
    t_sleep = int(t_animation/num_slices)
    
    animation = anim.FuncAnimation(
            figure, 
            _update_frames, 
            fargs=[len(frames)],
            frames=frames, 
            interval=t_sleep,
            repeat=repeat,
            # blit=True -> Esta opcion no permite actualizar el titulo, aunque mejora la velocidad de carga de los frames
        )
    plt.show()
    
    return animation