from __future__ import print_function, absolute_import, division

import os
import h5py
import glob
import numpy as np
import poseutils.camera_utils as cameras
from poseutils.logger import log
from poseutils.constants import dataset_indices
from poseutils.datasets.unprocessed.Dataset import Dataset

class H36MDataset(Dataset):
    """Dataset class for H36M dataset.

        :param path: Base directory path to h36m files with cameras.h5
        :type path: str
    """

    def __init__(self, path):
        super(H36MDataset, self).__init__('h36m')

        self.actions = ["Directions","Discussion","Eating","Greeting",
           "Phoning","Photo","Posing","Purchases",
           "Sitting","SittingDown","Smoking","Waiting",
           "WalkDog","Walking","WalkTogether"]

        self.train_subs = [1, 5, 6, 7, 8]
        self.test_subs = [9, 11]

        self.load_data(path)

    def load_data(self, path):

        self.cameras = cameras.load_cameras(os.path.join(path, "cameras.h5"))

        trainset = self.load_3d_data(path, self.train_subs, self.actions)
        testset = self.load_3d_data(path, self.test_subs, self.actions)

        self._data_train['raw'] = trainset
        self._data_valid['raw'] = testset

        d2d_train, _, d3d_train = self.project_to_cameras(trainset)
        d2d_valid, _, d3d_valid = self.project_to_cameras(testset)

        self._data_train['2d'] = d2d_train
        self._data_train['3d'] = d3d_train
        self._data_valid['2d'] = d2d_valid
        self._data_valid['3d'] = d3d_valid

        log("Loaded raw data")

    def load_3d_data(self, path, subjects, actions):

        data = {}

        total_data_points = 0
        for subj in subjects:
            for action in actions:

                dpath = os.path.join( path, 'S{0}'.format(subj), 'MyPoses/3D_positions', '{0}*.h5'.format(action) )

                fnames = glob.glob( dpath )

                loaded_seqs = 0

                for fname in fnames:

                    seqname = os.path.basename( fname )

                    if action == "Sitting" and seqname.startswith( "SittingDown" ):
                        continue

                    if seqname.startswith( action ):
                        loaded_seqs = loaded_seqs + 1

                        with h5py.File( fname, 'r' ) as h5f:
                            poses = h5f['3D_positions'][:]
                            poses = poses.T

                            data[( subj, action, seqname )] = poses.reshape((-1, 32, 3))

                            total_data_points += poses.shape[0]

        return data

    def project_to_cameras( self, poses_set):

        t2d = []
        t2dc = []
        t3d = []

        total_points = 0
        for key in poses_set.keys():
            (subj, action, sqename) = key
            t3dw = poses_set[key]

            for cam in range(4):
                R, T, f, c, k, p, name = self.cameras[ (subj, cam+1) ]

                t3dc = cameras.world_to_camera_frame( np.reshape(t3dw, [-1, 3]), R, T)
                pts2d, _, _, _, _ = cameras.project_point_radial( np.reshape(t3dw, [-1, 3]), R, T, f, c, k, p )
                cam2d = np.divide(pts2d - c.T, f.T)
                pts2d = np.reshape( pts2d, [-1, 32, 2] )
                total_points += pts2d.shape[0]
                t2d.append(pts2d)
                t3d.append(t3dc.reshape((-1, 32, 3)))
                t2dc.append(cam2d.reshape((-1, 32, 2)))

        t2d = np.vstack(t2d)
        t2dc = np.vstack(t2dc)
        t3d = np.vstack(t3d)

        return t2d, t2dc, t3d
