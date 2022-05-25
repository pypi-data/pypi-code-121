import os
import torch.nn.functional as F
import torchvision.transforms as transforms
import torch
import warnings

class coco():

    def __init__(self,base=0,window=1,imgs='val2017',p='/nas/softechict-nas-2/datasets/coco'):


        self.p,self.base,self.window=p,base,window
        self.name='coco'
        #self.img_dir = os.path.join(self.p, 'JPEGImages/')
        #self.ann_dir = os.path.join(self.p, 'Annotations')
        #self.img = os.path.join(self.p, 'ImageSets', 'Main')
        self.labels = os.path.join(self.p, 'annotations', 'instances_val2017.json')
        self.p = os.path.join(self.p, 'val2017')

        self.load_data()
        self.img_list = {k: v for k, v in enumerate(sorted(self.images_dict.keys(), \
            key=lambda x:int(x[:-4])))}

        if len(self.img_list) == 0:
            raise ValueError(f'Empty dataset')
        elif len(self.img_list) < self.window:
            warnings.warn(f'Dataset length lower than window ({len(self.img_list)} < {self.window})')

        self.labs = self.list_image_sets()
        self.GT = {el[1]: f'{el[1]} {self.list_image_sets()[int(el[0]) % 80]}' for el in self.img_list.items()}


        pass

    def list_image_sets(self):

        """
        List all the image sets from Pascal VOC. Don't bother computing
        this on the fly, just remember it. It's faster.
        """
        return [
                'person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train',
                'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
                'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
                'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
                'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
                'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
                'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
                'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
                'hot dog', 'pizza', 'donut', 'cake', 'chair', 'sofa', 'pottedplant', 'bed',
                'diningtable', 'toilet', 'tvmonitor', 'laptop', 'mouse', 'remote',
                'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
                'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
                'hair drier', 'toothbrush',
            ]

    def load_data(self, cat='val'):

        assert cat in ['train','val','trainval'], \
            'cat must be train, val or trainval'

        self.images_dict = dict()
        #with open(self.labels, mode='r') as f:
        #    js = json.load(f)
        #anno = js['annotations'][self.base:self.base+self.window]

        #for i in range(len(anno)):
        #    img = (str(anno[i]['image_id'])+'.jpg').zfill(16)
        #    if img in os.listdir(self.p):
        #        self.images_dict[img]=anno[i]['category_id']

        for img in os.listdir(self.p)[self.base:self.base + self.window]:
            self.images_dict[img] = 1




    def train_model(self, model, yr=2012):
        import torchray.utils

    def get_img_number(self,img):
        return str(img)


    def transform(self,size=224,normalize=True):
        bgr_mean = [103.939, 116.779, 123.68]

        mean = [m / 255. for m in reversed(bgr_mean)]
        std = [1 / 255.] * 3

        # Note: image should always be downsampled. If image is being
        # upsampled, then this resize function will not match the behavior
        # of skimage.transform.resize in "constant" mode
        # (torch.nn.functional.interpolate uses "edge" padding).
        def resize(x):
            if not isinstance(size, int):
                orig_height, orig_width = size
            else:
                height, width = x.shape[1:3]
                if width < height:
                    orig_width = size
                    orig_height = int(size * height / width)
                else:
                    orig_height = size
                    orig_width = int(size * width / height)
            with torch.no_grad():
                x = F.interpolate(x.unsqueeze(0), (orig_height, orig_width),
                                  mode='bilinear', align_corners=False)
                x = x.squeeze(0)
            return x

        # if normalize:
        #     transform = transforms.Compose([
        #         transforms.ToTensor(),
        #         resize,
        #         transforms.Normalize(mean=mean, std=std),
        #     ])
        # else:
        #     transform = transforms.Compose([
        #         transforms.ToTensor(),
        #         resize,
        #     ])
        if normalize:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Resize(size),
                transforms.CenterCrop(size),
                transforms.Normalize(mean=mean, std=std),
            ])
        else:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Resize(size),
                transforms.CenterCrop(size)
            ])

        return transform

    def apply_transform(self,image,normalize=True,size=224):

        tensor=self.transform(size=size,normalize=normalize)(image).unsqueeze(0)
        return tensor

    def denormalize(self,tensor):
        return tensor