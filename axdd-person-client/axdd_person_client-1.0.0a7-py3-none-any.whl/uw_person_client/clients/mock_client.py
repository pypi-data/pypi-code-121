# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
import glob
import os
from uw_person_client.clients import AbstractUWPersonClient
from uw_person_client.components import Person
from uw_person_client.exceptions import PersonNotFoundException


class MockedUWPersonClient(AbstractUWPersonClient):

    def _glob_fixture_file(self, search_value):
        abspath = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../fixtures/'))
        path = os.path.join(abspath, search_value)
        return glob.glob(path, recursive=True)

    def _read_person_file(self, search_value):
        try:
            file_name = self._glob_fixture_file(search_value)[0]
        except IndexError:
            raise PersonNotFoundException()
        data = json.load(open(file_name))
        return Person().from_dict(data)

    def _read_person_files(self, search_value):
        file_names = self._glob_fixture_file(search_value)
        persons = []
        for file_name in file_names:
            persons.append(self._read_person_file(file_name))
        return persons

    def _paginate(self, values, page=None, page_size=None):
        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            values = values[offset:offset+page_size]
        return values

    def get_person_by_uwnetid(self, uwnetid):
        return self._read_person_file(f'**/*{uwnetid}*.json')

    def get_person_by_uwregid(self, uwregid):
        return self._read_person_file(f'**/*{uwregid}*.json')

    def get_person_by_student_number(self, student_number):
        return self._read_person_file(f'**/*{student_number}*.json')

    def get_persons(self, page=None, page_size=None):
        return self._paginate(
            self._read_person_files('**/**.json'),
            page=page,
            page_size=page_size)

    def get_active_students(self, page=None, page_size=None):
        return self._paginate(
            self._read_person_files('**/students/**.json'),
            page=page,
            page_size=page_size)

    def get_active_employees(self, page=None, page_size=None):
        return self._paginate(
            self._read_person_files('**/employees/**/*.json'),
            page=page,
            page_size=page_size)

    def get_advisers(self, advising_program=None):
        advisers = self._read_person_files('**/employees/advisers/*.json')
        if advising_program:
            filtered_advisers = []
            for person in advisers:
                if (person.employee.adviser.advising_program ==
                        advising_program):
                    filtered_advisers.append(person)
            return filtered_advisers
        else:
            return advisers

    def get_persons_by_adviser_netid(self, uwnetid):
        students = self.get_active_students()
        persons = []
        for person in students:
            for adviser in person.student.advisers:
                if adviser.uwnetid == uwnetid:
                    persons.append(person)
                    break
        return persons

    def get_persons_by_adviser_regid(self, uwregid):
        students = self.get_active_students()
        persons = []
        for person in students:
            for adviser in person.student.advisers:
                if adviser.uwregid == uwregid:
                    persons.append(person)
                    break
        return persons
