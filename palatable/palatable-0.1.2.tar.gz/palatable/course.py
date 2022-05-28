from typing import List

from palatable.student import Student


class Course(object):
    """
    A class that represents a course object.

    Every course should has the following attributes:
        - key
        - name
        - course level
        - time slot
        - color
        - number of sections
        - registered students

    Each Course represents a node in our graph, which means it has a
        - list of adjacent nodes (courses)
        - list of registered students
        - list of weight matrix
        - degree.
    """

    _all_courses = {}

    def __init__(self, key: str, name: str, level: int, sections: int) -> None:
        """
        Constructs a Course with the specified attributes and initializes
        an empty registered students List and assigns a color to this course.

        @param key      The course key
        @param name     The course name
        @param level    The course level
        @param sections Number of sections this course has
        """
        if key in self._all_courses:
            raise AttributeError(f"Course with the same key already exists: {key}")
        self._all_courses[key] = self

        self.key = key
        self.level = level
        self.name = name
        self.sections = sections
        self.color = None

        # Set the concurrency level of each course to the number of
        # sections for that course.
        self.concurrency_level = sections

        self._students = []
        self.weight_matrix = []
        self.time_slot = None

        # Attributes the graph set
        self.degree = 0
        self.largest_weight = 0

    @property
    def is_colored(self):
        """
        Returns True if this course is colored, False otherwise.
        """
        return self.color is not None

    @classmethod
    def exists(cls, key: str):
        return key in cls._all_courses

    @classmethod
    def get(cls, key: str):
        return cls._all_courses.get(key)

    @property
    def students(self) -> List[Student]:
        return self._students

    def add_student(self, student: Student):
        self._students.append(student)

    def __hash__(self) -> int:
        return id(self)

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"<Course: {self.key}>"

    def __lt__(self, __o):
        """
        Sort the courses in a descending order based on the degree of courses.
            - Courses with similar degrees are ordered based on the largest
              weight w in its adjacency list.
            - Courses with similar degrees d and weights w are ordered based on
              their course ID (smallest ID first).
        """
        if self.degree == __o.degree:
            if self.largest_weight == __o.largest_weight:
                return self.key < __o.key
            return self.largest_weight < __o.largest_weight

        return self.degree < __o.degree
