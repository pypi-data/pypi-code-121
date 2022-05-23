from math import atan2, degrees, pi

import cv2
import numpy as np
from scipy.interpolate import interp1d

from micromind.cv.image import intersection_with_line
from micromind.geometry.line import Line2
from micromind.geometry.vector import Vector2


class PropertyInfo:
    def __init__(self, name):
        self.name = name


class PropertyName(PropertyInfo):
    def __init__(self):
        super().__init__("name")

    def compute(self, synapse, MTOC, perforin):
        return f"{synapse.cell_1.name}/{synapse.cell_2.name}"


class PropertyPulsed(PropertyInfo):
    def __init__(self):
        super().__init__("pulsed")

    def compute(self, synapse, MTOC, perforin):
        return synapse.cell_1.get_data("condition")


class PropertyValue(PropertyInfo):
    def __init__(self, name, best, worst):
        super().__init__(name)
        self.best = best
        self.worst = worst
        self.interp = interp1d(
            [worst, best], [0, 1], bounds_error=False, fill_value=(0, 1)
        )

    def interpolate(self, data):
        return self.interp(data)


class PropertyAngle(PropertyValue):
    def __init__(self):
        super().__init__("angle", 10, 170)

    def compute(self, synapse, MTOC, perforin):
        v = synapse.cell_2 - synapse.cell_1
        w = MTOC - synapse.cell_1
        angle = atan2(w.y * v.x - w.x * v.y, w.x * v.x + w.y * v.y)
        if angle < 0:
            angle = abs(angle)
        return degrees(angle)


class PropertyPerforinSpread(PropertyValue):
    def __init__(self):
        super().__init__("perforin spread", 5, 30)

    def compute(self, synapse, MTOC, perforin):
        np_coords_MTOC = np.array([[MTOC.y], [MTOC.x]])
        diff_squared = np.square(perforin - np_coords_MTOC)
        sqrt_coords = np.sqrt(diff_squared[0] + diff_squared[1])
        mean_perforin_spread = np.mean(sqrt_coords)
        if mean_perforin_spread == np.nan:
            mean_perforin_spread = 20
        print(f"spread: {mean_perforin_spread}")
        return mean_perforin_spread


class PropertyPerforinDistance(PropertyValue):
    def __init__(self):
        super().__init__("perforin distance", 5, 50)

    def compute(self, synapse, MTOC, perforin):
        centroid_perforin = perforin.mean(axis=1)
        perforin_point = Vector2(centroid_perforin[1], centroid_perforin[0])
        synapse_line = Line2(synapse.cell_1, synapse.cell_2)
        synapse_line = [
            synapse_line.pt1.as_int_tuple(),
            synapse_line.pt2.as_int_tuple(),
        ]
        inter = intersection_with_line(synapse.cell_2.mask, synapse_line)
        membrane_point = Vector2(inter[1], inter[0])
        return membrane_point.distance(perforin_point)


class PropertyDistanceMTOC(PropertyValue):
    def __init__(self):
        super().__init__("MTOC distance", 5, 20)

    def compute(self, synapse, MTOC, perforin):
        MTOC_line = Line2(MTOC, synapse.cell_2)
        MTOC_line = [MTOC_line.pt1.as_int_tuple(), MTOC_line.pt2.as_int_tuple()]
        MTOC_to_CTL_membrane = intersection_with_line(synapse.cell_1.mask, MTOC_line)
        MTOC_to_CTL_membrane = Vector2(MTOC_to_CTL_membrane[1], MTOC_to_CTL_membrane[0])
        return MTOC_to_CTL_membrane.distance(MTOC)


class PropertyRoundness(PropertyValue):
    def __init__(self):
        super().__init__("roundness", 0, 1.0)

    def compute(self, synapse, MTOC, perforin):
        return abs(1.0 - synapse.cell_1.roundness)


class PropertyPerforinInContact(PropertyValue):
    def __init__(self):
        super().__init__("perforin in contact", 20, 5)
        self.K = np.ones((11, 11), np.uint8)

    def compute(self, synapse, MTOC, perforin):
        perforin_mask = np.zeros_like(synapse.cell_1.mask)
        perforin_mask[perforin] = 1
        n_perf = np.count_nonzero(perforin_mask * synapse.cell_1.mask)
        if not n_perf:
            return 0
        bigger_target = cv2.dilate(synapse.cell_2.mask, self.K)
        overlap_mask = bigger_target * synapse.cell_1.mask
        n_perf_overlap = np.count_nonzero(perforin_mask * overlap_mask)
        ratio = (n_perf_overlap / n_perf) * 100
        return ratio


class PropertyPerforinRatio(PropertyValue):
    def __init__(self):
        super().__init__("perforin ratio", 50, 5)

    def compute(self, synapse, MTOC, perforin):
        perforin_mask = np.zeros_like(synapse.cell_1.mask)
        perforin_mask[perforin] = 1
        n_perf = np.count_nonzero(perforin_mask * synapse.cell_1.mask)
        if not n_perf:
            return 0
        ratio = (n_perf / synapse.cell_1.area) * 100
        print(f"perf: {n_perf}, area: {synapse.cell_1.area}, ratio: {ratio}")
        return ratio
