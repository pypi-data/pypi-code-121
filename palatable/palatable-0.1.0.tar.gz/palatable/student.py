class Student(object):
    """
    This class represents a student object.
    Every student for scheduling purposes should has a unique key
    and courses enrolled in.
    """

    _all_students = set()

    def __init__(self, key: str) -> None:
        if key in self._all_students:
            raise AttributeError(f"Student with the same key already exists: {key}")

        self._all_students.add(key)

        self.key = key  # A student unique key
        self._registered_courses = set()  # Courses Schedule for this student

    def add_course(self, course):
        self._registered_courses.add(course)

    @property
    def courses(self):
        return self._registered_courses
