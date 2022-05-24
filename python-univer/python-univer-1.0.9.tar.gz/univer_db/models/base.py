from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class PaymentForm(Base):
    """
    Модель "Форма оплаты"
    Статус: Выполняется
    """

    __tablename__ = 'univer_payment_forms'

    # Идентификатор
    id = Column('payment_form_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('payment_form_name_ru', String(100))
    name_kz = Column('payment_form_name_kz', String(100))
    name_en = Column('payment_form_name_en', String(100))

    # Краткое наименование
    short_name_ru = Column('payment_form_short_name_ru', String(100))
    short_name_kz = Column('payment_form_short_name_kz', String(100))
    short_name_en = Column('payment_form_short_name_en', String(100))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<PaymentForm {} (id={} status={})>'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class Stage(Base):
    """
    Модель "Ступень обучения"
    Статус: Выполняется
    """

    __tablename__ = 'univer_stage'

    # Идентификатор
    id = Column('stage_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Наименование
    name_kz = Column('stage_name_kz', String(200))
    name_ru = Column('stage_name_ru', String(200))
    name_en = Column('stage_name_en', String(200))

    def __repr__(self):
        return "<Stage {} (id={} status={})>".format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class EducationForm(Base):
    """
    Модель "Форма обучения"
    Статус: Выполняется
    """

    __tablename__ = 'univer_education_form'

    # Идентификатор
    id = Column('education_form_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Наименование
    name_kz = Column('education_form_name_kz', String(200))
    name_ru = Column('education_form_name_ru', String(200))
    name_en = Column('education_form_name_en', String(200))

    def __repr__(self):
        return "<EducationForm {} (id={} status={})>".format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class EduLevel(Base):
    """
    Модель "Уровень обучения"
    Статус: Выполняется
    """

    __tablename__ = 'univer_edu_levels'

    # Идентификатор
    id = Column('edu_level_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('edu_level_name_ru', String(100))
    name_kz = Column('edu_level_name_kz', String(100))
    name_en = Column('edu_level_name_en', String(100))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<EduLevel {} (id={} status={})'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class EnrollmentType(Base):
    """
    Модель "Тип поступления"
    Статус: Выполняется
    """

    __tablename__ = 'univer_enrollment_type'

    # Идентификатор
    id = Column('enrollment_type_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('enrollment_type_name_ru', String(100))
    name_kz = Column('enrollment_type_name_kz', String(100))
    name_en = Column('enrollment_type_name_en', String(100))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<EnrollmentType {} (id={} status={})>'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class Audience(Base):
    """
    Модель: Аудитория
    """

    __tablename__ = 'univer_audience'

    # Идентификатор
    id = Column('audience_id', Integer, primary_key=True)

    # Номер аудитории (На русском)
    number_ru = Column('audience_number_ru', String)

    # Номер аудитории (На казахском)
    number_kz = Column('audience_number_kz', String)

    # Номер аудитории (На английском))
    number_en = Column('audience_number_en', String)


class Citizenship(Base):
    """
    Гражданство
    """
    __tablename__ = 'univer_citizenship_1c'

    # Идентификатор
    id = Column('citizenship_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('citizenship_name_ru', String(500))
    name_kz = Column('citizenship_name_kz', String(500))
    name_en = Column('citizenship_name_en', String(500))

    # Короткое наименование
    short_name_ru = Column('citizenship_short_name_ru', String(500))
    short_name_kz = Column('citizenship_short_name_kz', String(500))
    short_name_en = Column('citizenship_short_name_en', String(500))

    # ISO-коды
    code = Column('citizenship_code', Integer)
    code2 = Column('citizenship_code2', String(250))
    code3 = Column('citizenship_code3', String(250))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<Citizenship {} (id={} code2={} status={})>'.format(self, self.id, self.code2, self.status)

    def __str__(self):
        return self.name_ru


class Nationality(Base):
    """
    Национальность
    """
    __tablename__ = 'univer_nationality'

    # Идентификатор
    id = Column('nationality_id', Integer, primary_key=True)

    # Статус
    status = Column(Integer)

    # Наименование
    name_ru = Column('nationality_name_ru', String(100))
    name_kz = Column('nationality_name_kz', String(100))
    name_en = Column('nationality_name_en', String(100))

    # Короткое наименование
    short_name_ru = Column('nationality_short_name_ru', String(20))
    short_name_kz = Column('nationality_short_name_kz', String(20))
    short_name_en = Column('nationality_short_name_en', String(20))

    def __repr__(self):
        return '<Nationality {} (id={} status={})>'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class Grant(Base):
    """
    Грант студента
    """
    __tablename__ = 'univer_grant'

    # Идентификатор
    id = Column('grant_id', Integer, primary_key=True)

    # Дата назначения гранта
    date_recieved = Column('grant_date_recieved', DateTime)

    # Номер гранта
    number = Column('grant_number', String(15))

    # Студент
    student_id = Column(ForeignKey('univer_students.students_id'))
    student = relationship('Student')

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<Grant {} (id={} student={} status={})>'.format(self, self.id, self.student_id, self.status)

    def __str__(self):
        return f'Грант - {self.student}: {self.number} ({self.date_recieved})'


class Contract(Base):
    """
    Договор студента
    """
    __tablename__ = 'univer_contract'

    # Идентификатор
    id = Column('contract_id', Integer, primary_key=True)

    # Номер договора
    number = Column('contract_number', String(50))

    # Дата начало договора
    date_recieved = Column('contract_date_recieved', DateTime)

    # Студент
    student_id = Column('students_id', ForeignKey(
        'univer_students.students_id'))
    student = relationship('Student')

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<Contract {} (id={} student={} status={})>'.format(self, self.id, self.student_id, self.status)

    def __str__(self):
        return f'Договор - {self.student}: {self.number} ({self.date_recieved})'


class FamilyStatus(Base):
    """
    Семейное положение
    """
    __tablename__ = 'univer_family_status_1c'

    # Идентификатор
    id = Column('family_status_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('family_status_name_ru', String(500))
    name_kz = Column('family_status_name_kz', String(500))
    name_en = Column('family_status_name_en', String(500))

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<FamilyStatus {} (id={} status={})>'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru
