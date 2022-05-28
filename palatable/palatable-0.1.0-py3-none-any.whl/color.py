from faker import Faker


class Color(object):
    """
    A representation for node color. Implemented to simplify graph coloring.
    """

    def __init__(self, key, day=0, slot=0, instances=0) -> None:
        """
        Constructs a color with the specified key, day, and time slot
        """
        fake = Faker()

        self.key = key
        self.name = fake.unique.color_name()
        self.day = day
        self.slot = slot

        self._weight = None
        self.available_instances = instances
        self.colored_courses = []

    def calculate_weight(self, slots):
        """
        We define the weight of a color to be W (Rij) = (i- 1)*k+J;
        k is the range of J. A color Rij is said to be smaller than color Rgh
        if the weight W (Rij) is smaller than W (Rgh).
        """
        self._weight = ((self.day - 1) * slots) + self.slot

        return self._weight

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Color: {self.key}>"
