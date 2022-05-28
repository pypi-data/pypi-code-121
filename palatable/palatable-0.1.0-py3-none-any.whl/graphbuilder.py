from collections import defaultdict
from itertools import combinations

from palatable.course import Course
from palatable.graph import Graph
from palatable.helpers import read_file
from palatable.student import Student


class GraphBuilder(object):
    def __init__(self, slots: int, schedule_path: str, courses_path: str) -> None:
        self.slots = slots
        self.schedule_path = schedule_path
        self.courses_path = courses_path

        self.courses = []
        self.courses_ids = []

    def _read_courses(self):
        courses = defaultdict(list)

        for line in read_file(self.courses_path):
            key, name, level, sections = line.split()
            level, sections = int(level), int(sections)

            course = Course(key, name, level, sections)
            courses[level].append(course)

        return courses

    def _read_schedule(self):
        all_schedules = []

        for line in read_file(self.schedule_path):
            student_id, *courses_ids = line.split()

            student = Student(student_id)
            schedule = []

            for course_id in courses_ids:
                course = Course.get(course_id)

                # Only process courses that already been passed in the input. Student
                # might be enrolled in courses that we don't want to schedule.
                if course:
                    course.students.append(student)
                    student.add_course(course)
                    schedule.append(course)

            if schedule:
                all_schedules.append(schedule)

        return all_schedules

    def _process_courses(self, schedules):
        """
        For each course (node), we need to find the set of adjacent courses, and
        the weight of the edges connecting the course to its adjacent courses so that
        we are able fill in the weights in the adjacency list.
        We also want to set the degree of each course.

        Two courses are adjacent if the two corresponding courses are
        registered by at least one student.
        """
        graph = Graph(directed=False)

        for schedule in schedules:
            courses_combinations = combinations(schedule, 2)
            for source, destination in courses_combinations:
                weight = graph.get_weight(source, destination)
                if weight:
                    graph.set_weight(source, destination, weight=weight + 1)
                else:
                    graph.add_edge(source, destination)

        # Set the degree of the course
        for course in graph:
            course.degree = graph.get_degree(course)
            course.largest_weight = graph.get_largest_weight(course)

        return graph

    def build(self):
        self._read_courses()
        schedules = self._read_schedule()

        return self._process_courses(schedules)
