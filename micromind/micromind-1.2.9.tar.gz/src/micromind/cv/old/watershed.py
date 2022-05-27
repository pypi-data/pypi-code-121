import cv2
import numpy as np
from skimage.feature import peak_local_max





class WatershedOpenCV(WatershedTransform):
    pass


class WatershedMarkerBased(WatershedTransform):
    def __init__(self, backend="skimage", use_dt=False, min_distance=20):
        self._backend = backend
        self.use_dt = use_dt
        self.min_distance = min_distance

    def apply(self, mask, markers=None, image_color=None):
        if self._backend == "opencv":
            return self._cv_transform(mask, markers, image_color=image_color)
        elif self._backend == "skimage":
            return self._skimage_transform(mask, markers, image=image_color)

    def _cv_transform(self, mask, markers, image_color=None):
        if self.use_dt:
            mask = cv2.distanceTransform(
                mask, distanceType=cv2.DIST_L2, maskSize=5
            ).astype(np.uint8)
        if markers is None:
            local_max = peak_local_max(
                mask, indices=False, min_distance=self.min_distance
            ).astype(np.uint8)
            markers = cv2.connectedComponents(local_max, connectivity=8)[1]

        cv2.imwrite("mask.png", mask * 255)
        if image_color is None:
            image_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        signal = mask.copy()
        signal[markers != 0] = 0

        # Add one to all labels so that sure background is not 0, but 1
        markers = markers + 1

        # Now, mark the region of unknown with zero
        markers[signal > 0] = 0
        cv2.imwrite(
            "markers.png",
            cv2.applyColorMap((markers * 8).astype(np.uint8), cv2.COLORMAP_JET),
        )
        labels = cv2.watershed(image_color, markers)
        labels = labels - 1
        labels[labels < 1] = 0
        return labels
