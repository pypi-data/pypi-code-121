import unittest
from univer_db.models import TeacherChairLink, OfficeRegistrator, OfficeRegistratorFacultyLink, Adviser

from . import Session


class TestTeacherChairLink(unittest.TestCase):
    def test_get_obj(self):
        session = Session()
        links = session.query(TeacherChairLink).filter()
        print("links: %s" % links.count())
        self.assertTrue(links.count())


class TestOfficeRegistrator(unittest.TestCase):
    def test_get_obj(self):
        session = Session()
        office_registrator = session.query(OfficeRegistrator).first()
        print(f'office_registrator: {office_registrator}')

        for faculty_links in office_registrator.faculties:
            print(f'faculty: {faculty_links.faculty}')


class TestAdviser(unittest.TestCase):
    def test_get_obj(self):
        session = Session()
        adviser = session.query(Adviser).filter(Adviser.status == 1).first()
        print(f'adviser: {adviser}')

        total = adviser.students.count()

        for index, adviser_student in enumerate(adviser.students):
            print(f'[{index + 1}/{total}] student: {adviser_student.student}')
