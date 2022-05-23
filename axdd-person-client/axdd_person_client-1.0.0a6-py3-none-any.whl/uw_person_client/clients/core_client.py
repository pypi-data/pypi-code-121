# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.orm.exc import NoResultFound
from uw_person_client.clients import AbstractUWPersonClient
from uw_person_client.databases.uwpds import UWPDS
from uw_person_client.exceptions import PersonNotFoundException
from uw_person_client.components import Person, Student, Employee, \
    Transcript, Major, Sport, Adviser, Term


class UWPersonClient(AbstractUWPersonClient):

    """
    Public methods
    """

    def __init__(self):
        self.DB = UWPDS()

    def get_person_by_uwnetid(self, uwnetid):
        sqla_person = self.DB.session.query(self.DB.HistoricalPerson).filter(
            self.DB.HistoricalPerson.prior_uwnetid == uwnetid).first()
        if not sqla_person:
            raise PersonNotFoundException()
        return self._map_person(sqla_person)

    def get_person_by_uwregid(self, uwregid):
        sqla_person = self.DB.session.query(self.DB.HistoricalPerson).filter(
            self.DB.HistoricalPerson.prior_uwregid == uwregid).first()
        if not sqla_person:
            raise PersonNotFoundException()
        return self._map_person(sqla_person)

    def get_person_by_student_number(self, student_number):
        sqla_person = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).filter(
            self.DB.Student.student_number == student_number).one_or_none()
        if not sqla_person:
            raise PersonNotFoundException()
        return self._map_person(sqla_person)

    def get_persons(self, page=None, page_size=None):
        sqla_persons = self.DB.session.query(self.DB.Person)
        return self._get_page(sqla_persons,
                              self._map_person,
                              page=page,
                              page_size=page_size)

    def get_active_students(self, page=None, page_size=None):
        sqla_persons = self.DB.session.query(self.DB.Person).filter(
            self.DB.Person._is_active_student == True)  # noqa
        return self._get_page(sqla_persons,
                              self._map_person,
                              page=page,
                              page_size=page_size)

    def get_active_employees(self, page=None, page_size=None):
        sqla_persons = self.DB.session.query(self.DB.Person).filter(
            self.DB.Person._is_active_employee == True)  # noqa
        return self._get_page(sqla_persons,
                              self._map_person,
                              page=page,
                              page_size=page_size)

    def get_advisers(self, advising_program=None):
        sqla_persons = self.DB.session.query(self.DB.Person).join(
            self.DB.Employee).join(self.DB.Adviser)
        if advising_program:
            sqla_persons = sqla_persons.filter(
                self.DB.Adviser.advising_program == advising_program)
        return [self._map_person(item)for item in sqla_persons.all()]

    def get_persons_by_adviser_netid(self, uwnetid):
        sqla_adviser = self.DB.session.query(self.DB.Adviser).join(
            self.DB.Employee).join(self.DB.Person).filter(
            self.DB.Person.uwnetid == uwnetid).one()
        sqla_persons = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).join(self.DB.StudentToAdviser).join(
            self.DB.Adviser).filter(self.DB.Adviser.id == sqla_adviser.id)
        return [self._map_person(item)for item in sqla_persons.all()]

    def get_persons_by_adviser_regid(self, uwregid):
        sqla_adviser = self.DB.session.query(self.DB.Adviser).join(
            self.DB.Employee).join(self.DB.Person).filter(
            self.DB.Person.uwregid == uwregid).one()
        sqla_persons = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).join(self.DB.StudentToAdviser).join(
            self.DB.Adviser).filter(self.DB.Adviser.id == sqla_adviser.id)
        return [self._map_person(item)for item in sqla_persons.all()]

    """
    Private Methods
    """

    def _get_page(self, query, mapper, page=None, page_size=None):
        """
        Returns results for a single page of data. If page and page_size are
        not specified, all results are returned
        """
        if page is not None and page_size is not None:
            # limit results to page
            query = query.limit(page_size).offset(
                (page - 1) * page_size)
        return [mapper(item)for item in query.all()]

    def _map_person(self, sqla_person, include_employee=True,
                    include_student=True):
        person = Person()
        person.uwnetid = sqla_person.uwnetid
        person.uwregid = sqla_person.uwregid
        prior_uwnetids = self.DB.session.query(self.DB.PriorUWNetID).filter(
            self.DB.PriorUWNetID.person_id == sqla_person.id).all()
        person.prior_uwnetids = [pni.uwnetid for pni in prior_uwnetids]
        prior_uwregids = self.DB.session.query(self.DB.PriorUWRegID).filter(
            self.DB.PriorUWRegID.person_id == sqla_person.id).all()
        person.prior_uwregids = [pri.uwregid for pri in prior_uwregids]
        person.pronouns = sqla_person.pronouns
        person.full_name = sqla_person.full_name
        person.display_name = sqla_person.display_name
        person.first_name = sqla_person.first_name
        person.surname = sqla_person.surname
        person.preferred_first_name = sqla_person.preferred_first_name
        person.preferred_middle_name = \
            sqla_person.preferred_middle_name
        person.preferred_surname = sqla_person.preferred_surname
        person.whitepages_publish = sqla_person.whitepages_publish
        person.active_student = sqla_person._is_active_student
        person.active_employee = sqla_person._is_active_employee

        if include_student:
            try:
                sqla_student = self.DB.session.query(self.DB.Student).filter(
                    self.DB.Student.person_id == sqla_person.id).one()
                person.student = self._map_student(sqla_student)
            except NoResultFound:
                pass

        if include_employee:
            try:
                sqla_employee = self.DB.session.query(self.DB.Employee).filter(
                    self.DB.Employee.person_id == sqla_person.id).one()
                person.employee = self._map_employee(sqla_employee)
            except NoResultFound:
                pass

        return person

    def _map_student(self, sqla_student):
        student = Student()
        student.student_number = sqla_student.student_number
        student.assigned_ethnic_code = \
            sqla_student.assigned_ethnic_code
        student.assigned_ethnic_desc = \
            sqla_student.assigned_ethnic_desc
        student.assigned_ethnic_group_desc = \
            sqla_student.assigned_ethnic_group_desc
        student.birthdate = sqla_student.birthdate
        student.student_email = sqla_student.student_email
        student.external_email = sqla_student.external_email
        student.local_phone_number = sqla_student.local_phone_number
        student.gender = sqla_student.gender
        student.cumulative_gpa = sqla_student.cumulative_gpa
        student.total_credits = sqla_student.total_credits
        student.total_uw_credits = sqla_student.total_uw_credits
        student.campus_code = sqla_student.campus_code
        student.campus_desc = sqla_student.campus_desc
        student.class_code = sqla_student.class_code
        student.class_desc = sqla_student.class_desc
        student.resident_code = sqla_student.resident_code
        student.resident_desc = sqla_student.resident_desc
        student.perm_addr_line1 = sqla_student.perm_addr_line1
        student.perm_addr_line2 = sqla_student.perm_addr_line2
        student.perm_addr_city = sqla_student.perm_addr_city
        student.perm_addr_state = sqla_student.perm_addr_state
        student.perm_addr_5digit_zip = sqla_student.perm_addr_5digit_zip
        student.perm_addr_4digit_zip = sqla_student.perm_addr_4digit_zip
        student.perm_addr_country = sqla_student.perm_addr_country
        student.perm_addr_postal_code = sqla_student.perm_addr_postal_code
        student.registered_in_quarter = sqla_student.registered_in_quarter

        # map majors
        student.majors = []
        for major in sqla_student.major:
            major = self._map_major(major)
            student.majors.append(major)

        # map sports
        student.sports = []
        for sport in sqla_student.sport:
            sport = self._map_sport(sport)
            student.sports.append(sport)

        # map advisers
        student.advisers = []
        for adviser in sqla_student.adviser:
            adviser_person = self._map_person(adviser.employee.person,
                                              include_student=False)
            student.advisers.append(adviser_person)

        # map transcripts
        student.transcripts = []
        for transcript in sqla_student.transcript:
            transcript = self._map_transcript(transcript)
            student.transcripts.append(transcript)

        return student

    def _map_employee(self, sqla_employee):
        employee = Employee()
        employee.employee_number = sqla_employee.employee_number
        employee.employee_affiliation_state = \
            sqla_employee.employee_affiliation_state
        employee.email_addresses = sqla_employee.email_addresses
        employee.home_department = sqla_employee.home_department
        employee.primary_title = sqla_employee.title
        employee.primary_department = sqla_employee.department

        if sqla_employee.adviser:
            employee.adviser = self._map_adviser(sqla_employee.adviser)

        return employee

    def _map_adviser(self, sqla_adviser):
        adviser = Adviser()
        adviser.is_dept_adviser = sqla_adviser.is_dept_adviser
        adviser.advising_email = sqla_adviser.advising_email
        adviser.advising_phone_number = \
            sqla_adviser.advising_phone_number
        adviser.advising_program = sqla_adviser.advising_program
        adviser.advising_pronouns = sqla_adviser.advising_pronouns
        adviser.booking_url = sqla_adviser.booking_url
        return adviser

    def _map_sport(self, sqla_sport):
        sport = Sport()
        sport.sport_code = sqla_sport.sport_code
        return sport

    def _map_major(self, sqla_major):
        major = Major()
        major.major_abbr_code = sqla_major.major_abbr_code
        major.major_full_code = sqla_major.major_full_code
        major.major_name = sqla_major.major_name
        major.major_short_name = sqla_major.major_short_name
        return major

    def _map_transcript(self, sqla_transcript):
        transcript = Transcript()
        transcript.tran_term = self._map_term(
            sqla_transcript.tran_term)
        transcript.leave_ends_term = self._map_term(
            sqla_transcript.leave_ends_term)
        transcript.resident = sqla_transcript.resident
        transcript.resident_cat = sqla_transcript.resident_cat
        transcript.veteran = sqla_transcript.veteran
        transcript.veteran_benefit = sqla_transcript.veteran_benefit
        transcript.class_code = sqla_transcript.class_code
        transcript.qtr_grade_points = \
            float(sqla_transcript.qtr_grade_points)
        transcript.qtr_graded_attmp = \
            float(sqla_transcript.qtr_graded_attmp)
        transcript.honors_program = sqla_transcript.honors_program
        transcript.special_program = sqla_transcript.special_program
        transcript.scholarship_type = sqla_transcript.scholarship_type
        transcript.yearly_honor_type = sqla_transcript.yearly_honor_type
        transcript.exemption_code = sqla_transcript.exemption_code
        transcript.grad_status = sqla_transcript.grad_status
        transcript.num_ind_study = sqla_transcript.num_ind_study
        transcript.num_courses = sqla_transcript.num_courses
        transcript.enroll_status = sqla_transcript.enroll_status
        transcript.tenth_day_credits = \
            float(sqla_transcript.tenth_day_credits)
        transcript.tr_en_stat_dt = sqla_transcript.tr_en_stat_dt
        return transcript

    def _map_term(self, sqla_term):
        term = Term()
        term.year = sqla_term.year
        term.quarter = sqla_term.quarter
        return term
