#!/usr/bin/env python
'''
Created by Seria at 02/11/2018 3:38 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-
import numpy as np
import random as rand
import logging
try:
    import av
    logging.getLogger('libav').setLevel(logging.FATAL)
    # print(av.logging.get_level())
    # print('='*50)
    # av.logging.set_level(av.logging.ERROR)
    # print(av.logging.get_level())
    # print('=' * 50)
except:
    print('NEBULAE WARNING ◘ that PyAV has not been installed properly results in failure of video augmentation.')
from collections import abc
from torchvision.transforms import *
F = functional
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from ..toolkit import byte2arr


__all__ = ('Comburant', 'HWC2CHW', 'Random',
           'NEAREST', 'LINEAR', 'CUBIC', 'HORIZONTAL', 'VERTICAL',
           'Resize', 'Crop', 'Flip', 'Rotate',
           'Brighten', 'Contrast', 'Saturate', 'Hue', 'Blur', 'Sharpen',
           'JPEG', 'PNG', 'MPEG4', 'H264', 'VP9', 'AV1')


NEAREST = 0
LINEAR = 1
CUBIC = 2

PIL_INTERP = {NEAREST: Image.NEAREST, LINEAR: Image.BILINEAR, CUBIC: Image.BICUBIC}

HORIZONTAL = 10
VERTICAL = 11




class Comburant(object):
    def __init__(self, *args, is_encoded=False, interm=False):
        if isinstance(args[-1], HWC2CHW):
            ls_args = list(args[:-1])
            self.cvt_form = args[-1]
        else:
            ls_args = list(args)
        self.comburant = Compose(ls_args)
        self.is_encoded = is_encoded
        self.interm = interm

    def _byte2arr(self, imgs):
        if isinstance(imgs, abc.Sequence):
            arr = []
            for i in imgs:
                arr.append(self._byte2arr(i))
        else:
            arr = byte2arr(imgs, as_np=False)
        return arr

    def _post(self, src):
        if isinstance(src, abc.Sequence):
            dst = []
            for img in src:
                dst.append(self._post(img))
        else:
            src = np.array(src)
            dst = src.astype(np.float32) / 255
            if hasattr(self, 'cvt_form'):
                dst = self.cvt_form(dst)
        return dst

    def __call__(self, imgs):
        if self.is_encoded:
            imgs = self._byte2arr(imgs)
        ret = self.comburant(imgs)
        if not self.interm:
            ret = self._post(ret)
        return ret



class ABC(object):
    def __init__(self):
        pass

    def call(self, *args, **kwargs):
        raise NotImplementedError

    def exec(self, imgs, *args, **kwargs):
        if isinstance(imgs, abc.Sequence):
            ret = []
            if isinstance(imgs[0], abc.Sequence):
                basket = []
                for v in zip(*imgs):
                    basket.append(self.exec(v, *args, **kwargs))
                for r in zip(*basket):
                    ret.append(r)
            else:
                for i in imgs:
                    ret.append(self.call(i, *args, **kwargs))
        else:
            ret = self.call(imgs, *args, **kwargs)

        return ret



class HWC2CHW(object):
    def __init__(self):
        super(HWC2CHW, self).__init__()

    def __call__(self, img):
        return np.transpose(img, (2, 0, 1))



class Random(object):
    def __init__(self, p, comburant):
        super(Random, self).__init__()
        if isinstance(p, (tuple, list)):
            assert len(p)==len(comburant), 'NEBULAE ERROR ⨷ the number of prob does not match with comburants.'
            assert sum(p)==1, 'NEBULAE ERROR ⨷ the sum of probabilities must be 1.'
        self.p = p
        self.cbr = comburant

    def __call__(self, imgs):
        if not isinstance(self.p, (tuple, list)):
            if rand.random() < self.p:
                return self.cbr(imgs)
            else:
                return imgs
        else:
            cbr = np.random.choice(self.cbr, size=1, replace=False, p=self.p)[0]
            return cbr(imgs)



class Void():
    def __init__(self):
        pass

    def __call__(self, imgs):
        return imgs



class Resize(object):
    def __init__(self, size, interp=LINEAR, scale=()):
        # size: (height, width)
        super(Resize, self).__init__()
        self.size = size
        self.interp = interp
        self.scale = scale

    def call(self, img, t=1):
        w = self.size[1] * t
        h = self.size[0] * t
        return img.resize((w, h), PIL_INTERP[self.interp])

    def __call__(self, imgs, _zipped=False):
        if isinstance(imgs, abc.Sequence):
            ret = []
            if isinstance(imgs[0], abc.Sequence):
                basket = []
                for v in zip(*imgs):
                    basket.append(self(v, True))
                for r in zip(*basket):
                    ret.append(r)
            else:
                if _zipped:
                    for i, v in enumerate(imgs):
                        ret.append(self.call(v, self.scale[i]))
                else:
                    for i, v in enumerate(imgs):
                        ret.append(self.call(v))
        else:
            ret = self.call(imgs)

        return ret



class Crop(ABC):
    def __init__(self, size, padding=(0, 0, 0, 0), area_ratio=(1, 1), aspect_ratio=(1, 1), interp=LINEAR, scale=()):
        # size: (height, width)
        # padding: (left, top, right, bottom)
        super(Crop, self).__init__()
        self.size = size
        self.padding = padding
        self.area_ratio = area_ratio
        self.aspect_ratio = aspect_ratio
        self.scale = scale
        if area_ratio == aspect_ratio == (1,1):
            self.reshape = False
            self.comburant = RandomCrop(size)
        else: # firstly crop a patch that meets area and aspect ratio, then resize it to the given size
            self.reshape = True
            self.comburant = RandomResizedCrop(size, area_ratio, aspect_ratio, PIL_INTERP[interp])

    def call(self, img, param, t=1):
        param = [p * t for p in param]
        y, x, h, w = param
        padding = tuple([p * t for p in self.padding])
        size = tuple([s * t for s in self.size])
        img = F.pad(img, padding, 0, 'constant')
        # pad the width if needed
        if img.size[0] < size[1]:
            img = F.pad(img, (size[1] - img.size[0], 0), 0, 'constant')
        # pad the height if needed
        if img.size[1] < size[0]:
            img = F.pad(img, (0, size[0] - img.size[1]), 0, 'constant')

        if self.reshape:
            return F.resized_crop(img, y, x, h, w, size, self.comburant.interpolation)
        else:
            return F.crop(img, y, x, h, w)

    def __call__(self, imgs, p=None, _zipped=False):
        if p is not None:
            param = p
        else:
            if isinstance(imgs, abc.Sequence):
                if isinstance(imgs[0], abc.Sequence):
                    ref = imgs[0][0]
                else:
                    ref = imgs[0]
            else:
                ref = imgs
            ref = F.pad(ref, self.padding, 0, 'constant')
            # pad the width if needed
            if ref.size[0] < self.size[1]:
                ref = F.pad(ref, (self.size[1] - ref.size[0], 0), 0, 'constant')
            # pad the height if needed
            if ref.size[1] < self.size[0]:
                ref = F.pad(ref, (0, self.size[0] - ref.size[1]), 0, 'constant')
            if self.reshape:
                param = self.comburant.get_params(ref, self.comburant.scale, self.comburant.ratio)
            else:
                param = self.comburant.get_params(ref, self.comburant.size)

        if isinstance(imgs, abc.Sequence):
            ret = []
            if isinstance(imgs[0], abc.Sequence):
                basket = []
                for v in zip(*imgs):
                    basket.append(self(v, param, True))
                for r in zip(*basket):
                    ret.append(r)
            else:
                if _zipped:
                    for i, v in enumerate(imgs):
                        ret.append(self.call(v, param, self.scale[i]))
                else:
                    for i, v in enumerate(imgs):
                        ret.append(self.call(v, param))
        else:
            ret = self.call(imgs, param)

        return ret



class Flip(ABC):
    def __init__(self, axial):
        super(Flip, self).__init__()
        if axial == HORIZONTAL:
            self.comburant = RandomVerticalFlip(1)
        elif axial == VERTICAL:
            self.comburant = RandomHorizontalFlip(1)
        else:
            raise Exception('NEBULAE ERROR ⨷ the invoked flip type is not defined or supported.')

    def call(self, img):
        return self.comburant(img)

    def __call__(self, imgs):
        ret = self.exec(imgs)
        return ret



class Rotate(ABC):
    def __init__(self, degree, intact=False, interp=NEAREST):
        '''
        Args
        intact: whether to keep image intact which might enlarge the output size
        '''
        super(Rotate, self).__init__()
        self.comburant = RandomRotation(degree, PIL_INTERP[interp], intact)

    def call(self, img, angle):
        return F.rotate(img, angle, self.comburant.resample, self.comburant.expand,
                        self.comburant.center, self.comburant.fill)

    def __call__(self, imgs):
        angle = self.comburant.get_params(self.comburant.degrees)
        ret = self.exec(imgs, angle)
        return ret



class Brighten(ABC):
    def __init__(self, range):
        super(Brighten, self).__init__()
        self.comburant = ColorJitter(brightness=range)

    def call(self, img, factor):
        return F.adjust_brightness(img, factor)

    def __call__(self, imgs):
        factor = rand.uniform(self.comburant.brightness[0], self.comburant.brightness[1])
        ret = self.exec(imgs, factor)
        return ret



class Contrast(ABC):
    def __init__(self, range):
        super(Contrast, self).__init__()
        self.comburant = ColorJitter(contrast=range)

    def call(self, img, factor):
        return F.adjust_contrast(img, factor)

    def __call__(self, imgs):
        factor = rand.uniform(self.comburant.contrast[0], self.comburant.contrast[1])
        ret = self.exec(imgs, factor)
        return ret



class Saturate(ABC):
    def __init__(self, range):
        super(Saturate, self).__init__()
        self.comburant = ColorJitter(saturation=range)

    def call(self, img, factor):
        return F.adjust_saturation(img, factor)

    def __call__(self, imgs):
        factor = rand.uniform(self.comburant.saturation[0], self.comburant.saturation[1])
        ret = self.exec(imgs, factor)
        return ret



class Hue(ABC):
    def __init__(self, range):
        # hue range: [-0.5, 0.5]
        super(Hue, self).__init__()
        self.comburant = ColorJitter(hue=range)

    def call(self, img, factor):
        return F.adjust_hue(img, factor)

    def __call__(self, imgs):
        factor = rand.uniform(self.comburant.hue[0], self.comburant.hue[1])
        ret = self.exec(imgs, factor)
        return ret



class Blur(ABC):
    def __init__(self, radius):
        super(Blur, self).__init__()
        if isinstance(radius, tuple):
            assert radius[1] >= radius[0], 'NEBULAE ERROR ⨷ the second element should not be less than the first.'
        elif isinstance(radius, int):
            assert radius>0, 'NEBULAE ERROR ⨷ a valid radius should be larger than zero.'
        else:
            raise TypeError('NEBULAE ERROR ⨷ a valid radius should be an integer or a tuple.')
        self.radius = radius

    def call(self, img, r):
        return img.filter(ImageFilter.GaussianBlur(r))

    def __call__(self, imgs):
        if isinstance(self.radius, tuple):
            radius = rand.randint(self.radius[0], self.radius[1])
        else:
            radius = self.radius
        ret = self.exec(imgs, radius)
        return ret


class Sharpen(ABC):
    def __init__(self, factor):
        super(Sharpen, self).__init__()
        if isinstance(factor, tuple):
            assert factor[1] >= factor[0], 'NEBULAE ERROR ⨷ the second element should not be less than the first.'
        elif isinstance(factor, (int, float)):
            assert factor>1, 'NEBULAE ERROR ⨷ a valid factor should be larger than one.'
        else:
            raise TypeError('NEBULAE ERROR ⨷ a valid factor should be an float or a tuple.')
        self.factor = factor

    def call(self, img, factor):
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(factor)

    def __call__(self, imgs):
        if isinstance(self.factor, tuple):
            factor = self.factor[0] + rand.random()*(self.factor[1]-self.factor[0])
        else:
            factor = self.factor
        ret = self.exec(imgs, factor)
        return ret



class JPEG(ABC):
    def __init__(self, quality):
        super(JPEG, self).__init__()
        if isinstance(quality, tuple):
            assert quality[1] >= quality[0], 'NEBULAE ERROR ⨷ the second element should not be less than the first.'
            assert quality[0]>0 and quality[1]<10, 'NEBULAE ERROR ⨷ a valid quality should be an integer within [1, 9].'
        elif isinstance(quality, int):
            assert quality>0 and quality<10, 'NEBULAE ERROR ⨷ a valid quality should be an integer within [1, 9].'
        else:
            raise TypeError('NEBULAE ERROR ⨷ a valid quality should be an integer or a tuple.')
        self.quality = quality

    def call(self, img, qlt):
        buffer = BytesIO()
        img.save(buffer, 'JPEG', quality=qlt)
        return Image.open(buffer)

    def __call__(self, imgs):
        if isinstance(self.quality, tuple):
            qlt = int((rand.uniform(self.quality[0], self.quality[1]) - 1) * 11.75 + 1.1)
        else:
            qlt = self.quality
        ret = self.exec(imgs, qlt)
        return ret



class PNG(ABC):
    def __init__(self, quality):
        super(PNG, self).__init__()
        if isinstance(quality, tuple):
            assert quality[1] >= quality[0], 'NEBULAE ERROR ⨷ the second element should not be less than the first.'
            assert quality[0]>0 and quality[1]<10, 'NEBULAE ERROR ⨷ a valid quality should be an integer within [1, 9].'
        elif isinstance(quality, int):
            assert quality>0 and quality<10, 'NEBULAE ERROR ⨷ a valid quality should be an integer within [1, 9].'
        else:
            raise TypeError('NEBULAE ERROR ⨷ a valid quality should be an integer or a tuple.')
        self.quality = quality

    def call(self, img, qlt):
        buffer = BytesIO()
        img.save(buffer, 'PNG', compress_level=qlt)
        return Image.open(buffer)

    def __call__(self, imgs):
        if isinstance(self.quality, tuple):
            qlt = rand.randint(self.quality[0], self.quality[1])
        else:
            qlt = self.quality
        ret = self.exec(imgs, qlt)
        return ret



def vidEncode(imgs, fps, bitrate, codec):
    buf = BytesIO()
    with av.open(buf, 'w', 'mp4') as container:
        stream = container.add_stream(codec, rate=fps)
        w, h = imgs[0].size
        stream.height = h
        stream.width = w
        stream.pix_fmt = 'yuv420p'
        stream.bit_rate = bitrate

        for img in imgs:
            frame = av.VideoFrame.from_image(img)
            frame.pict_type = 'NONE'
            for packet in stream.encode(frame):
                container.mux(packet)

        # Flush stream
        for packet in stream.encode():
            container.mux(packet)

    outputs = []
    with av.open(buf, 'r', 'mp4') as container:
        if container.streams.video:
            for frame in container.decode(**{'video': 0}):
                outputs.append(frame.to_rgb().to_image())
    return outputs



class VABC(ABC):
    def __init__(self, fps, br):
        super(VABC, self).__init__()
        self.fps = fps
        self.br = br

    def __call__(self, seqs):
        if isinstance(self.fps, tuple):
            fps = rand.randint(self.fps[0], self.fps[1])
        else:
            fps = self.fps
        if isinstance(self.br, tuple):
            br = rand.randint(self.br[0], self.br[1])
        else:
            br = self.br

        if isinstance(seqs[0], abc.Sequence):
            ret = []
            for s in seqs:
                ret.append(self.call(s, fps, br))
        else:
            ret = self.call(seqs, fps, br)

        return ret



class MPEG4(VABC):
    def __init__(self, fps, br):
        super(MPEG4, self).__init__(fps, br)

    def call(self, imgs, fps, br):
        return vidEncode(imgs, fps, br, 'mpeg4')



class H264(VABC):
    def __init__(self, fps, br):
        super(H264, self).__init__(fps, br)

    def call(self, imgs, fps, br):
        return vidEncode(imgs, fps, br, 'h264')



class VP9(VABC):
    def __init__(self, fps, br):
        super(VP9, self).__init__(fps, br)

    def call(self, imgs, fps, br):
        return vidEncode(imgs, fps, br, 'vp9')



class AV1(VABC):
    def __init__(self, fps, br):
        super(AV1, self).__init__(fps, br)

    def call(self, imgs, fps, br):
        return vidEncode(imgs, fps, br, 'av1')



if __name__ == '__main__':
    img = Image.open('/Users/Seria/Desktop/nebulae/test/sing.jpg')
    cbr = Sharpen(2)
    dst = cbr(img)
    dst.save('/Users/Seria/Desktop/nebulae/test/sharp.png', format='PNG', compress_level=0)

    # seq = []
    # lrs = []
    # for i in range(5):
    #     img = Image.open('/Users/Seria/Desktop/nebulae/test/vid/%04d.png'%(i+1))
    #     seq.append(img)
    #     lrs.append(img.resize((img.size[0]//2, img.size[1]//2)))
    # # cbr = AV1(30, 6e5)
    # # dst = cbr(seq)
    # # cbr = Comburant(Crop((128,128), scale=(1,2)))
    # cbr = Comburant(Blur(3), JPEG((7,9)))
    # dst = cbr([lrs, seq])
    # import matplotlib.pyplot as plt
    # for i in range(5):
    #     # dst[i].save('/Users/Seria/Desktop/nebulae/test/30+1e6/%04d.png'%(i+1), format='PNG', compress_level=0)
    #     plt.imsave('/Users/Seria/Desktop/nebulae/test/crop/lr-%04d.png'%(i+1), dst[0][i])
    #     plt.imsave('/Users/Seria/Desktop/nebulae/test/crop/hr-%04d.png'%(i+1), dst[1][i])