import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
from PIL import Image
import fire
import random


def process_one(image_type: str, image_name: str, percentage: float,
                image_root: str, adapted_root: str):
    # TODO: genericise. Currently assumes all file names are the same.
    target_image = f'{image_root}/{image_type}/{"_".join(image_name.split("_"))}'
    img = cv2.imread(target_image)[:,:,::-1]
    img = cv2.resize(img, (512,512))

    adapted_img = f"{adapted_root}/{image_name}"
    adapted_img = np.array(Image.open(adapted_img).resize((512,512)))
    # adapted_img = cv2.imread(adapted_img)
    adapted_img.resize((512,512,3))
    # adapted_img = adapted_img[:,:,::-1]

    img_adj = int( img.shape[1] * percentage )
    reverse_adj = img.shape[1] - img_adj
    result_img = np.hstack(( img[:,:img_adj,:], adapted_img[:, img_adj:,:] ))
    # result_img = np.concat([img[:percentage_adj], adapted_img[percentage_adj:])

    return result_img



def create_viz(
    images = '/efs/public_data/gta5/images',
    labels = 'labels',
    adapted = '/efs/public_data/images'):

    labels = '/'.join(images.split('/')[:-1]) + labels
    # set up ui
    label_paths = sorted([ x for x in os.listdir(labels) ])[:1000]
    image_paths = sorted([ x for x in os.listdir(images) ])[:1000]
    adapted_paths = sorted([ x for x in os.listdir(adapted) ])[2:1000]

    im_type = ['rgb', 'label']
    tar_im_type = st.sidebar.selectbox("Which type of image?", im_type)

    file_selection = st.sidebar.selectbox("Which file?", adapted_paths)

    percentage = st.sidebar.slider("percentage", 0, 100) / 100

    if st.button('Random Image'):
        file_selection = random.choice(image_paths)
    #     i = image_paths.index(file_selection)
    #     file_selection = image_paths[i+var_i]
    #     var_i += 1
        st.code(f"{adapted}/{file_selection}")
    else:
        st.write(f'Offset {var_i}')

    image_root = '/'.join(images.split('/')[:-1])
    adapted_root = '/'.join(adapted.split('/')[:-1])

    kpd_img = process_one(tar_im_type, file_selection, percentage,
                            image_root, adapted_root)
    kpd_img_1 = process_one(tar_im_type, file_selection, 0,
                            image_root, adapted_root)
    kpd_img_2 = process_one(tar_im_type, file_selection, 1,
                            image_root, adapted_root)

    # st.image(kpd_img, width=256)
    # st.image(kpd_img_1, width=256)
    # st.image(kpd_img_2, width=256)

    col1, col2, col3 = st.beta_columns(3)
    col1.header("Mix")
    col1.image(kpd_img, use_column_width=True)

    col2.header("Adapted")
    col2.image(kpd_img_1, use_column_width=True)

    col3.header("Original")
    col3.image(kpd_img_2, use_column_width=True)


if __name__ == "__main__":
    fire.Fire(create_viz)