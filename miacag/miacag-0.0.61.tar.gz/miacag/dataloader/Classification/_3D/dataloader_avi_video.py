from dataloader.dataloader_base_video import VideoDataloaderTrain
from dataloader.dataloader_base_video import VideoDataloaderTest
import os
import torch
import numpy as np


class VideoDataloaderAVITrain(VideoDataloaderTrain):
    def __init__(self, video_path, csv_path, transforms=None):
        super(VideoDataloaderAVITrain, self).__init__(video_path,
                                                      csv_path,
                                                      transforms)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        vid_name = os.path.join(self.video_path, self.csv['path'].iloc[idx])
        video = self.load_video(vid_name)
        video = torch.from_numpy(video)
        data['labels'] = torch.tensor(np.int(self.mapped_labels.iloc[idx]))
        sample = {'inputs': video, config['labels_names']: labels}
        if self.transform:
            sample['inputs'] = self.transform(sample['inputs'])
        return sample


class VideoDataloaderAVITest(VideoDataloaderTest):
    def __init__(self, video_path, csv_path, nr_frames, transform=None):
        super(VideoDataloaderAVITest, self).__init__(video_path,
                                                     csv_path,
                                                     transform)
        self.nr_frames = nr_frames

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        vid_name = os.path.join(self.video_path, self.csv['path'].iloc[idx])
        video = self.load_video(vid_name)
        video = torch.from_numpy(video)
        patches = VideoDataloaderTest.create_patches(video,
                                                     self.nr_frames,
                                                     self.transform)
        data['labels'] = torch.tensor(np.int(self.mapped_labels.iloc[idx]))
        sample = {'inputs': patches,
                  config['labels_names']: labels,
                  'file': self.csv['path'].iloc[idx],
                  'shape': video.shape[2]}
        return sample
