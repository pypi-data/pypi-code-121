import numpy as np
import cv2

class ImUtil():
    def __init__(self, dataset_desc, class_dictionary):

        if not type(dataset_desc) is dict:
            raise TypeError('{} {} dataset_desc must be dictionary'.format(__file__, __name__))

        self.dataset_desc = dataset_desc

        if not type(class_dictionary) is dict:
            raise TypeError('{} {} class_dictionary must be dictionary'.format(__file__, __name__))

        if 'objects' not in class_dictionary:
            raise TypeError('{} {} class_dictionary["objects"] undefined'.format(__file__, __name__))

        if 'background' not in class_dictionary:
            raise TypeError('{} {} class_dictionary["background"] undefined'.format(__file__, __name__))

        self.class_dictionary = class_dictionary
        self.CreateLut()

    def isGrayscale(self):
        if 'image_colorspace' in self.dataset_desc:
            color_str = self.dataset_desc['image_colorspace']
            if color_str.lower() == 'grayscale':
                return True
        return False

    def CreateLut(self):
        self.lut = np.zeros([256,3], dtype=np.uint8)
        for obj in self.class_dictionary ['objects']: # Load RGB colors as BGR
            self.lut[obj['trainId']][0] = obj['color'][2]
            self.lut[obj['trainId']][1] = obj['color'][1]
            self.lut[obj['trainId']][2] = obj['color'][0]
        self.lut = self.lut.astype(float) * 1/255. # scale colors 0-1
        self.lut[self.class_dictionary ['background']] = [1.0,1.0,1.0] # Pass Through

    # Display functions
    def ColorizeAnnotation(self, ann):
        annrgb = [cv2.LUT(ann, self.lut[:, i]) for i in range(3)]
        annrgb = np.dstack(annrgb) 
        return annrgb

    def MergeIman(self, img, ann, mean=None, stDev = None):
        if mean is not None and stDev is not None:
            img = (img*stDev) + mean

        if self.class_dictionary is not None:
            ann = self.ColorizeAnnotation(ann)

        if self.isGrayscale():
            img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        img = (img*ann).astype(np.uint8)
        return img

    def DisplayImAn(self, img, ann, seg, mean, stdev):

        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        iman = self.MergeIman(img, ann, mean, stdev)
        imseg = self.MergeIman(img, seg, mean, stdev)

        iman = cv2.putText(iman, 'Segmentation',(10,25), font, 1,(255,255,255),1,cv2.LINE_AA)
        imseg = cv2.putText(imseg, 'TensorRT',(10,25), font, 1,(255,255,255),1,cv2.LINE_AA)

        im = cv2.hconcat([iman, imseg])
        return im

class ImTransform():
    def __init__(self, 
        height=640, 
        width=640, 
        normalize=True, 
        enable_transform=True, 
        flipX=True, 
        flipY=False, 
        rotate=3, 
        scale_min=0.75, 
        scale_max=1.25, 
        offset=0.1,
        astype='float32',
        borderType=cv2.BORDER_CONSTANT,
        borderValue=0
    ):
        self.height = height
        self.width = width

        self.normalize = normalize
        self.enable_transform = enable_transform
        self.flipX = flipX
        self.flipY = flipY
        self.rotate = rotate
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.offset = offset
        self.astype = astype
        self.borderType = borderType
        self.borderValue = borderValue



    # Expect img.shape[0]==ann.shape[0] and ann.shape[0]==ann.shape[0]
    def random_resize_crop_or_pad(self, img, ann):
        imgMean = None
        imgStd = None
        imgtype = img.dtype.name
        if self.normalize:
            imgMean = np.mean(img)
            imgStd = np.std(img)
            if imgStd > 0.0:
                img = (img - imgMean)/imgStd
            else:
                print('ImagesDataset.random_resize_crop_or_pad: imgStd is 0.0')
        
        if self.astype is not None:
            img = img.astype(self.astype)
        elif img.dtype.name is not  imgtype:
            img = img.astype(imgtype)

        height = img.shape[0]
        width = img.shape[1]
        
        # Pad
        pad = False
        top=0
        bottom=0
        left=0
        right=0
        if self.height > height:
            bottom = int((self.height-height)/2)
            top = self.height-height-bottom
            pad = True
        if self.width > width:
            right = int((self.width-width)/2)
            left = self.width-width-right
            pad = True

        if pad:
            img = cv2.copyMakeBorder(img, top, bottom, left, right, self.borderType, None, self.borderValue)
            ann = cv2.copyMakeBorder(ann, top, bottom, left, right, self.borderType, None, self.borderValue)

        # Transform
        if self.enable_transform:
                height, width = img.shape[:2]

                matFlip = np.identity(3)
                if self.flipX and np.random.choice(np.array([True, False])):
                    matFlip[0,0] *= -1.0
                    matFlip[0,2] += width-1
                if self.flipY and np.random.choice(np.array([True, False])):
                    matFlip[1,1] *= -1.0
                    matFlip[1,2] += height-1

                scale = np.random.uniform(self.scale_min, self.scale_max)
                angle = np.random.uniform(-self.rotate, self.rotate)
                offsetX = width*np.random.uniform(-self.offset, self.offset)
                offsetY = height*np.random.uniform(-self.offset, self.offset)
                center = (width/2.0 + offsetX, height/2.0 + offsetY)
                matRot = cv2.getRotationMatrix2D(center, angle, scale)
                matRot = np.append(matRot, [[0,0,1]],axis= 0)

                mat = np.matmul(matFlip, matRot)
                mat = mat[0:2]


                img = cv2.warpAffine(src=img, M=mat, dsize=(width, height))
                ann = cv2.warpAffine(src=ann, M=mat, dsize=(width, height))

        # Crop
        height = img.shape[0]
        width = img.shape[1]
        maxX = width - self.width
        maxY = height - self.height

        crop = False
        startX = 0
        startY = 0
        if maxX > 0:
            startX = np.random.randint(0, maxX)
            crop = True
        if  maxY > 0:
            startY = np.random.randint(0, maxY)
            crop = True
        if crop:

            img = img[startY:startY+self.height, startX:startX+self.width]
            ann = ann[startY:startY+self.height, startX:startX+self.width]

        return img, ann, imgMean, imgStd