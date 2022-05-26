# Copyright 2018 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""PointCloud Datasets
"""
import pickle
import time
import tqdm
import os
import glob
import torch
import numpy as np
import tw
import tw.transform as T
from tw.media.ply import read_ply, write_ply


class SensatUrban(torch.utils.data.Dataset):

  """https://github.com/QingyongHu/SensatUrban

    Ref: Towards Semantic Segmentation of Urban-Scale 3D Point Clouds:
        A Dataset, Benchmarks and Challenges
  """

  def __len__(self):
    return self.num_per_epoch

  def __init__(self, original_block_ply_path,
               grid_path,
               phase,
               batchsize,
               step,
               noise_init=3.5,
               num_points=65536,
               num_layers=5,
               knn_num=16,
               sub_sampling_ratio=[4, 4, 4, 4, 2],
               rank=0,
               subset='',
               **kwargs):
    tw.fs.raise_path_not_exist(original_block_ply_path)
    tw.fs.raise_path_not_exist(grid_path)

    # distributed sampler
    self.rank = rank
    self.subset = subset
    self.current_epoch = 0

    # record batchsize and step to prepare
    self.batchsize = batchsize
    self.step = step
    self.phase = phase
    # self.transform = transform
    self.num_per_epoch = self.step * self.batchsize
    self.noise_init = noise_init
    self.num_points = num_points
    self.num_layers = num_layers
    self.sub_sampling_ratio = sub_sampling_ratio
    self.knn_search = tw.nn.KnnSearch(k=knn_num)
    self.knn_search_up = tw.nn.KnnSearch(k=1)

    # label to name mapping
    self.label_to_names = {
        0: 'Ground', 1: 'High Vegetation', 2: 'Buildings', 3: 'Walls',
        4: 'Bridge', 5: 'Parking', 6: 'Rail', 7: 'traffic Roads', 8: 'Street Furniture',
        9: 'Cars', 10: 'Footpath', 11: 'Bikes', 12: 'Water'}
    self.num_classes = len(self.label_to_names)
    self.label_values = np.sort([k for k, v in self.label_to_names.items()])
    self.label_to_idx = {l: i for i, l in enumerate(self.label_values)}
    self.ignored_labels = np.array([])

    # make sure original ply
    all_files = np.sort(glob.glob(os.path.join(original_block_ply_path, '*.ply')))

    # val and test subset
    if self.subset == 'all':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5', 'cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8', 'cambridge_block_15', 'cambridge_block_22',
                        'cambridge_block_16', 'cambridge_block_27']
    elif self.subset == 'birmingham':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8']
    elif self.subset == 'cambridge':
      val_file_name = ['cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['cambridge_block_15', 'cambridge_block_22', 'cambridge_block_16', 'cambridge_block_27']
    elif self.subset == 'bike':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5', 'cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8', 'cambridge_block_15', 'cambridge_block_22',
                        'cambridge_block_16', 'cambridge_block_27']
    elif self.subset == 'rail':
      val_file_name = ['birmingham_block_1', 'birmingham_block_5', 'cambridge_block_10', 'cambridge_block_7']
      test_file_name = ['birmingham_block_2', 'birmingham_block_8', 'cambridge_block_15', 'cambridge_block_22',
                        'cambridge_block_16', 'cambridge_block_27']
    else:
      raise NotImplementedError(self.subset)

    # train subset
    if self.subset == 'all':
      train_file_name = [x.split('/')[-1][:-4] for x in all_files]
    elif self.subset == 'birmingham':
      train_file_name = [x.split('/')[-1][:-4] for x in filter(lambda x: 'birmingham' in x, all_files)]
    elif self.subset == 'cambridge':
      train_file_name = [x.split('/')[-1][:-4] for x in filter(lambda x: 'cambridge' in x, all_files)]
    elif self.subset == 'bike':
      train_file_name = ['cambridge_block_12', 'cambridge_block_13', 'cambridge_block_18']
    elif self.subset == 'rail':
      train_file_name = ['birmingham_block_4']
    else:
      raise NotImplementedError(self.subset)

    # train filter val and test collection
    for name in train_file_name:
      if name in val_file_name or name in test_file_name:
        train_file_name.remove(name)

    # select used files
    self.all_files = []
    for file_path in all_files:
      cloud_name = file_path.split('/')[-1][:-4]
      if self.phase == tw.phase.train and cloud_name in train_file_name:
        self.all_files.append(file_path)
      elif self.phase == tw.phase.val and cloud_name in val_file_name:
        self.all_files.append(file_path)
      elif self.phase == tw.phase.test and cloud_name in test_file_name:
        self.all_files.append(file_path)
    assert len(self.all_files) > 0, "at least including a file."

    # initialize
    self.num_per_class = np.zeros(self.num_classes)
    self.val_proj = []
    self.val_labels = []
    self.test_proj = []
    self.test_labels = []
    self.possibility = {}
    self.min_possibility = {}
    self.input_trees = []
    self.input_colors = []
    self.input_labels = []
    self.input_names = []

    # loading sub-sampled clouds
    self.load_sub_sampled_clouds(grid_path)

    # remove ignored labels
    for ignore_label in self.ignored_labels:
      self.num_per_class = np.delete(self.num_per_class, ignore_label)

    # generate possibility
    self.possibility = []
    self.min_possibility = []
    for i, tree in enumerate(self.input_colors):
      if self.phase == tw.phase.train:
        # where we define random sample possibility for each data point of each file.
        self.possibility += [np.random.rand(tree.data.shape[0]) * 0.001]
      else:
        # for validation or test, we uniformly sample.
        self.possibility += [np.zeros(tree.data.shape[0])]
      # find minimum possibility
      self.min_possibility += [float(np.min(self.possibility[-1]))]

    tw.logger.info(f'num samples per class: {self.num_per_class.tolist()}')
    tw.logger.info(f'generate {len(self.input_colors)} group possibility.')

  def load_sub_sampled_clouds(self, sub_grid_path):
    """loading and process sub-sampled clouds.
    """
    # loading original ply to split train/val/test
    for i, file_path in enumerate(self.all_files):
      t0 = time.time()
      cloud_name = file_path.split('/')[-1][:-4]

      # name of the input files
      kd_tree_file = os.path.join(sub_grid_path, '{:s}_KDTree.pkl'.format(cloud_name))
      sub_ply_file = os.path.join(sub_grid_path, '{:s}.ply'.format(cloud_name))

      data = read_ply(sub_ply_file)
      sub_colors = np.vstack((data['red'], data['green'], data['blue'])).T
      sub_labels = data['class']

      # compute num_per_class in training set
      if self.phase == tw.phase.train:
        self.num_per_class += self.get_num_class_from_label(sub_labels, self.num_classes)

      # read pkl with search tree
      with open(kd_tree_file, 'rb') as f:
        search_tree = pickle.load(f)

      self.input_trees += [search_tree]
      self.input_colors += [sub_colors]
      self.input_labels += [sub_labels]
      self.input_names += [cloud_name]

      size = sub_colors.shape[0] * 4 * 7
      tw.logger.info('[{}] {:s} {:.1f} MB loaded in {:.1f}s, search_tree:{}, sub_colors:{}, sub_labels:{}'.format(
          self.phase.name, kd_tree_file.split('/')[-1], size * 1e-6, time.time() - t0,
          search_tree.data.shape, sub_colors.shape, sub_labels.shape))

  def get_num_class_from_label(self, labels, total_class):
    """count number sample of per class.

    Args:
        labels ([np.numpy]): sample labels.
        total_class ([int]): number of classes

    Returns:
        [int]: number sample per class
    """
    num_pts_per_class = np.zeros(total_class, dtype=np.int32)
    # original class distribution
    val_list, counts = np.unique(labels, return_counts=True)
    for idx, val in enumerate(val_list):
      num_pts_per_class[val] += counts[idx]
    return num_pts_per_class

  def get_class_weights(self, num_per_class, name='sqrt'):
    # pre-calculate the number of points in each category
    frequency = num_per_class / float(sum(num_per_class))
    ce_label_weight = np.zeros_like(frequency)

    if name == 'sqrt' or name == 'lovas':
      ce_label_weight[frequency != 0] = 1 / np.sqrt(frequency[frequency != 0])
    elif name == 'wce':
      ce_label_weight = 1 / (frequency + 0.02)
    elif name == 'cb':
      beta = 0.999
      frequency = np.sqrt(frequency)
      ce_label_weight[frequency != 0] = (1 - beta) / (1 - np.power(beta, frequency[frequency != 0]))
    else:
      raise ValueError('Only support sqrt and wce')
    return np.expand_dims(ce_label_weight, axis=0)

  def shuffle_idx(self, x):
    """shuffle list.

    Args:
        x ([list]): a list

    """
    idx = np.arange(len(x))
    np.random.shuffle(idx)
    return x[idx]

  def data_aug(self, xyz, color, labels, idx, num_out):
    """repeat points
    """
    num_in = len(xyz)
    dup = np.random.choice(num_in, num_out - num_in)
    xyz_dup = xyz[dup, ...]
    xyz_aug = np.concatenate([xyz, xyz_dup], 0)
    color_dup = color[dup, ...]
    color_aug = np.concatenate([color, color_dup], 0)
    idx_dup = list(range(num_in)) + list(dup)
    idx_aug = idx[idx_dup]
    label_aug = labels[idx_dup]
    return xyz_aug, color_aug, idx_aug, label_aug

  def sample(self):
    # select a minimum possibility point cloud
    cloud_idx = int(np.argmin(self.min_possibility))

    # choose a minimum possibility point from minimum possibility point cloud
    point_ind = np.argmin(self.possibility[cloud_idx])

    # get points from tree structure [k, 3]
    points = np.array(self.input_trees[cloud_idx].data, copy=False)

    # center point of input region [1, 3]
    center_point = points[point_ind, :].reshape(1, -1)

    if self.phase == tw.phase.train:
      # add noise to the center point
      noise = np.random.normal(scale=self.noise_init / 10, size=center_point.shape)
      pick_point = center_point + noise.astype(center_point.dtype)
    else:
      # 1) fixed point to inference but maybe damage effects.
      # pick_point = center_point
      # 2) vanilla implementation: random sample but need multiple inference.
      # add noise to the center point
      noise = np.random.normal(scale=self.noise_init / 10, size=center_point.shape)
      pick_point = center_point + noise.astype(center_point.dtype)

    # sample nearest points
    if len(points) < self.num_points:
      queried_idx = self.input_trees[cloud_idx].query(pick_point, k=len(points))[1][0]
    else:
      queried_idx = self.input_trees[cloud_idx].query(pick_point, k=self.num_points)[1][0]

    # shuffle nearest points index
    if self.phase == tw.phase.train:
      queried_idx = self.shuffle_idx(queried_idx)
    else:
      # using random point to inference and take average
      queried_idx = self.shuffle_idx(queried_idx)

    # collect points and colors ([num_points, 3], [num_points, 3], [num_points, ])
    queried_pc_xyz = points[queried_idx]
    queried_pc_xyz = queried_pc_xyz - pick_point  # normalize spatial position in terms of pick point
    queried_pc_colors = self.input_colors[cloud_idx][queried_idx]
    queried_pc_labels = self.input_labels[cloud_idx][queried_idx]

    # compute normalized distance between sampled points and center points
    dists = np.sum(np.square((points[queried_idx] - pick_point).astype(np.float32)), axis=1)
    # close to center, gain higher possibility
    delta = np.square(1 - dists / np.max(dists))  # to [0, 1]
    # add delta to vanilla
    self.possibility[cloud_idx][queried_idx] += delta
    self.min_possibility[cloud_idx] = float(np.min(self.possibility[cloud_idx]))

    if len(points) < self.num_points:
      queried_pc_xyz, queried_pc_colors, queried_idx, queried_pc_labels = self.data_aug(
          queried_pc_xyz, queried_pc_colors, queried_pc_labels, queried_idx, self.num_points)

    return (queried_pc_xyz[None].astype(np.float32),  # [1, 65536, 3]
            queried_pc_colors[None].astype(np.float32),  # [1, 65536, 3]
            queried_pc_labels[None],  # [1, 65536, ]
            queried_idx[None].astype(np.int32),  # [1, 65536, ]
            np.array([cloud_idx], dtype=np.int32))  # [1, ]

  def sample_an_epoch_impl(self):
    targets = []
    for _ in tqdm.tqdm(range(self.num_per_epoch)):
      # (1, 65536, 3) (1, 65536, 3) (1, 65536,) (1, 65536,) (1,)
      pc_xyz, pc_colors, pc_labels, queried_idx, cloud_idx = self.sample()
      targets.append((pc_xyz, pc_colors, pc_labels, queried_idx, cloud_idx))
    return targets

  def sample_an_epoch(self):
    """add using cephFS code, it require at least 1.5T space.
    """
    t1 = time.time()

    # path1: prefer to select a cache file
    if self.num_points == 16384:
      if self.phase == tw.phase.train and self.num_per_epoch == 8000:
        cache_path = f'/cephFS/jk/SensatUrban/{self.num_per_epoch}/Epoch-{self.current_epoch}.pth'
      elif self.phase != tw.phase.train and self.num_per_epoch == 5600:
        cache_path = f'/cephFS/jk/SensatUrban/{self.num_per_epoch}/{self.phase.name}.pth'
      else:
        cache_path = None
    else:
      cache_path = None

    # sample or load
    if cache_path is None:
      self.targets = self.sample_an_epoch_impl()

    elif not os.path.exists(cache_path):
      self.targets = self.sample_an_epoch_impl()

      # allowing to create a folder
      try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        torch.save(self.targets, cache_path)
        tw.logger.info(f'save targets to cephFS: {cache_path}')
      except BaseException:
        tw.logger.warn(f'failed to save targets to cephFS: {cache_path}')

    else:
      tw.logger.info(f'load targets from cephFS: {cache_path}')
      self.targets = torch.load(cache_path, 'cpu')

    t2 = (time.time() - t1)

    # distribution
    self.sample_weight = np.array(self.get_class_weights(self.num_per_class, name='sqrt')[0])

    # stat
    tw.logger.info(f'generate a batch of {len(self.targets)} samples, {t2}s.')
    self.current_epoch += 1

  def normalize(self, weight):
    return weight / np.sum(weight, axis=0)

  def __getitem__(self, idx):

    # sample a item
    # (1, 65536, 3) (1, 65536, 3) (1, 65536,) (1, 65536,) (1,)
    pc_xyz, pc_colors, pc_labels, queried_idx, cloud_idx = self.targets[idx]

    # xyz + colors to tensor [bs, num_points, 6]
    input_features = torch.cat([torch.tensor(pc_xyz), torch.tensor(pc_colors)], dim=2)[0].transpose(1, 0)

    # labels to tensor [bs, num_points]
    input_labels = torch.tensor(pc_labels).long()[0]
    input_queried = torch.tensor(queried_idx).long()[0]
    input_idx = torch.tensor(cloud_idx).long()[0]

    # random pooling: form [1, 1, 65536] -> [1, 1, 256]
    input_points, input_neighbors, input_pools, input_up_samples = [], [], [], []

    # random
    sub_labels = pc_labels[0]
    select_random_sample = np.random.rand() > 0.2

    for i in range(self.num_layers):
      # find neighbour_idx of pc_xyz
      _, num_points, _ = pc_xyz.shape
      neighbour_idx = self.knn_search(pc_xyz, pc_xyz)  # pc_xyz [1, 65546, 3], idx[1, 65536, 16]

      if self.phase == tw.phase.train:

        if select_random_sample:
          # 1) random sample
          # there, it is not to sample top-k points
          # note that the sequence order of pc_xyz has been shuffled during training.
          # therefore, top (num_points // self.sub_sampling_ratio[i]) points means that
          #   sample random (num_points // self.sub_sampling_ratio[i]) points from whole space
          #   instead of top-k space.
          sub_points = pc_xyz[:, :num_points // self.sub_sampling_ratio[i], :]  # [1, 16384, 3]
          pool_i = neighbour_idx[:, :num_points // self.sub_sampling_ratio[i], :]  # [1, 16384, 16]

        else:
          # 2) weighted sample
          inds = np.random.choice(np.arange(num_points),
                                  size=num_points // self.sub_sampling_ratio[i],
                                  p=self.normalize(self.sample_weight[sub_labels]))
          sub_labels = sub_labels[inds]
          sub_points = pc_xyz[:, inds, :]
          pool_i = neighbour_idx[:, inds, :]

      else:
        # NOTE: if using `queried_idx = self.shuffle_idx(queried_idx)`, this line will
        # take no effects!!!
        # sample point in terms of fixed stride to subsample whole space.
        sub_points = pc_xyz[:, ::self.sub_sampling_ratio[i], :]  # [1, 16384, 3]
        pool_i = neighbour_idx[:, ::self.sub_sampling_ratio[i], :]  # [1, 16384, 16]

      # find nearest points for each pc_xyz in sub_points
      up_i = self.knn_search_up(sub_points, pc_xyz)  # [1, 16384, 1]

      # add into tensor list
      input_points.append(torch.tensor(pc_xyz.transpose(0, 2, 1))[0].float().unsqueeze(-1))  # [bs, 3, num_points, 1]
      input_neighbors.append(torch.tensor(neighbour_idx)[0].long())  # [bs, num_points, num_neighbor]
      input_pools.append(torch.tensor(pool_i)[0].long())  # [bs, sub_num_points, num_neighbor]
      input_up_samples.append(torch.tensor(up_i)[0].long())  # [bs, num_points, num_neighbor]

      # next, we use sub_points to sample. aka. <random pool>
      pc_xyz = sub_points

    return input_points, input_neighbors, input_pools, input_up_samples, input_features, input_labels, input_queried, input_idx
