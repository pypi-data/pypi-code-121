import cv2

from cvee.io.handlers.base import BaseFileHandler


# TODO: write test cases
class ImageHandler(BaseFileHandler):
    def load_from_fileobj(self, file, **kwargs):
        raise NotImplementedError()

    def save_to_fileobj(self, file, obj, **kwargs):
        raise NotImplementedError()

    def load_from_path(self, filepath, to_rgb=True, **kwargs):
        img = cv2.imread(filepath, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED)

        if to_rgb and img.ndim == 3:
            if img.shape[-1] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif img.shape[-1] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

        return img

    def save_to_path(self, filepath, img, from_rgb=True, **kwargs):
        if from_rgb and img.ndim == 3:
            if img.shape[-1] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            elif img.shape[-1] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)

        cv2.imwrite(filepath, img)
