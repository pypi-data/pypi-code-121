from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, REAL
from sqlalchemy.orm import relationship

from univer_db.orm import get_base


Base = get_base()


class Sheet(Base):
    """
    Модель "Ведомость"
    """

    __tablename__ = 'univer_sheet'

    # Идентификатор
    id = Column('sheet_id', Integer, primary_key=True)

    # Тип ведомости
    sheet_type_id = Column(ForeignKey('univer_sheet_type.sheet_type_id'))
    sheet_type = relationship('SheetType')

    # Дата и время закрытия
    date_keep = Column(DateTime)

    # Группа
    group_id = Column(ForeignKey('univer_group.group_id'))
    group = relationship('Group')

    # Дата и время изменения
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<Sheet {}>'.format(self)

    def __str__(self):
        return str(self.id)


class SheetType(Base):
    """
    Тип ведомости
    """
    __tablename__ = 'univer_sheet_type'

    # Идентификатор
    id = Column('sheet_type_id', Integer, primary_key=True)

    # Наименование
    name_ru = Column('sheet_type_name_ru', String(200))
    name_kz = Column('sheet_type_name_kz', String(200))
    name_en = Column('sheet_type_name_en', String(200))

    # Короткое наименование
    short_name_ru = Column('sheet_type_short_name_ru', String)
    short_name_kz = Column('sheet_type_short_name_kz', String)
    short_name_en = Column('sheet_type_short_name_en', String)

    # Статус
    status = Column(Integer)

    def __repr__(self):
        return '<SheetType {} (id={} status={})>'.format(self, self.id, self.status)

    def __str__(self):
        return self.name_ru


class SheetResult(Base):
    """
    Результат ведомости
    """
    __tablename__ = 'univer_sheet_result'

    # Ведомость
    sheet_id = Column(ForeignKey('univer_sheet.sheet_id'), primary_key=True)
    sheet = relationship('Sheet')

    # Дисциплина
    subject_id = Column(ForeignKey('univer_subject.subject_id'))
    subject = relationship('Subject')

    # Преподаватель
    teacher_id = Column(ForeignKey('univer_teacher.teacher_id'))
    teacher = relationship('Teacher')

    # Академический год
    academ_year = Column(Integer)

    # Семестр академического кода
    semester = Column('semestr', Integer)

    # Контроль
    control_id = Column('control', ForeignKey(
        'univer_control.control_id'), primary_key=True)
    control = relationship('Controll')

    # Студент
    student_id = Column(ForeignKey(
        'univer_students.students_id'), primary_key=True)
    student = relationship('Student')

    # Результат
    result = Column(REAL)

    # Неизвестное поле
    date_keep = Column(DateTime)

    # Неизвестное поле
    P_P = Column(Integer)

    # Общий семестр
    n_seme = Column(Integer)

    # Неизвестное поле
    mark_sheet_result = Column(Integer)

    # Неизвестное поле
    retake_type = Column(Integer)

    def __repr__(self):
        return f'<SheetResult {self} (result={self.result})>'

    def __str__(self):
        return f'{self.sheet_id}'
