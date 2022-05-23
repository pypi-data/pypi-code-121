# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


class AbstractUWPersonClient():

    def get_person_by_uwnetid(self, uwnetid):
        raise NotImplementedError()

    def get_person_by_uwregid(self, uwregid):
        raise NotImplementedError()

    def get_person_by_student_number(self, student_number):
        raise NotImplementedError()

    def get_persons(self, page=None, page_size=None):
        raise NotImplementedError()

    def get_active_students(self, page=None, page_size=None):
        raise NotImplementedError()

    def get_active_employees(self, page=None, page_size=None):
        raise NotImplementedError()

    def get_advisers(self, advising_program=None):
        raise NotImplementedError()

    def get_persons_by_adviser_netid(self, uwnetid):
        raise NotImplementedError()

    def get_persons_by_adviser_regid(self, uwregid):
        raise NotImplementedError()
