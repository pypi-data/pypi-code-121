import math
from typing import Optional
from matplotlib import patches
from matplotlib import pyplot as plt


class Triangle:
    def __init__(self, l1: float, l2: float, l3: Optional[float] = None, angle: Optional[float] = None):
        """
        Create an instance of the Triangle class. It can be done either by specifying the three edges
        of the triangle, or two edges and the angle between them. Both cannot be used, even if the resulting
        triangle could exist.

        If the triangle is of unreasonable proportions (e.g. 1 degree angle), it will not look pretty.

        :param l1: the length pf the first edge of the triangle.
        :param l2: the length pf the second edge of the triangle.
        :param l3: the length pf the third edge of the triangle.
        :param angle: the angle between the first and second edge of the triangle.
        """
        if not l3 and not angle:
            raise ValueError('Either angle or third length must be provided.')

        if l3 and angle:
            raise ValueError('Either angle or third length must be provided, but not both.')

        # Assure the angle is possible in a triangle.
        if angle:
            if angle <= 0 or angle >= 180:
                raise ValueError('Angle must be between 0 and 180 degrees.')

            l3 = (l1 ** 2 + l2 ** 2 - 2 * l1 * l2 * math.cos(math.radians(angle))) ** 0.5

        # Assure the triangle is possible
        try:
            assert l1 + l2 > l3
            assert l1 + l3 > l2
            assert l3 + l2 > l1
        except AssertionError:
            raise ValueError('No length may be bigger than the other two combined.')

        self.lengths = list(reversed(sorted([l1, l2, l3])))

        # Calculate the area of the triangle
        semi_perimeter = sum(self.lengths) / 2

        self.area = (semi_perimeter * (semi_perimeter - self.lengths[0]) * (semi_perimeter - self.lengths[1]) * (
                    semi_perimeter - self.lengths[2])) ** 0.5

        # Nprmalise the triangle size to always be reasonable.
        self.__ratio = 20 / sum(self.lengths)
        self.__lengths = [length * self.__ratio for length in self.lengths]

        # Calculate the normalised area
        self.__area = self.area * self.__ratio * self.__ratio

        self.__A, self.__B, self.__C = self.__get_coordinates(self.__lengths)
        self.A_angle, self.B_angle, self.C_angle = self.__get_angles(self.__A, self.__B, self.__C)


    @classmethod
    def __get_coordinates(cls, lengths):
        s = sum(lengths) / 2  # semi-perimeter
        area = (s * (s - lengths[0]) * (s - lengths[1]) * (s - lengths[2])) ** 0.5  # Heron's formula
        y = 2 * area / lengths[0]  # height
        x = (lengths[2] ** 2 - y ** 2) ** 0.5
        return [[0.0, 0.0], [lengths[0], 0.0], [x, y]]

    @classmethod
    def __get_angle(cls, a, b, c):
        ang = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
        return ang + 360 if ang < 0 else ang

    @classmethod
    def __get_angles(cls, A, B, C):
        first = cls.__get_angle(B, A, C)
        second = cls.__get_angle(C, B, A)
        third = cls.__get_angle(A, C, B)

        return first, second, third

    @classmethod
    def __get_max_coordinates(cls, coords):
        x = max(i[0] for i in coords)
        y = max(i[1] for i in coords)

        return x + 1, y + 1

    def draw(self) -> None:
        """
        Draw the triangle on an interactive plot, where the angles, side lengths and area of the triangle can be seen.

        :return: No return
        """
        fig, ax = plt.subplots()

        # Draw the triangle poygon
        polygon = plt.Polygon([self.__A, self.__B, self.__C], fill=None, color='black')

        # Draw the wedges for each angle of the triangle
        A_patch = patches.Wedge(self.__A, 0.5, theta1=0.0, theta2=self.A_angle, fill=None)
        B_patch = patches.Wedge(self.__B, 0.5, theta2=180.0, theta1=180.0 - self.B_angle, fill=None)
        C_patch = patches.Wedge(self.__C, min(0.5, self.__area / self.__lengths[0]), theta1=180.0 + self.A_angle, theta2=360.0 - self.B_angle, fill=None)

        # Calculate the incenter of the triangle.
        incenter_x = self.__A[0] * self.__lengths[1] + self.__B[0] * self.__lengths[2] + self.__C[0] * self.__lengths[0]
        incenter_y = self.__A[1] * self.__lengths[1] + self.__B[1] * self.__lengths[2] + self.__C[1] * self.__lengths[0]

        incenter_x = incenter_x / sum(self.__lengths)
        incenter_y = incenter_y / sum(self.__lengths)

        # Place invisible area annotation on the incenter.
        annotation = plt.annotate('area: ' + str(round(self.area, 2)), (incenter_x, incenter_y),
                                  bbox=dict(boxstyle="round", fc="w"), ha='center', va='center')
        annotation.set_visible(False)

        ax.add_patch(polygon)
        ax.add_patch(A_patch)
        ax.add_patch(B_patch)
        ax.add_patch(C_patch)

        # Put point names near the triangle, away from the incenter
        for name, point in zip(['A', 'B', 'C'], [self.__A, self.__B, self.__C]):
            center_vector = point[0] - incenter_x, point[1] - incenter_y
            length = (center_vector[0] ** 2 + center_vector[1] ** 2) ** 0.5
            unit_vector = center_vector[0] / length, center_vector[1] / length

            moved_point = point[0] + unit_vector[0] * 0.25, point[1] + unit_vector[1] * 0.25

            plt.annotate(name, moved_point, ha='center', va='center')

        annotation_objects = [polygon, A_patch, B_patch, C_patch]
        annotations = [annotation]

        # Put invisible angle number annotations on the angle wedges
        for angle, point in zip([self.A_angle, self.B_angle, self.C_angle], [self.__A, self.__B, self.__C]):
            annotation = plt.annotate(str(round(angle, 2)) + '°', point, xytext=(10, 10), textcoords="offset points",
                 bbox=dict(boxstyle="round", fc="w"))
            annotations.append(annotation)
            annotation.set_visible(False)

        # Put invisible length annotations on the edges.
        for duo, length in zip([[self.__B, self.__A], [self.__C, self.__B], [self.__C, self.__A]], [self.lengths[0], self.lengths[1], self.lengths[2]]):
            line = self.__line(duo[0], duo[1])
            annotation = plt.annotate(round(length, 2), self.__midpoint(duo[0], duo[1]),
                 bbox=dict(boxstyle="round", fc="w"), ha='center', va='center')

            annotation_objects.append(line)
            annotations.append(annotation)
            annotation.set_visible(False)

        # Find the limits of the plot to always include the triangle
        x_max, y_max = self.__get_max_coordinates([self.__A, self.__B, self.__C])

        plt.ylim(-1, y_max)
        plt.xlim(-1, x_max)

        plt.axis('off')
        plt.axis('equal')

        # Turn on annotations when hovered over the annotated items
        def hover(event):
            if event.inaxes == ax:
                for item, annotation in zip(annotation_objects, annotations):
                    cont, ind = item.contains(event)
                    if cont:
                        annotation.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if annotation.get_visible():
                            annotation.set_visible(False)
                            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.show()

    @classmethod
    def __line(cls, a, b):
        x_values = [a[0], b[0]]
        y_values = [a[1], b[1]]
        line = plt.plot(x_values, y_values)[0]
        line.set_visible(False)

        return line

    @classmethod
    def __midpoint(cls, a, b):
        return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
