import skimage.io
import os
import cv2
import numpy as np
def frames_to_video(pathIn,
            pathOut,
             fps,
             
            ):
    '''
    a utility that takes in a folder containing image frames `pathIn`
    and generates a video `pathOut` at certain `fps`
    '''

    frame_array = []
    files = [f for f in os.listdir(pathIn) if os.path.isfile(os.path.join(pathIn, f))]

    #for sorting the file names properly
    files.sort(key = lambda x: int(x[:-4]))

    for i in range(len(files)):
        filename= os.path.join(pathIn,files[i])
        #reading each files
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
#         print(filename)
        #inserting the frames into an image array
        frame_array.append(img)

    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()

def start_video(frames_folder,video_filename,fps=20,lazy_video=True):
    '''
    utility to monitor a process by making a video. for e.g. we could monitor 
    an image GAN's generated image for the same input code over time
    requires `frames_folder` to dump all the intermediate frames, `video_filename`,`fps`.
    `lazy_video` collects all the frames into a video only when a trigger is called
    else it keeps making a video out of the frames collected thus far.

    returns: 2 functions `add_to_video` to add the next frame, `finish_video` to trigger
    the end of the video creation. see `lazy_video` above
    '''

    counter = [0]
    if not os.path.isdir(frames_folder):
        os.mkdir(frames_folder)
    pass    
    def add_to_video(frame):
        '''.add the next frame to video '''
        ix = counter[0]
        skimage.io.imsave(os.path.join(frames_folder,f'{ix}.png'),frame)
        if not lazy_video:
            frames_to_video(frames_folder,
                            video_filename,
                            fps)        
        counter[0] = counter[0] + 1
        pass
    def finish_video():
        '''.end the video '''
        frames_to_video(frames_folder,
                        video_filename,
                        fps)        
        pass
    return add_to_video,finish_video

def test_video_creator():
    import tempfile
    fps = 20
    n_frames = 100
    #-----------------------------------------------------------------
    frame_size = (100,100)
    speed = 1
    strip_size = 20
    #-----------------------------------------------------------------
    for lazy_video in [True,False]:
        with tempfile.TemporaryDirectory() as frames_folder:
            with tempfile.TemporaryDirectory() as output_video_folder:
                add_to_video,finish_video = start_video(frames_folder,os.path.join(output_video_folder,f'video{"_lazy_video" if lazy_video else ""}_fps{fps}_frame_size{frame_size[0]}.mp4'),fps=fps,lazy_video=lazy_video)    
                for i in range(n_frames):
                    frame = np.zeros(frame_size+(3,))
                    frame[:, int(i*speed):min(int(i*speed)+strip_size,frame_size[1]),:] = 1
                    add_to_video(frame)
                finish_video()
    pass
test_video_creator()