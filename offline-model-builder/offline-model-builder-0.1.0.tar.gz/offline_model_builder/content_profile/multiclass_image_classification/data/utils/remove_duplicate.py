import concurrent.futures
import logging
import shutil
import numpy as np
from imutils import paths
import cv2
import tempfile

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")
hashes = {}


def dhash(imagePath, hashSize):
    logging.info("Reading {}".format(imagePath))
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hashSize + 1, hashSize))
    diff = resized[:, 1:] > resized[:, :-1]
    h = sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])
    p = hashes.get(h, [])
    p.append(imagePath)
    hashes[h] = p


def low_res_image(hps):
    resolutions = {}
    for p in hps:
        (h, w, c) = cv2.imread(p).shape
        logging.info("Path: {}, Height: {} Width: {}".format(p, h, w))
        resolutions[p] = h*w
    max_res = set([max(resolutions.values())])
    all = set(resolutions.values())
    all_images = list(set(resolutions.keys()))
    deleted_res = all - max_res
    deleted_images = []
    for p, res in resolutions.items():
        if res in deleted_res:
            deleted_images.append(p)
    if deleted_images:
        return deleted_images
    return all_images[1:]


logging.info("Computing image hashes...")

dir_path = tempfile.mkdtemp()


def remove_duplicate(img_path):
    img_paths = list(paths.list_images(img_path))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(dhash, img_paths, [8 for i in range(len(img_paths))])

    with open('../dataset.json', 'w') as f:
        f.write(str(hashes))
    for (h, hashedPaths) in hashes.items():
        if len(hashedPaths) > 1:
            montage = None
            for p in hashedPaths:
                image = cv2.imread(p)
                image = cv2.resize(image, (640, 480))
                if montage is None:
                    montage = image
                else:
                    montage = np.hstack([montage, image])
                    logging.info("hash: {} path {}".format(h, hashedPaths))
                    cv2.imshow("Montage", montage)
                    cv2.waitKey(0)
            # otherwise, we'll be removing the duplicate images
            for p in low_res_image(hashedPaths):
                try:
                    logging.info("Deleting {}".format(p))
                    shutil.move(p, dir_path)
                except shutil.Error as e:
                    logging.info(e)
                    shutil.move(p, dir_path)
                    shutil.rmtree(dir_path)
        if cv2.waitKey(1) & 0xFF == ord('q'):
              break

