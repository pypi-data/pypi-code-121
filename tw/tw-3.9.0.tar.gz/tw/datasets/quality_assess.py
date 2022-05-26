# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
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
"""Image quality assessment dataset:

  - PIPAL
  - HTID
  - TID2013
  - CSIQ
  - KonIQ10k
  - SPAQ
  - LIVEC
  - LIVE2005
  - LIVEMD
  - LIVEVideo
  - VQA-III

"""
import copy
import os
from collections import OrderedDict
import torch
import scipy
import numpy as np
import tw
import tw.transform as T


#!<-----------------------------------------------------------------------------
#!< PIPAL DATASET
#!<-----------------------------------------------------------------------------


class PIPAL(torch.utils.data.Dataset):
  """PIPAL dataset

    training data
      200 reference images
      23,200 distortion images
      MOS scores for each distortion image

    validation data
      25 reference images
      1,000 distortion images

    PIPAL Root
    ├── [ 36K]  Dis
    ├── [212K]  Distortion_1
    ├── [196K]  Distortion_2
    ├── [204K]  Distortion_3
    ├── [204K]  Distortion_4
    ├── [4.0K]  Ref
    ├── [4.0K]  Train_Label
    └── [4.0K]  Train_Ref

  """

  def __init__(self, path, transform, phase=tw.phase.train, split=(0, 200), blind_mode=False, **kwargs):
    """PIPAL dataset. It only contains training label. Therefore, we need to split
     a part of data as validation set. The default split (0, 200) means that
     all data is used for trianing.


    Train:
      ref_file_path distort_file_path mos
      ...

    Val/Test:
      ref_file_path distort_file_path
      ...

    Args:
        path ([type]): path to pipal root
        transform ([type]): augmentation
        split (tuple, optional): defaults to (0, 200).
    """

    tw.fs.raise_path_not_exist(path)

    if phase == tw.phase.train:

      start, end = split[0], split[1]
      assert start >= 0 and end <= 200, "wrong split."

      dir_label = os.path.join(path, 'Train_Label')
      dir_ref = os.path.join(path, 'Train_Ref')
      folds = ['Distortion_1', 'Distortion_2', 'Distortion_3', 'Distortion_4']
      dir_distort = [os.path.join(path, fold) for fold in folds]

      dir_label_files = []
      for f in sorted(os.listdir(dir_label)):
        dir_label_files.append(os.path.join(dir_label, f))

      dir_ref_files = []
      for f in sorted(os.listdir(dir_ref)):
        dir_ref_files.append(os.path.join(dir_ref, f))

      # select a subset
      dir_ref_files = dir_ref_files[start: end]
      dir_label_files = dir_label_files[start:end]

      dir_distort_files = {}
      for d in sorted(dir_distort):
        for f in sorted(os.listdir(d)):
          file_path = os.path.join(d, f)
          dir_distort_files[os.path.basename(file_path)] = file_path

      targets = []
      for label_file, ref_file in zip(dir_label_files, dir_ref_files):
        assert os.path.basename(ref_file)[:-4] == os.path.basename(label_file)[:-4]
        with open(label_file) as fp:
          for line in fp:
            name, label = line.split(',')
            targets.append((ref_file, dir_distort_files[name], float(label)))

    elif phase == tw.phase.test:

      dir_ref = os.path.join(path, 'Ref')
      dir_distort = os.path.join(path, 'Dis')
      assert os.path.exists(dir_ref) and os.path.exists(dir_distort)

      targets = []
      for f in sorted(os.listdir(dir_distort)):
        ref = f[:5] + '.bmp'
        distort_file = os.path.join(dir_distort, f)
        ref_file = os.path.join(dir_ref, ref)
        assert os.path.exists(distort_file) and os.path.exists(ref_file), f"{distort_file}, {ref_file}"
        targets.append((ref_file, distort_file))

    else:
      raise NotImplementedError

    self.phase = phase
    self.targets = targets
    self.transform = transform
    self.blind_mode = blind_mode
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    distort_meta = T.ImageMeta(path=self.targets[idx][1], source=T.COLORSPACE.BGR)
    if self.phase == tw.phase.train:
      distort_meta.label = self.targets[idx][2]
    if self.blind_mode:
      return self.transform([distort_meta.load().numpy()])
    return self.transform([img_meta.load().numpy(), distort_meta.load().numpy()])


#!<-----------------------------------------------------------------------------
#!< TID 2013
#!<-----------------------------------------------------------------------------

class HTID(torch.utils.data.Dataset):

  """HTID test image database for verification of no-reference image visual quality metrics

      The database contains 2880 color images of size 1536x1024 pixels cropped from
    the real-life photos produced by the mobile phone cameras with various shooting
    and post-processing settings. Mean opinion scores (MOS) for images of the database
    are provided.

      Zipped archive: htid.zip (7 Gb) includes test images and "htid.mat" file which
    contains "h_names.mat" with images file names and "h_mos.mat" with mean opinion
    scores.
  """
  pass


class TID2013(torch.utils.data.Dataset):

  """http://www.ponomarenko.info/tid2013.htm

      The TID2013 contains 25 reference images and 3000 distorted images (25
    reference images x 24 types of distortions x 5 levels of distortions). Reference
    images are obtained by cropping from Kodak Lossless True Color Image Suite.
    All images are saved in database in Bitmap format without any compression.
    File names are organized in such a manner that they indicate a number of the
    reference image, then a number of distortion's type, and, finally, a number
    of distortion's level: "iXX_YY_Z.bmp".

      The file "mos.txt" contains the Mean Opinion Score for each distorted image.
    The MOS was obtained from the results of 971 experiments carried out by observers
    from five countries: Finland, France, Italy, Ukraine and USA (116 experiments
    have been carried out in Finland, 72 in France, 80 in Italy, 602 in Ukraine,
    and 101 in USA). Total, the 971 observers have performed 524340 comparisons
    of visual quality of distorted images or 1048680 evaluations of relative visual
    quality in image pairs. Higer value of MOS (0 - minimal, 9 - maximal, MSE of
    each score is 0.018) corresponds to higer visual quality of the image.

      download: https://webpages.tuni.fi/imaging/htid/htid.zip

      N       Type of distortion

      1       Additive Gaussian noise
      2       Additive noise in color components is more intensive than additive noise in the luminance component
      3       Spatially correlated noise
      4       Masked noise
      5       High frequency noise
      6       Impulse noise
      7       Quantization noise
      8       Gaussian blur
      9       Image denoising
      10      JPEG compression
      11      JPEG2000 compression
      12      JPEG transmission errors
      13      JPEG2000 transmission errors
      14      Non eccentricity pattern noise
      15      Local block-wise distortions of different intensity
      16      Mean shift (intensity shift)
      17      Contrast change
      18      Change of color saturation
      19      Multiplicative Gaussian noise
      20      Comfort noise
      21      Lossy compression of noisy images
      22      Image color quantization with dither
      23      Chromatic aberrations
      24      Sparse sampling and reconstruction

  """

  def __init__(self, path, transform, split=None, blind_mode=False, **kwargs):
    """TID2013 dataset

    Args:
        path ([type]): path to mos_with_names.txt
        transform ([type]): [description]
        split (tuple, optional): [description]. Defaults to (0, 25).
        phase ([type], optional): [description]. Defaults to tw.phase.train.
    """
    tw.fs.raise_path_not_exist(path)
    assert os.path.basename(path) == 'mos_with_names.txt'
    root = os.path.dirname(os.path.abspath(path))

    targets = []
    with open(path) as fp:
      for line in fp:
        label, name = line.replace('\n', '').split(' ')
        ref = name[:3] + '.bmp'
        if split is not None:
          if int(name[1:3]) not in split:
            continue
        ref_path = os.path.join(root, ref.lower())
        if not os.path.exists(ref_path):
          ref_path = os.path.join(root, ref.upper())
        distort_path = os.path.join(root, name)
        assert os.path.exists(ref_path), f"{ref_path}"
        assert os.path.exists(distort_path), f"{distort_path}"
        targets.append([ref_path, distort_path, float(label)])

    self.targets = targets
    self.transform = transform
    self.blind_mode = blind_mode
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    distort_meta = T.ImageMeta(path=self.targets[idx][1], source=T.COLORSPACE.BGR)
    distort_meta.label = self.targets[idx][2]
    if self.blind_mode:
      return self.transform([distort_meta.load().numpy()])
    return self.transform([img_meta.load().numpy(), distort_meta.load().numpy()])


class CSIQ(torch.utils.data.Dataset):

  """CSIQ dataset (full reference) with 866 distort and 30 reference.
  """

  def __init__(self, path, transform, phase=tw.phase.train, split=None, blind_mode=False, **kwargs):
    tw.fs.raise_path_not_exist(path)
    res, _ = tw.parser.parse_from_text(path, (str, str, int, float, float), (True, True, False, False, False))

    refs = {v: k for k, v in enumerate(sorted(set(res[0])))}
    targets = []
    for ref, distort, level, dmos_std, dmos in zip(*res):
      if split is not None:
        if refs[ref] not in split:
          continue
      targets.append((ref, distort, dmos))

    self.targets = targets
    self.transform = transform
    self.blind_mode = blind_mode
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    distort_meta = T.ImageMeta(path=self.targets[idx][1], source=T.COLORSPACE.BGR)
    distort_meta.label = self.targets[idx][2]
    if self.blind_mode:
      return self.transform([distort_meta.load().numpy()])
    return self.transform([img_meta.load().numpy(), distort_meta.load().numpy()])


class KonIQ10k(torch.utils.data.Dataset):
  """KonIQ10K dataset:

    path
    ├── 1024x768/
    ├── 512x384/
    ├── koniq10k_distributions_sets.csv
    ├── koniq10k_indicators.csv
    └── koniq10k_scores_and_distributions.csv

    train split: [0, 8058)
    test split: [8058, 10073)

  """

  def __init__(self, path, transform, phase=tw.phase.train, **kwargs):
    tw.fs.raise_path_not_exist(path)
    assert os.path.basename(path) == 'koniq10k_scores_and_distributions.csv'
    root = os.path.dirname(os.path.abspath(path))

    targets = []
    fp = open(path)
    for i, line in enumerate(fp):
      if i == 0:
        continue
      image_name, c1, c2, c3, c4, c5, c_total, mos, sd, mos_zscore = line.replace('\n', '').split(',')
      img_path = os.path.join(root, '512x384', image_name.replace('"', ''))
      assert os.path.exists(img_path), f'{img_path} failed to find.'
      targets.append((img_path, float(mos_zscore)))
    fp.close()

    if phase == tw.phase.train:
      targets = targets[:8058]
    elif phase == tw.phase.val:
      targets = targets[8058: 10073]
    elif phase == tw.phase.test:
      targets = targets[8058: 10073]
    else:
      raise NotImplementedError(phase)

    self.targets = targets
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    img_meta.label = self.targets[idx][1]
    return self.transform([img_meta.load().numpy()])


class SPAQ(torch.utils.data.Dataset):

  """Reference:

    Y. Fang et al., "Perceptual Quality Assessment of Smartphone Photography"
    in IEEE Conference on Computer Vision and Pattern Recognition, 2020

  File Strcture:
    SPAQ:
      - Annotations()
        - MOS_and_Image_attribute_scores.csv (from MOS and Image attribute scores.xlsx)
      - TestImage(11125)
        - 00001.png
        - 00002.png
        - ...

  Attribution:
    Image name, MOS, Brightness, Colorfulness, Contrast, Noisiness, Sharpness

  """

  def __init__(self, path, transform, phase=tw.phase.train, **kwargs):
    tw.fs.raise_path_not_exist(path)
    protocal = os.path.join(path, 'Annotations', 'MOS_and_Image_attribute_scores.csv')
    root = os.path.join(path, 'TestImage')
    assert os.path.exists(protocal) and os.path.exists(root)

    targets = []
    fp = open(protocal)
    for i, line in enumerate(fp):
      if i == 0:
        continue
      image_name, mos, brightness, colorfulness, contrast, noisiness, sharpness = line.replace('\n', '').split(',')
      img_path = os.path.join(root, image_name)
      assert os.path.exists(img_path), f'{img_path} failed to find.'
      targets.append((img_path,
                      float(mos),
                      float(brightness),
                      float(colorfulness),
                      float(contrast),
                      float(noisiness),
                      float(sharpness)))
    fp.close()

    if phase == tw.phase.train:
      targets = targets[:9125]
    elif phase == tw.phase.val:
      targets = targets[9125:]
    elif phase == tw.phase.test:
      targets = targets[9125:]
    else:
      raise NotImplementedError(phase)

    self.targets = targets
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    img_meta.label = self.targets[idx][1]
    img_meta.caption = np.array(self.targets[idx][1:])
    return self.transform([img_meta.load().numpy()])


class LIVEC(torch.utils.data.Dataset):

  """The LIVE In the Wild Image Quality Challenge Database contains 1,162 images
    impaired by a wide variety of randomly occurring distortions and genuine capture
    artifacts that were obtained using a wide-variety of contemporary mobile camera
    devices including smartphones and tablets. We gathered numerous "authentically"
    distorted images taken by many dozens of casual international users, containing
    diverse distortion types, mixtures, and severities. The images were collected
    without artificially introducing any distortions beyond those occurring during
    capture, processing, and storage.

      Since these images are authentically distorted, they usually contain mixtures
    of multiple impairments that defy categorization into "distortion types." Such
    images are encountered in the real world and reflect a broad range of difficult
    to describe (or pigeon-hole) composite image impairments.

    1. AllImages_release.mat : Contains the names of all the 1169 images that
      are part of this database (1162 test images + 7 training images).

    2. AllMOS_release.mat : This file has the mean opinion scores (MOS)
      corresponding to each of the 1169 images. These values are presented in
      the same order as the images in AllImages_release.mat

    3. AllStdDev_release.mat : This file has the standard deviation obtained on
      the raw opinion scores obtained from a large number of subjects on each image.
      These values correspond to the images in AllImages_release.mat in the same order.

  """

  def __init__(self, root, transform, split=None, **kwargs):
    tw.fs.raise_path_not_exist(root)

    imgpath = scipy.io.loadmat(os.path.join(root, 'Data', 'AllImages_release.mat'))
    imgpath = imgpath['AllImages_release']
    imgpath = imgpath[7:1169]

    mos = scipy.io.loadmat(os.path.join(root, 'Data', 'AllMOS_release.mat'))
    labels = mos['AllMOS_release'].astype(np.float32)
    labels = labels[0][7:1169]

    targets = []
    for i, label in enumerate(labels):
      targets.append((os.path.join(root, 'Images', imgpath[i][0][0]), label))

    if split is not None:
      targets = [targets[i] for i in split]

    self.targets = targets
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    meta.label = self.targets[idx][1]
    return self.transform([meta.load().numpy()])


class LIVE2005(torch.utils.data.Dataset):

  """Twenty-nine high-resolution 24-bits/pixel RGB color images
    (typically 768 X 512) were distorted using five distortion
    types: JPEG2000, JPEG, white noise in the RGB components, Gaussian
    blur, and transmission errors in the JPEG2000 bit stream using a
    fast-fading Rayleigh channel model. A database was derived from
    the $29$ images such that each image had test versions with each
    distortion type, and for each distortion type the perceptual
    quality roughly covered the entire quality range. Observers were
    asked to provide their perception of quality on a continuous
    linear scale that was divided into five equal regions marked with
    adjectives ``Bad", ``Poor", ``Fair", ``Good" and ``Excellent".
    About 20-29 human observers rated each image. Each distortion type
    was evaluated by different subjects in different experiments using
    the same equipment and viewing conditions. In this way a total of
    982 images, out of which 203 were the reference images, were
    evaluated by human subjects in seven experiments. The raw scores
    for each subject were converted to difference scores (between
    the test and the reference) and then Z-scores and
    then scaled and shifted to the full range (1 to 100). Finally, a
    Difference Mean Opinion Score (DMOS) value for each distorted image
    was computed.

  """

  def __init__(self, root, transform, split=None, blind_mode=False, **kwargs):
    tw.fs.raise_path_not_exist(root)

    files = []
    for folder, num in [('jp2k', 227), ('jpeg', 233), ('wn', 174), ('gblur', 174), ('fastfading', 174)]:
      for i in range(num):
        path = '%s%s%s' % ('img', str(i + 1), '.bmp')
        path = os.path.join(root, folder, path)
        files.append(path)

    refpath = os.path.join(root, 'refimgs')
    refnames = os.listdir(refpath)

    dmos = scipy.io.loadmat(os.path.join(root, 'dmos_realigned.mat'))
    labels = dmos['dmos_new'].astype(np.float32)

    orgs = dmos['orgs']
    refnames_all = scipy.io.loadmat(os.path.join(root, 'refnames_all.mat'))
    refnames_all = refnames_all['refnames_all']

    if split is not None:
      # assert split[0] >= 0 and split[1] <= 29
      refnames = [refnames[i] for i in split]

    targets = []
    for i, name in enumerate(refnames):
      sel = refnames[i] == refnames_all
      sel = sel * ~orgs.astype(np.bool)
      sel = np.where(sel == True)
      sel = sel[1].tolist()
      gt_path = os.path.join(refpath, refnames[i])
      for item in sel:
        targets.append((gt_path, files[item], labels[0][item]))

    self.blind_mode = blind_mode
    self.targets = targets
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    distort_meta = T.ImageMeta(path=self.targets[idx][1], source=T.COLORSPACE.BGR)
    distort_meta.label = self.targets[idx][2]
    if self.blind_mode:
      return self.transform([distort_meta.load().numpy()])
    return self.transform([img_meta.load().numpy(), distort_meta.load().numpy()])


class LIVEMD(torch.utils.data.Dataset):

  """This database contains images and results from a subjective study conducted
    at the Laboratory for Image and Video Engineering, The University of Texas at Austin,
    described in: Dinesh Jayaraman, Anish Mittal, Anush K. Moorthy and Alan C. Bovik,
    "Objective Image Quality Assessment of Multiply Distorted Images", Proceedings
    of Asilomar Conference on Signals, Systems and Computers, 2012. The study was
    conducted in two parts. Part 1 deals with blur followed by JPEG, and part 2 with
    blur followed by noise.

    -> 15 reference, 405 distort

  """

  def __init__(self, root, transform, split=None, blind_mode=False, **kwargs):
    tw.fs.raise_path_not_exist(root)
    targets = []

    # part1
    images = scipy.io.loadmat(os.path.join(root, 'Part 1/Imagelists.mat'))
    scores = scipy.io.loadmat(os.path.join(root, 'Part 1/Scores.mat'))

    # series
    refs = set()
    for refimg in images['refimgs']:
      refs.add(refimg[0].tolist()[0])
    refs = OrderedDict({v: k for k, v in enumerate(sorted(list(refs)))})

    # add part1
    for ref_id, img_name, zscore in zip(images['ref4dist'], images['distimgs'], scores['Zscores'][0]):
      ref = images['refimgs'][ref_id - 1][0].tolist()[0][0]
      img_name = img_name[0].tolist()[0]
      if split is not None and refs[ref] not in split:
        continue
      ref_path = os.path.join(root, 'Part 1', 'blurjpeg', ref)
      img_path = os.path.join(root, 'Part 1', 'blurjpeg', img_name)
      if ref == img_name:
        continue
      assert os.path.exists(ref_path), f'{ref_path}'
      assert os.path.exists(img_path), f'{img_path}'
      targets.append((ref_path, img_path, zscore))

    # part2
    images = scipy.io.loadmat(os.path.join(root, 'Part 2/Imagelists.mat'))
    scores = scipy.io.loadmat(os.path.join(root, 'Part 2/Scores.mat'))

    # add part2
    for ref_id, img_name, zscore in zip(images['ref4dist'], images['distimgs'], scores['Zscores'][0]):
      ref = images['refimgs'][ref_id - 1][0].tolist()[0][0]
      img_name = img_name[0].tolist()[0]
      if split is not None and refs[ref] not in split:
        continue
      ref_path = os.path.join(root, 'Part 2', 'blurnoise', ref)
      img_path = os.path.join(root, 'Part 2', 'blurnoise', img_name)
      if ref == img_name:
        continue
      assert os.path.exists(ref_path), f'{ref_path}'
      assert os.path.exists(img_path), f'{img_path}'
      targets.append((ref_path, img_path, zscore))

    self.blind_mode = blind_mode
    self.targets = targets
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    distort_meta = T.ImageMeta(path=self.targets[idx][1], source=T.COLORSPACE.BGR)
    distort_meta.label = self.targets[idx][2]
    if self.blind_mode:
      return self.transform([distort_meta.load().numpy()])
    return self.transform([img_meta.load().numpy(), distort_meta.load().numpy()])


class LIVEVideo(torch.utils.data.Dataset):

  def __init__(self, path, transform, split=(0, 200), phase=tw.phase.train, **kwargs):
    tw.fs.raise_path_not_exist(path)

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    distort_meta = T.ImageMeta(path=self.targets[idx][1], source=T.COLORSPACE.BGR)
    if self.phase == tw.phase.train:
      img_meta.label = self.targets[idx][2]
    return self.transform([img_meta.load().numpy(), distort_meta.load().numpy()])


class FLIVE(torch.utils.data.Dataset):

  """FLIVE datasets (39807 pairs)
  """

  def __init__(self, path, transform, phase=tw.phase.train, **kwargs):
    tw.fs.raise_path_not_exist(path)

    targets = []
    with open(path) as fp:
      for i, line in enumerate(fp):
        if i == 0:
          continue
        v = line.split(',')

        # parse patches
        p1_mos, p1_y1, p1_x1, p1_y2, p1_x2 = float(v[2]), int(v[6]), int(v[7]), int(v[8]), int(v[9])
        p2_mos, p2_y1, p2_x1, p2_y2, p2_x2 = float(v[10]), int(v[13]), int(v[14]), int(v[15]), int(v[16])
        p3_mos, p3_y1, p3_x1, p3_y2, p3_x2 = float(v[17]), int(v[20]), int(v[21]), int(v[22]), int(v[23])
        name, mos, img_h, img_w = v[25], float(v[24]), int(v[30]), int(v[31])
        is_val = False if v[35] == 'False' else True
        img_path = os.path.join(os.path.dirname(path), 'database', name)
        assert os.path.exists(img_path), f'{img_path} vs {name}'

        if phase == tw.phase.train:
          if is_val:
            continue
          if img_h > 640 or img_w > 640:
            continue
        elif phase == tw.phase.val:
          if not is_val:
            continue
          if img_h > 640 or img_w > 640:
            continue
        elif phase == tw.phase.test:
          if img_h <= 640 and img_w <= 640:
            continue
        else:
          raise NotImplementedError(phase.value)

        # inject into metas
        img_meta = T.ImageMeta(path=img_path)
        img_meta.label = mos
        box_meta = T.BoxListMeta()
        box_meta.set_affine_size(max_h=int(v[30]), max_w=int(v[31]))
        box_meta.add(p1_x1, p1_y1, p1_x2, p1_y2, label=p1_mos)
        box_meta.add(p2_x1, p2_y1, p2_x2, p2_y2, label=p2_mos)
        box_meta.add(p3_x1, p3_y1, p3_x2, p3_y2, label=p3_mos)
        targets.append([img_meta, box_meta.numpy()])

    self.targets = targets
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta, box_meta = copy.deepcopy(self.targets[idx])
    img_meta.load().numpy()
    if len(img_meta.bin.shape) == 2:
      img_meta.bin = np.stack([img_meta.bin, img_meta.bin, img_meta.bin], axis=2)
    return self.transform([img_meta, box_meta])


class VQA_III(torch.utils.data.Dataset):

  """VQA_III datasets
  """

  def __init__(self, path, transform, phase=tw.phase.train, **kwargs):
    tw.fs.raise_path_not_exist(path)

    targets = []
    with open(path) as fp:
      for i, line in enumerate(fp):
        if i == 0:
          continue
        res = line.replace('\n', '').split(',')
        mean, img_path = res[0], res[-1]
        # assert os.path.exists(img_path), f'{img_path} failed to find.'
        targets.append((img_path, float(mean)))

    if phase == tw.phase.train:
      targets = targets[2000:]
    elif phase == tw.phase.val:
      targets = targets[:2000]
    elif phase == tw.phase.test:
      targets = targets[:2000]
    else:
      raise NotImplementedError(phase)

    self.targets = targets
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    img_meta.label = self.targets[idx][1]
    return self.transform([img_meta.load().numpy()])
