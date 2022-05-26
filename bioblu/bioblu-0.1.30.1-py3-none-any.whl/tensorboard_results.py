#!/usr/bin/env python3

import os
import tensorboard


def show_results(fpath):
    os.system(f"tensorboard --logdir={fpath}")


if __name__ == '__main__':
    FDIR = '/media/findux/DATA/Documents/Malta_II/radagast_transport/3303_2022-02-07_201522_on_dataset_01/'
    FDIR = "/home/findux/Desktop/tmp/2022-04-25_0002/"
    FDIR = "/media/findux/DATA/Documents/Malta_II/colab_outputs/2022-04-25_0002/"
    FDIR = "file:///media/findux/DATA/Documents/Malta_II/results/5239_2022-05-07_052041/"
    show_results(FDIR)

    # then open http://localhost:6006/ in browser.