# -*- coding: utf-8 -*-
"""Blur eye.ipynb
### **Blur eyes in a human face**
This notebook uses OpenCV to blur human eyes

Importing libraries.
- OpenCV is a image processing library.
- dlib
- Matplotlib to visualize images
"""
import os
import glob
import cv2
import numpy as np
import sys


import dlib

"""Then find facial landmarks using a [pre-trained 68 point predictor:](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)"""


#Blurs eye in a single image
def blur_eyes_in_image(file_path,save_base_path,save_name,sp,size):

    """Load a image using `cv2.imread `function"""
    img = cv2.imread(file_path)

    # Convert to dlib
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #plt.imshow(img)

    """Next, you can use the dlib face detector to detect the faces (second argument means to upsample by 1x):"""

    #detect the faces
    detector = dlib.get_frontal_face_detector()
    detections = detector(img, 1)


    faces = dlib.full_object_detections()
    for det in detections:
        faces.append(sp(img, det))


    """Note: From here you could get face chips dlib.get_face_chip(img, faces[0])

    extract all the detections
    """

    # Find landmarks
    faces = dlib.full_object_detections()
    for det in detections:
        faces.append(sp(img, det))


    """Get the bounding boxes"""

    # Bounding box and eyes
    bb = [i.rect for i in faces]
    bb = [((i.left(), i.top()),
               (i.right(), i.bottom())) for i in bb]                            # Convert out of dlib format

    right_eyes = [[face.part(i) for i in range(36, 42)] for face in faces]
    right_eyes = [[(i.x, i.y) for i in eye] for eye in right_eyes]          # Convert out of dlib format

    left_eyes = [[face.part(i) for i in range(42, 48)] for face in faces]
    left_eyes = [[(i.x, i.y) for i in eye] for eye in left_eyes]            # Convert out of dlib format

    # Display
    imgd = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)             # Convert back to OpenCV


    """Blur the right and left eyes using the gaussian blur effect from opencv"""

    for eye in right_eyes:
        x2 = max(eye, key=lambda x: x[0])[0] + size
        y2 = max(eye, key=lambda x: x[1])[1] + size
        x1 = min(eye, key=lambda x: x[0])[0] - size
        y1 = min(eye, key=lambda x: x[1])[1] - size
        # merge this blurry rectangle to our final image
        imgd[y1:y2, x1:x2] = cv2.GaussianBlur(imgd[y1:y2,x1:x2],(23, 23), 30)

    for eye in left_eyes:
        x2 = max(eye, key=lambda x: x[0])[0] + size
        y2 = max(eye, key=lambda x: x[1])[1] + size
        x1 = min(eye, key=lambda x: x[0])[0] - size
        y1 = min(eye, key=lambda x: x[1])[1] - size
        # merge this blurry rectangle to our final image
        imgd[y1:y2, x1:x2] = cv2.GaussianBlur(imgd[y1:y2,x1:x2],(23, 23), 30)

    RGB_img = cv2.cvtColor(imgd, cv2.COLOR_BGR2RGB)

    #save file
    face_file_name = save_base_path + '/' + save_name
    cv2.imwrite(face_file_name, imgd)

"""The below function blurs eyes for a batch of images. Store the images in a folder and store the folder in the same folder of blur_face.py"""
def blur_eyes_in_images(file_base_path,save_base_path,size):
    read_files = glob.glob(file_base_path+"/*.jpeg")
    paths = [file_name for file_name in read_files]
    #load pretrained model
    sp = dlib.shape_predictor("./model/shape_predictor_68_face_landmarks.dat")

    for path in paths:
      save_name_arr = path.split('/')
      file_name = save_name_arr[len(save_name_arr)-1]
      #print('file_name',file_name)
      blur_eyes_in_image(path,save_base_path,file_name,sp,size)

    print('Saved at {} '.format(save_base_path))
