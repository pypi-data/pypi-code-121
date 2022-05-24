import os
import re
import zlib
import shutil
import base64
import math
import cv2
import numpy as np
from . import utils
import subprocess

from scipy.spatial.distance import cdist


class Lire:
    """
    Run lire analysis on a file that contains a list of image file names
    """

    @staticmethod
    def analyse(img_list_file, threads=16):
        lire_classpath = ['/data/brand-data/lire/bin/commons-codec-1.9.jar',
                          '/data/brand-data/lire/bin/common-image-3.0.jar',
                          '/data/brand-data/lire/bin/common-io-3.0.jar',
                          '/data/brand-data/lire/bin/common-lang-3.0.jar',
                          '/data/brand-data/lire/bin/imageio-core-3.0.jar',
                          '/data/brand-data/lire/bin/imageio-jpeg-3.0.jar',
                          '/data/brand-data/lire/bin/imageio-metadata-3.0.jar',
                          '/data/brand-data/lire/bin/imageio-tiff-3.0.jar',
                          '/data/brand-data/lire/bin/jhlabs.jar',
                          '/data/brand-data/lire/bin/lire-request-handler.jar']

        lire_cmd = ['/usr/bin/java', '-cp', ':'.join(lire_classpath),
                    'net.semanticmetadata.lire.solr.ParallelSolrIndexer',
                    '-n', str(threads),
                    '-f',
                    '-p',
                    '-y', 'ce,sc',
                    '-i']
        subprocess.check_call(lire_cmd + [img_list_file])

    @staticmethod
    def rename(path):
        for root, dirs, files in os.walk(path):
            lire_files = [f for f in files if f.endswith('_solr.xml')]
            if not len(lire_files):
                continue
            lire_dir = os.path.join(path, os.path.relpath(root, path))
            for lire_file in lire_files:
                lire_rename = re.sub(
                    '\.high\.\w+_solr\.xml', '.lire.xml', lire_file)
                os.rename(os.path.join(lire_dir, lire_file),
                          os.path.join(lire_dir, lire_rename))


class Convert:

    @staticmethod
    def from_gif(img_file, to_ext='png'):
        img_name, img_ext = os.path.splitext(os.path.basename(img_file))

        # gif is not supported by cv2
        # convert it to jpg using imagemagick
        if not img_ext.lower() == '.gif':
            return img_file

        img_dir = os.path.dirname(img_file)
        img_ext = '.%s' % to_ext
        img_converted = os.path.join(img_dir, '%s%s' % (img_name, img_ext))
        convert_exe = utils.which('convert')
        subprocess.call([convert_exe, '-resize',
                         '512x512', img_file, img_converted])
        os.remove(img_file)

        return img_converted

    @staticmethod
    def to_hgh(img_file, img_name, img_ext='png'):
        _, _ext = os.path.splitext(os.path.basename(img_file))

        img_dir = os.path.dirname(img_file)
        img_hgh = os.path.join(img_dir, '%s.%s' % (img_name, img_ext))

        #  monaremlawi
        if os.path.exists(img_hgh):
            return img_hgh

        # transforming whatever image file into img.high.png
        # --------------------------------------------------
        if not _ext == '.%s' % img_ext:  # needs transformation
            if _ext == '.png' and img_ext == 'jpg':
                img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
                if len(img.shape) > 2 and img.shape[2] == 4:
                    img = Generate.remove_transparency(img)
                    cv2.imwrite(img_file, img)
            img = cv2.imread(img_file)
            # some stupid jpegs (mytm) need to be converted from jpeg tp jpeg
            # (grr) using imagemagick
            # convert then try again
            if not type(img) == np.ndarray:
                convert_exe = utils.which('convert')
                subprocess.call([convert_exe,
                                 img_file, 'JPEG:%s' % img_file])
                img = cv2.imread(img_file)

            cv2.imwrite(img_hgh, img)
            # os.remove(img_file)
        else:
            # os.rename(img_file, img_hgh)
            shutil.copy(img_file, img_hgh)
        return img_hgh


class Generate:

    @staticmethod
    def high(img_file):
        img_modified = False

        img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

        if len(img.shape) > 2 and img.shape[2] == 4:
            img = Generate.remove_transparency(img)
            img_modified = True

        # resize but keep the aspect ratio
        if max(img.shape[0], img.shape[1]) > 800:
            r = 800.0 / max(img.shape[0], img.shape[1])
            dim = (int(img.shape[1] * r), int(img.shape[0] * r))
            try:
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                img_modified = True
            except Exception as e:
                pass

        if img_modified:
            cv2.imwrite(img_file, img)

    @staticmethod
    def remove_transparency(source, background_color=255.0):
        source_img = source[:, :, :3]
        base_mask = source[:, :, 3] * (1 / 255.0)
        source_mask = np.dstack([base_mask, base_mask, base_mask])

        background_mask = 1.0 - source_mask
        bg_part = (background_color * (1 / 255.0))
        bg_part = bg_part * background_mask
        bg_fill = (source_img * (1 / 255.0)) * source_mask

        return np.uint8(cv2.addWeighted(bg_part, 255.0, bg_fill, 255.0, 0.0))

    @staticmethod
    def thumbnail(img_file, img_name):
        img_dir = os.path.dirname(img_file)
        img_thm = os.path.join(img_dir, '%s-th.jpg' % img_name)

        #  monaremlawi
        if os.path.exists(img_thm):
            return img_thm

        img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

        # check if image has a transparency layer
        if len(img.shape) > 2 and img.shape[2] == 4:
            img = Generate.remove_transparency(img)

        # resize but keep the aspect ratio
        if max(img.shape[0], img.shape[1]) > 250:
            r = 250.0 / max(img.shape[0], img.shape[1])
            dim = (int(img.shape[1] * r), int(img.shape[0] * r))
            try:
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                cv2.imwrite(img_thm, resized)
            except Exception as e:
                cv2.imwrite(img_thm, img)
        # no resize needed. just convert to jpg
        else:
            cv2.imwrite(img_thm, img)

        return img_thm

    @staticmethod
    def icon(img_file, img_name):
        img_dir = os.path.dirname(img_file)
        img_ico = os.path.join(img_dir, '%s-ic.jpg' % img_name)

        #  monaremlawi
        if os.path.exists(img_ico):
            return img_ico

        img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

        # check if image has a transparency layer
        if len(img.shape) > 2 and img.shape[2] == 4:
            img = Generate.remove_transparency(img)

        # resize but keep the aspect ratio
        if max(img.shape[0], img.shape[1]) > 64:
            target_area = 80 * 80
            aspect_ratio = float(img.shape[1]) / float(img.shape[0])

            # + 5 for some padding
            target_height = int(math.sqrt(target_area / aspect_ratio) + .5) + 5
            # target_width  = int((target_height * aspect_ratio) + .5)

            while img.shape[0] > target_height:
                img = cv2.pyrDown(img)

        try:
            cv2.imwrite(img_ico, img[:, :, :3],
                        [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        # fails to get the 3rd dimesion for some files
        except Exception as e:
            cv2.imwrite(img_ico, img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

        return img_ico


#######################################
def to_base64(img_file):
    encoded_string = ''
    with open(img_file, 'rb') as fh:
        encoded_string = base64.b64encode(fh.read())
    return encoded_string.decode("utf-8")

def get_crc(img_file):
    prev = 0
    fh = open(img_file, 'rb')
    for eachLine in fh:
        prev = zlib.crc32(eachLine, prev)
    fh.close()
    return "%X" % (prev & 0xFFFFFFFF)

#######################################


def _contour_props(contour):
    x1, y1, w, h = cv2.boundingRect(contour)
    x2, y2 = (x1 + w, y1 + h)

    features = cv2.moments(contour)
    area = features['m00']
    if area:
        # centroid
        cx = int(features['m10'] / area)
        cy = int(features['m01'] / area)
    else:
        cx = x1
        cy = y1
    radius = math.sqrt(area/math.pi)

    return (x1, y1), (x2, y2), (w, h), (cx, cy), radius, area


def compress(img):
    png_tool = 'optipng -quiet -o2'
    jpg_tool = 'jpegoptim --quiet'

    _, img_ext = os.path.splitext(img)

    tool = png_tool if img_ext == '.png' else jpg_tool

    cmd = '%s %s' % (tool, img)

    subprocess.check_call(cmd.split(' '))


def crop(img_src, img_dest):
    """
    # return 2  - corrupt image
    # return 1  - faded image
    # return 0  - image cropped
    # return -1 - image does not need cropping
    """
    kernel2 = np.ones((2, 2), np.uint8)

    # load the image and convert it to grayscale
    img = cv2.imread(img_src)
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        return 2

    # erode to connect close dots
    gray = cv2.erode(gray, kernel2, iterations=1)
    # blur and threshold to remove very gray areas
    gray = cv2.GaussianBlur(gray, (71, 71), -1)
    gray = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)[1]

    # get contours and sort by area
    contours = cv2.findContours(gray,
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[0]
    contours = list(contours)
    sorted(contours, key=cv2.contourArea, reverse=True)

    # sometimes the whole image is too faded => do nothing
    if not len(contours):
        return 1

    # take the biggest contour and make it our reference
    ref = contours.pop(0)
    ((ref_x1, ref_y1),
     (ref_x2, ref_y2),
     (ref_w,  ref_h),
     (ref_cx, ref_cy),
     ref_radius, ref_area) = _contour_props(ref)
    ref_area = ref_w * ref_h

    def sort_by_distance(node, nodes):
        distances = cdist([node], nodes, 'euclidean')
        return distances.tolist()[0]

    # sort contours by the distance from ref
    contours_order = []
    if len(contours):
        contours_props = [_contour_props(c) for c in contours]
        contours_cntrs = [c[3] for c in contours_props]
        contours_dstnc = sort_by_distance((ref_cx, ref_cy), contours_cntrs)
        contours_order = [c for _, c in sorted(zip(contours_dstnc,
                                                   range(len(contours))))]

    # loop over other contours (closest to furthest)
    for idx in contours_order:
        cnt = contours[idx]
        cnt_area = cv2.contourArea(cnt)
        # if the area covers less than .3% of total area => ignore
        if float(cnt_area / ref_area) * 100 < .3:
            continue

        ((cnt_x1, cnt_y1),
         (cnt_x2, cnt_y2),
         (cnt_w,  cnt_h),
         (cnt_cx, cnt_cy),
         cnt_radius, cnt_area) = contours_props[idx]

        # calculate the distance between the 2 contours
        dist = math.sqrt(
            (math.fabs(cnt_cx - ref_cx))**2 + (math.fabs(cnt_cy - ref_cy))**2)

        # decide whether to keep or dismiss contour
        # as a function of distance and size
        if dist - 2*math.pi*cnt_radius > dist:
            continue
        if dist - ref_radius - cnt_radius > cnt_radius**2:
            continue

        # keeping the area

        # calculate bounding points
        tl = (min(ref_x1, cnt_x1), min(ref_y1, cnt_y1))
        tr = (max(ref_x2, cnt_x2), min(ref_y1, cnt_y1))
        bl = (min(ref_x1, cnt_x1), max(ref_y2, cnt_y2))
        br = (max(ref_x2, cnt_x2), max(ref_y2, cnt_y2))

        # update the ref properties
        ref_x1, ref_y1 = tl
        ref_w, ref_h = (tr[0] - tl[0], br[1] - tr[1])
        ref_x2, ref_y2 = (ref_x1 + ref_w, ref_y1 + ref_h)
        ref_cx, ref_cy = (ref_x1 + ref_w/2, ref_y1 + ref_h/2)
        ref_area = ref_area + cnt_area
        ref_radius = ref_radius + cnt_radius

    crop_shape = (ref_h, ref_w)

    if crop_shape != (img.shape[0], img.shape[1]):
        cv2.imwrite(img_dest, img[ref_y1:ref_y1+ref_h, ref_x1:ref_x1+ref_w])
        return 0

    return -1
