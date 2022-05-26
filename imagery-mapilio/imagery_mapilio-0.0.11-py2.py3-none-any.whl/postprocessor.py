from typing import Tuple

import numpy as np
import cv2
import random

from calculation.pixel import Pixel

class PostProcessor:

    @staticmethod
    def image_coloring(image: np.ndarray, rgb_mask: list) -> (np.ndarray, np.ndarray):
        """

        :param image: it have processed image
        :param rgb_mask: predicted mask array
        :return:
        """
        image_rgb = image.copy()
        image_white = image.copy()
        for i in range(len(rgb_mask[0])):
            image_rgb[rgb_mask[1][i], rgb_mask[0][i], 0] = 5  # y and x coordinates coloring
            image_rgb[rgb_mask[1][i], rgb_mask[0][i], 2] = 200  # y and x coordinates coloring

        for i in range(len(rgb_mask[0])):
            image_white[rgb_mask[1][i], rgb_mask[0][i], 0] = 255  # y and x coordinates coloring
            image_white[rgb_mask[1][i], rgb_mask[0][i], 1] = 255  # y and x coordinates coloring
            image_white[rgb_mask[1][i], rgb_mask[0][i], 2] = 255  # y and x coordinates coloring

        del image
        return image_white, image_rgb

    @staticmethod
    def vis_bbox(image: np.ndarray, bbox: list, **kwargs) -> np.ndarray:

        """
            Draw bbox,info box on image
        :param image: images to be processed
        :param bbox: [xmin, ymin, xmax, ymax]
        :param kwargs: classname,box,args (string) :custom box for value
        :return: box drawn image
        """

        overlay = image.copy()
        alpha = 0.4  # Transparency factor.
        pixel = 0
        pixel_height = 17
        header_list = []
        header_pix_x = 4
        header_pix_y = 13
        for key, value in kwargs.items():
            text = str(key).capitalize() + ' : ' + str(value)
            x = bbox[0]
            x2 = bbox[2]
            if key == 'classname':
                y, y2 = bbox[1], bbox[1] - 30
                color = (0, 0, 200)
                header_value = (text, (x + header_pix_x, y - header_pix_y))
                header_list.append((text, (x + header_pix_x, y - header_pix_y)))
            elif key == 'box':
                if value:
                    y, y2 = bbox[1], bbox[3]
                    color = (250, 100, 0)
                else:
                    continue
            else:
                y, y2 = bbox[3] + pixel, bbox[3] + pixel_height
                color = (0, 200, 0)
                header_value = (text, (x + header_pix_x, y + header_pix_y + pixel))
                pixel += 8

            header_list.append(header_value)
            cv2.rectangle(overlay, (x, y), (x2, y2), color, -1)
            image_new = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
            pixel_height += 11

        for i in range(len(header_list)):
            cv2.putText(image_new, header_list[i][0], header_list[i][1], cv2.FONT_HERSHEY_DUPLEX, 0.4, (0, 0, 0), 1)

        return image_new

    @staticmethod
    def get_coloured_mask(mask: list) -> np.ndarray:
        """
        random_colour_masks
          parameters:
            - image - predicted masks
          method:
            - the masks of each predicted object is given random colour for visualization
        """
        colours = [[0, 255, 0], [0, 0, 255], [255, 0, 0], [0, 255, 255], [255, 255, 0], [255, 0, 255], [80, 70, 180],
                   [250, 80, 190], [245, 145, 50], [70, 150, 250], [50, 190, 190]]
        r = np.zeros_like(mask).astype(np.uint8)
        g = np.zeros_like(mask).astype(np.uint8)
        b = np.zeros_like(mask).astype(np.uint8)
        r[mask == 1], g[mask == 1], b[mask == 1] = colours[random.randrange(0, 10)]
        coloured_mask = np.stack([r, g, b], axis=2)
        return coloured_mask

    def get_mask_polygon_to_rectangle(mask: list) -> list:
        """

        :return:
        """
        maskx = np.any(mask, axis=0)
        masky = np.any(mask, axis=1)
        xmin = np.argmax(maskx)
        ymin = np.argmax(masky)
        xmax = len(maskx) - np.argmax(maskx[::-1])
        ymax = len(masky) - np.argmax(masky[::-1])

        return [xmin, ymin, xmax, ymax]

    @staticmethod
    def get_segmentation(mask: list, x0: int, y0: int, horizon: int, image: np.ndarray) -> np.ndarray:
        """

        :param mask:
        :param x0:
        :param y0:
        :param horizon:
        :param image:
        :return:
        """
        maskRaw = mask[0]
        mask_ = maskRaw.mul(255).byte().cpu().numpy()
        contours, _ = cv2.findContours(
            mask_.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        if contours:
            contour = np.flip(contours[0], axis=1)
            contour = contour.ravel().tolist()
            segmentation = Pixel.calc_origin(y0, x0, contour, 1, 1, horizon)
            # TODO have a problem i could not solved
            # cv2.drawContours(image, segmentation, -1, (255, 0, 0), 2, cv2.LINE_AA)
            # cv2.imwrite("test2.jpeg", image)

        else:
            segmentation = None

        return segmentation

    # @staticmethod
    # # Deprecated since 07.07.2021
    # def get_histogram_matcher(detect_1: np.ndarray, detect_2: np.ndarray) -> float:
    #     # The histogram size refers to the number of bins in the histogram.
    #     hbins = 180
    #     sbins = 255
    #     hrange = [0, 180]
    #     srange = [0, 256]
    #     ranges = hrange + srange
    #     rows, cols = detect_1.shape[:2]
    #
    #     # Use the 0-th and 1-st channels
    #     channels = [0, 1]
    #
    #     # Calculate the Hist for each images
    #     # Calculate the histogram and normalize it
    #     hist_img1 = cv2.calcHist([detect_1], channels, None, [256], [0, 256], accumulate=False)
    #     # cv2.normalize(hist_img1, hist_img1, alpha=0, beta=None, norm_type=cv2.NORM_L1)
    #     hist_img2 = cv2.calcHist([detect_2], channels, None, [256], [0, 256], accumulate=False)
    #     # cv2.normalize(hist_img2, hist_img2, alpha=0, beta=None, norm_type=cv2.NORM_L1)
    #
    #     # find the metric value
    #     metric_val = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_BHATTACHARYYA)
    #     del hist_img1, hist_img2
    #
    #     return metric_val

    @staticmethod
    def calc_color_histogram_similarity(img1: np.ndarray, img2: np.ndarray) -> float:

        h_b1, h_g1, h_r1 = calc_rgb_histogram(img1)
        h_b2, h_g2, h_r2 = calc_rgb_histogram(img2)

        bSimilarity = cv2.compareHist(h_b1, h_b2, cv2.HISTCMP_CORREL)
        gSimilarity = cv2.compareHist(h_g1, h_g2, cv2.HISTCMP_CORREL)
        rSimilarity = cv2.compareHist(h_r1, h_r2, cv2.HISTCMP_CORREL)

        return (bSimilarity + gSimilarity + rSimilarity) / 3.0

    @staticmethod
    def mask_to_polygons(mask):
        # cv2.RETR_CCOMP flag retrieves all the contours and arranges them to a 2-level
        # hierarchy. External contours (boundary) of the object are placed in hierarchy-1.
        # Internal contours (holes) are placed in hierarchy-2.
        # cv2.CHAIN_APPROX_NONE flag gets vertices of polygons from contours.
        mask = np.ascontiguousarray(mask)  # some versions of cv2 does not support incontiguous arr
        res = cv2.findContours(mask.astype("uint8"), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        hierarchy = res[-1]
        if hierarchy is None:  # empty mask
            return [], False
        has_holes = (hierarchy.reshape(-1, 4)[:, 3] >= 0).sum() > 0
        res = res[-2]
        res = [x.flatten() for x in res]
        # These coordinates from OpenCV are integers in range [0, W-1 or H-1].
        # We add 0.5 to turn them into real-value coordinate space. A better solution
        # would be to first +0.5 and then dilate the returned polygon by 0.5.
        res = [x + 0.5 for x in res if len(x) >= 6]
        return res, has_holes


def calc_rgb_histogram(img: np.ndarray, isNormalized: bool = True) -> Tuple:
    h_b = cv2.calcHist([img], [0], None, [256], [0, 255])
    h_g = cv2.calcHist([img], [1], None, [256], [0, 255])
    h_r = cv2.calcHist([img], [2], None, [256], [0, 255])

    if isNormalized == True:
        cv2.normalize(h_b, h_b, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(h_g, h_g, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(h_r, h_r, 0, 255, cv2.NORM_MINMAX)

    return h_b, h_g, h_r