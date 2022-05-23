# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_person_client.databases.postgres import Postgres
from sqlalchemy import Table, Column, ForeignKey, TEXT, Integer
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship


class UWPDS(Postgres):

    Base = automap_base()

    def __init__(self, *args, **kwargs):
        UWPDS.Base.metadata.clear()
        super().__init__(*args, **kwargs)
        self.initialize_relationships()

    def initialize_relationships(self):
        student_to_sport = Table(
            'student_to_sport',
            UWPDS.Base.metadata,
            Column('student_id',
                   ForeignKey('student.id', ondelete="CASCADE"),
                   primary_key=True),
            Column('sport_id',
                   ForeignKey('sport.id', ondelete="CASCADE"),
                   primary_key=True)
        )

        student_to_adviser = Table(
            'student_to_adviser',
            UWPDS.Base.metadata,
            Column('student_id', ForeignKey('student.id', ondelete="CASCADE"),
                   primary_key=True),
            Column('adviser_id', ForeignKey('adviser.id', ondelete="CASCADE"),
                   primary_key=True)
        )

        student_to_major = Table(
            'student_to_major',
            UWPDS.Base.metadata,
            Column('student_id', ForeignKey('student.id', ondelete="CASCADE"),
                   primary_key=True),
            Column('major_id', ForeignKey('major.id', ondelete="CASCADE"),
                   primary_key=True)
        )

        student_to_intended_major = Table(
            'student_to_intended_major',
            UWPDS.Base.metadata,
            Column('student_id', ForeignKey('student.id', ondelete="CASCADE"),
                   primary_key=True),
            Column('major_id', ForeignKey('major.id', ondelete="CASCADE"),
                   primary_key=True)
        )

        Table(
            'historical_person',
            UWPDS.Base.metadata,
            Column('prior_uwnetid', TEXT(), primary_key=True),
            Column('prior_uwregid', TEXT(), primary_key=True),
            Column('id', Integer(), primary_key=True),
            autoload=True,
            autoload_with=self.engine
        )

        class Student(UWPDS.Base):
            __tablename__ = 'student'
            sport = relationship("sport",
                                 secondary=student_to_sport,
                                 cascade="all, delete")
            adviser = relationship("adviser",
                                   secondary=student_to_adviser,
                                   cascade="all, delete")
            major = relationship("major",
                                 secondary=student_to_major,
                                 cascade="all, delete")
            intended_major = relationship("major",
                                          secondary=student_to_intended_major,
                                          cascade="all, delete")
            transcript = relationship(
                "Transcript", back_populates="student", uselist=True)

        class Employee(UWPDS.Base):
            __tablename__ = 'employee'
            adviser = relationship(
                "adviser", back_populates="employee", uselist=False)

        class Transcript(UWPDS.Base):
            __tablename__ = 'transcript'
            tran_term_id = Column('tran_term_id',
                                  ForeignKey('term.id', ondelete="CASCADE"))
            tran_term = relationship("term", foreign_keys=[tran_term_id])
            leave_ends_term_id = Column('leave_ends_term_id',
                                        ForeignKey('term.id',
                                                   ondelete="CASCADE"))
            leave_ends_term = relationship("term",
                                           foreign_keys=[leave_ends_term_id])

        UWPDS.Base.prepare(self.engine, reflect=True)

        self.Person = UWPDS.Base.classes.person
        self.HistoricalPerson = UWPDS.Base.classes.historical_person
        self.PriorUWNetID = UWPDS.Base.classes.prior_uwnetids
        self.PriorUWRegID = UWPDS.Base.classes.prior_uwregids
        self.Student = Student
        self.Transcript = Transcript
        self.Employee = Employee
        self.Adviser = UWPDS.Base.classes.adviser
        self.StudentToAdviser = student_to_adviser
