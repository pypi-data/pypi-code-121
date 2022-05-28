from typing import List

from palatable.color import Color
from palatable.course import Course
from palatable.graph import Graph
from palatable.helpers import calculate_distance


class GraphPainter(object):
    def __init__(self, graph: Graph, days: int, slots: int, fairness: int) -> None:
        self.graph = graph
        self.current_courses = self.graph.adj_list

        self.days = days
        self.slots = slots
        self.fairness = fairness

        self.colors = self._generate_colors_matrix()

    def _generate_colors_matrix(self):
        """
        Responsible of initializing the color matrix with empty
        non-scheduled colors.
        """
        colors = []

        key = 1
        for day in range(self.days):
            colors.append(list())
            for slot in range(self.slots):
                colors[day].append(Color(key, day=day, slot=slot, instances=self.days))
                key += 1

        return colors

    def _is_fair_to_schedule(self, course: Course, day: int):
        """
        Determines fairness of the scheduling for each student in the course.
        Fairness means that a student doesn't get a number of exams in the same
        day that equals or exceeds the fairness parameter determined by faculty.

        @params course The course we want to check its check enrolled students.
        @params day The day to schedule the exams in.

        @returns True if all students get fair assignment, False otherwise.
        """
        for student in course.students:
            counter = 0
            for slot in range(self.slots):
                colored_courses = self.colors[day][slot].colored_courses
                booked = False

                for colored_course in colored_courses:
                    if student in colored_course.students:
                        counter += 1
                        if counter == self.fairness or booked:
                            return False

                        booked = True

        return True

    def _get_first_course_color(self, course):
        """
        Responsible for fetching the course color. The color should
        have available instances more than or equals the course sections.
        If this condition fails we will return None, which means no scheduling
        is possible.

        @params course The first course in the scheduling process.
        @returns The color assigned to the give course or None.
        """
        for day in range(self.days):
            for slot in range(self.slots):
                color = self.colors[day][slot]
                if color.available_instances >= course.sections:
                    return color

    def _is_color_valid(self, potential_color, neighbor_color, course):
        """
        Determines whether a color is for the given course is valid or not.

        - If the potential color (exam potential date and time) is in the same
          day as its neighbor, and the potential color's slot is super close to
          its neighber then this is not a valid scheduling.
        - If potential color's available instances is less than or equals to the
          course section, then this is not a valid scheduling.
        - If the scheduling is not fair for one of the students, then this is
          not a valid scheduling.

        Otherwise, all seems right and the color is okay to be assigned to the
        given course.
        """
        # Same day
        if calculate_distance(neighbor_color.day, potential_color.day) == 0:
            if calculate_distance(neighbor_color.slot, potential_color.slot) <= 1:
                return False

        if potential_color.available_instances <= course.sections:
            return False

        if not self._is_fair_to_schedule(course, potential_color.day):
            return False

        return True

    def _get_smallest_available_color(self, course: Course):
        """
        Responsible for fetching the course color. The color be checked against
        _is_color_valid for validity check. If this condition fails we will return
        None, which means course cannot be scheduled.

        @params course The first course in the scheduling process.
        @returns The color assigned to the give course or None.
        """
        adjacency_list = self.graph.get_adjacency_list(course)

        for day in range(self.days):
            for slot in range(self.slots):
                valid = True
                potential_color = self.colors[day][slot]

                for neighbor, _ in adjacency_list:
                    neighbor_color = neighbor.color
                    if not neighbor.is_colored:
                        continue

                    color_day = neighbor_color.day
                    color_slot = neighbor_color.slot

                    not_same_day_and_time = color_day != day or color_slot != slot

                    valid = (
                        self._is_color_valid(potential_color, neighbor_color, course)
                        if not_same_day_and_time
                        else False
                    )

                    if not valid:
                        break

                if valid:
                    return potential_color

    def _set_course_color(self, course, new_color, day, slot):
        """
        Responsible for setting the course color. Will reset the number of
        available instances for that color in the process.
        """
        available_instances = (
            self.colors[day][slot].available_instances - course.sections
        )

        if available_instances < 0:
            raise ValueError("Available instances is less than 0, operation aborted.")

        course.color = new_color
        self.colors[day][slot].colored_courses.append(course)
        self.colors[day][slot].available_instances = available_instances

    def _attempt_course_color(self, course, colored_courses, color=None):
        """
        A reusable module for coloring the given course.
        """
        color = color or self._get_smallest_available_color(course)

        if color and color.key:
            self._set_course_color(course, color, color.day, color.slot)
            colored_courses += 1

        return colored_courses

    def paint(self):
        """
        The main logic of coloring the courses.
        """
        sorted_courses: List[Course] = sorted(self.graph, reverse=True)
        colored_courses = 0

        if not len(sorted_courses):
            return colored_courses

        first_course = sorted_courses[0]
        if not first_course.is_colored:
            first_course_color = self._get_first_course_color(first_course)

            if not first_course_color:
                raise RuntimeError("No schedule is possible.")

            colored_courses = self._attempt_course_color(
                first_course, colored_courses, color=first_course_color
            )

        for i in range(1, len(sorted_courses)):
            course = sorted_courses[i]

            if not course.is_colored:
                colored_courses = self._attempt_course_color(course, colored_courses)

            # Process adjacent courses
            sorted_adjacency_courses = sorted(
                self.graph.get_adjacency_list(course), reverse=True
            )

            for (adj_course, _) in sorted_adjacency_courses:
                if not adj_course.is_colored:
                    colored_courses = self._attempt_course_color(
                        adj_course, colored_courses
                    )

        return colored_courses
