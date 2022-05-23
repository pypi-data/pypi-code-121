from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, JSON, ARRAY
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from .orm import get_base


Base = get_base()


class BrandConfig(Base):
    """
    Неизвестная модель
    """
    __tablename__ = 'brand_configs'

    # MD5-хеш
    md5 = Column(String(32), primary_key=True)

    # Переменные
    # YAML-формат
    variables = Column(String)

    # Неизвестное поле
    share = Column(Boolean)

    # Наименование
    name = Column(String(255))

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Неизвестное поле
    js_overrides = Column(String)

    # Неизвестное поле
    css_overrides = Column(String)

    # Неизвестное поле
    mobile_js_overrides = Column(String)

    # Неизвестное поле
    mobile_css_overrides = Column(String)

    # Неизвестное поле
    parent_md5 = Column(String(255))

    def __repr__(self):
        return f'<BrandConfig {self} (md5={self.md5})>'

    def __str__(self):
        return f'{self.name}'


class Account(Base):
    """
    Учетная запись
    """
    __tablename__ = 'accounts'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    name = Column(String(255))

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Статус
    # Возможные значения:
    # - active (Активный)
    # - deleted (Удаленный)
    workflow_state = Column(String(255), default='active')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state могут быть следующие значения:
        - active (Активный)
        - deleted (Удаленный)
        """
        assert value in ['active', 'deleted']
        return value

    # Дата и время удаления
    # deleted_at необходимо ставить когда workflow_state='deleted'
    deleted_at = Column(DateTime)

    @validates('deleted_at')
    def validate_deleted_at(self, key, value):
        """
        deleted_at необходимо ставить когда workflow_state='deleted'
        """
        if self.workflow_state == 'deleted':
            assert value is not None

        return value

    # Родительская учетная запись
    parent_account_id = Column(ForeignKey('accounts.id'))
    parent_account = relationship('Account', foreign_keys=[parent_account_id])

    # SIS-идентификатор
    sis_source_id = Column(String(255))

    # Неизвестное поле
    sis_batch_id = Column(Integer)

    # Неизвестное поле
    current_sis_batch_id = Column(Integer)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account', foreign_keys=[root_account_id])

    # Неизвестное поле
    last_successful_sis_batch_id = Column(Integer)

    # Неизвестное поле
    membership_types = Column(String(255))

    # Временная зона по-умолчанию
    default_time_zone = Column(String(255))

    # Неизвестное поле
    external_status = Column(String(255))

    # Неизвестное поле
    storage_quota = Column(Integer)

    # Неизвестное поле
    default_storage_quota = Column(Integer)

    # Неизвестное поле
    enable_user_notes = Column(Boolean)

    # Неизвестное поле
    allowed_services = Column(String(255))

    # Неизвестное поле
    turnitin_pledge = Column(String)

    # Неизвестное поле
    turnitin_comments = Column(String)

    # Неизвестное поле
    turnitin_account_id = Column(String(255))

    # Неизвестное поле
    turnitin_salt = Column(String(255))

    # Неизвестное поле
    turnitin_crypted_secret = Column(String(255))

    # Неизвестное поле
    show_section_name_as_course_name = Column(Boolean)

    # Неизвестное поле
    allow_sis_import = Column(Boolean)

    # Неизвестное поле
    equella_endpoint = Column(String(255))

    # Настройки
    # YAML-формат
    settings = Column(String)

    # UUID-идентификатор
    uuid = Column(String(255))

    # Язык по-умолчанию
    default_locale = Column(String(255))

    # Неизвестное поле
    stuck_sis_fields = Column(String)

    # Неизвестное поле
    default_user_storage_quota = Column(Integer)

    # LTI-идентификатор
    lti_guid = Column(String(255))

    # Неизвестное поле
    default_group_storage_quota = Column(Integer)

    # Неизвестное поле
    turnitin_host = Column(String(255))

    # Неизвестное поле
    integration_id = Column(String(255))

    # Неизвестное поле
    lti_context_id = Column(String(255))

    # Неизвестный модель (BrandConfig)
    brand_config_md5 = Column(ForeignKey('brand_configs.md5'))
    brand_config = relationship('BrandConfig')

    # Неизвестное поле
    turnitin_originality = Column(String(255))

    # Неизвестное поле
    latest_outcome_import_id = Column(Integer)

    # Неизвестное поле
    course_template_id = Column(Integer)

    def __repr__(self):
        return '<Account {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.name


class Wiki(Base):
    """
    Wiki
    """
    __tablename__ = 'wikis'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    title = Column(String(255))

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Неизвестное поле
    front_page_url = Column(String)

    # Неизвестное поле
    has_no_front_page = Column(Boolean)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    def __repr__(self):
        return f'<Wiki {self} (id={self.id})>'

    def __str__(self):
        return f'{self.title}'


class EnrollmentTerm(Base):
    """
    Модель "EnrollmentTerm"
    """
    __tablename__ = 'enrollment_terms'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    # Наименование
    name = Column(String(255))

    def __repr__(self):
        return '<EnrollmentTerm {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.name


class SisBatch(Base):
    """
    Модель "SisBatch"
    """
    __tablename__ = 'sis_batches'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return '<SisBatch {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.id


class Role(Base):
    """
    Модель "Роли"
    """
    __tablename__ = 'roles'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    name = Column(String(255))

    def __repr__(self):
        return '<Role {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.name


class Course(Base):
    """
    Модель "Курс"
    """
    __tablename__ = 'courses'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование курса
    name = Column(String(255))

    # Учетная запись
    account_id = Column(ForeignKey('accounts.id'))
    account = relationship('Account', foreign_keys='Course.account_id')

    group_weighting_scheme = Column(String(255))

    # Статус
    workflow_state = Column(String(255))

    # Уникальный идентификатор
    uuid = Column(String(255))

    start_at = Column(DateTime)

    conclude_at = Column(DateTime)

    grading_standard_id = Column(Integer)

    # Публичный
    is_public = Column(Boolean)

    allow_student_wiki_edits = Column(Boolean)

    # Дата и время создания
    created_at = Column(DateTime)

    # Дата и время изменения
    updated_at = Column(DateTime)

    show_public_context_messages = Column(Boolean)

    syllabus_body = Column(String)

    allow_student_forum_attachments = Column(Boolean)

    default_wiki_editing_roles = Column(String(255))

    # Wiki
    wiki_id = Column(ForeignKey('wikis.id'))
    wiki = relationship('Wiki')

    allow_student_organized_groups = Column(Boolean)

    # Код курса
    course_code = Column(String(255))

    # Вид по-умолчанию
    default_view = Column(String(255))

    abstract_course_id = Column(Integer)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship(
        'Account', foreign_keys='Course.root_account_id')

    enrollment_term_id = Column(ForeignKey('enrollment_terms.id'))
    enrollment_term = relationship('EnrollmentTerm')

    # SIS-идентификатор
    sis_source_id = Column(String(255))

    sis_batch_id = Column(ForeignKey('sis_batches.id'))
    sis_batch = relationship('SisBatch')

    open_enrollment = Column(Boolean)

    storage_quota = Column(Integer)

    tab_configuration = Column(String)

    # Разрешить комментарии к Wiki
    allow_wiki_comments = Column(Boolean)

    turnitin_comments = Column(String)

    self_enrollment = Column(Boolean)

    # Лицензия
    license = Column(String(255))

    indexed = Column(Boolean)

    restrict_enrollments_to_course_dates = Column(Boolean)

    template_course_id = Column(Integer)

    # Локализация
    locale = Column(String(255))

    # Настройки курса
    settings = Column(String)

    replacement_course_id = Column(Integer)

    stuck_sis_fields = Column(String)

    # Публичное описание
    public_description = Column(String)

    self_enrollment_code = Column(String(255))

    self_enrollment_limit = Column(Integer)

    integration_id = Column(String(255))

    # Временная зона
    time_zone = Column(String(255))

    lti_context_id = Column(String(255))

    turnitin_id = Column(Integer)

    show_announcements_on_home_page = Column(Boolean)

    home_page_announcement_limit = Column(Integer)

    latest_outcome_import_id = Column(Integer)

    grade_passback_setting = Column(String(255))

    def __repr__(self):
        return '<Course {} (id={}, sis_source_id={})>'.format(self, self.id, self.sis_source_id)

    def __str__(self):
        return self.name


class CourseSection(Base):
    """
    Модель "Секция курса"
    """
    __tablename__ = 'course_sections'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # SIS-идентификатор
    sis_source_id = Column(String(255))

    sis_batch_id = Column(ForeignKey('sis_batches.id'))
    sis_batch = relationship('SisBatch')

    # Курс
    course_id = Column(ForeignKey('courses.id'))
    course = relationship('Course')

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    enrollment_term_id = Column(ForeignKey('enrollment_terms.id'))
    enrollment_term = relationship('EnrollmentTerm')

    # Наименование
    name = Column(String(255))

    # Секция по-умолчанию
    default_section = Column(Boolean)

    accepting_enrollments = Column(Boolean)

    can_manually_enroll = Column(Boolean)

    start_at = Column(DateTime)
    end_at = Column(DateTime)

    # Дата и время создания
    created_at = Column(DateTime)

    # Дата и время изменения
    updated_at = Column(DateTime)

    # Статус
    # active - Активный
    # deleted - Удаленный
    workflow_state = Column(String(255))

    restrict_enrollments_to_section_dates = Column(Boolean)

    nonxlist_course_id = Column(Integer)

    stuck_sis_fields = Column(String)

    integration_id = Column(String(255))

    def __repr__(self):
        return '<CourseSection {} (id={}, sis_source_id={})>'.format(self, self.id, self.sis_source_id)

    def __str__(self):
        return self.name


class ContextModule(Base):
    """
    Модель "Модули курса"
    """

    __tablename__ = 'context_modules'

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer)
    context_type = Column(String(255))
    name = Column(String)
    position = Column(Integer)
    workflow_state = Column(String(255))

    def __repr__(self):
        return '<ContextModule {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.name


class ContentTag(Base):
    __tablename__ = 'content_tags'

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer)
    content_type = Column(String(255))
    title = Column(String)
    context_module_id = Column(ForeignKey('context_modules.id'))
    context_module = relationship('ContextModule')
    workflow_state = Column(String(255))

    def __repr__(self):
        return '<ContentTag {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.title


class Score(Base):
    """
    Модель "Оценки"
    """

    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    enrollment_id = Column(ForeignKey('enrollments.id'))
    workflow_state = Column(String(255))
    current_score = Column(Float)
    final_score = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<Score {} (id={})>'.format(self, self.id)

    def __str__(self):
        return self.current_score


class Submission(Base):
    """
    Отправленные работы задании
    """
    __tablename__ = 'submissions'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Неизвестное поле
    body = Column(String)

    # Неизвестное поле
    url = Column(String(255))

    # Неизвестное поле
    attachment_id = Column(Integer)

    # Оценка (В виде строки)
    grade = Column(String(255))

    # Оценка (В виде числа)
    score = Column(Float)

    # Дата и время отправления
    submitted_at = Column(DateTime)

    # Задание
    assignment_id = Column(ForeignKey('assignments.id'))
    assignment = relationship('Assignment')

    # Пользователь
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User')

    # Тип отправки
    # Способ по которому студент отправил свои работы
    # Возможные значения:
    # - online_quiz (Контрольная работа)
    # - online_text_entry (Текстовая запись)
    # - online_upload (Загрузки файла)
    # - online_url (URL-адрес веб-сайта)
    submission_type = Column(String(255))

    @validates('submission_type')
    def validate_submission_type(self, key, value):
        """
        Значением submission_type могут быть следующие значения:
        - online_quiz (Контрольная работа)
        - online_text_entry (Текстовая запись)
        - online_upload (Загрузки файла)
        - online_url (URL-адрес веб-сайта)
        """
        if value:
            assert value in ['online_quiz', 'online_text_entry',
                             'online_upload', 'online_url']

        return value

    # Статус
    # Возможные значения:
    # - deleted (Удален)
    # - graded (Оценка поставлен)
    # - pending_review (Требуется просмотр от преподавателя)
    # - submitted (Студент отправил свою работу)
    # - unsubmitted (Студент еще не отправил свою работу)
    workflow_state = Column(String(255), default='unsubmitted')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state могут быть следующие значения:
        - deleted (Удален)
        - graded (Оценка поставлен)
        - pending_review (Требуется просмотр от преподавателя)
        - submitted (Студент отправил свою работу)
        - unsubmitted (Студент еще не отправил свою работу)
        """
        assert value in ['deleted', 'graded',
                         'pending_review', 'submitted', 'unsubmitted']
        return value

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Неизвестное поле
    group_id = Column(Integer)

    # Неизвестное поле
    attachment_ids = Column(String)

    # Неизвестное поле
    processed = Column(Boolean)

    # Неизвестное поле
    grade_matches_current_submission = Column(Boolean)

    # Опубликованная оценка в виде строки (Неизвестное поле)
    # В основном совпадает с полем score
    published_score = Column(String(255))

    # Опубликованная оценка в виде числа (Неизвестное поле)
    # В основном совпадает с полем grade
    published_grade = Column(Integer)

    # Дата и время оценки преподавателем
    graded_at = Column(DateTime)

    # Неизвестное поле
    student_entered_score = Column(String(255))

    # Преподаватель который поставил оценку
    # Почему-то есть значения с минусами (Неизвестное значение)
    grader_id = Column(Integer)

    # Неизвестное поле
    media_comment_id = Column(String(255))

    # Неизвестное поле
    media_comment_type = Column(String(255))

    # Идентификатор отправленной студентом контрольной работы
    # Доступен, если задание представляет собой Контрольную работу
    quiz_submission_id = Column(Integer)

    # Неизвестное поле
    submission_comments_count = Column(Integer)

    # Текущая попытка
    attempt = Column(Integer)

    # Неизвестное поле
    media_object_id = Column(Integer)

    # Данные TurnItIn
    # В основном не используется
    turnitin_data = Column(String)

    # Неизвестное поле
    cached_due_date = Column(DateTime)

    # Состояние - По уважительной причине
    # Проставляется если студент не смог выполнить задание по уважительной причине
    excused = Column(Boolean)

    # Анонимно оценен
    graded_anonymously = Column(Boolean)

    # Состояние отправки задания
    # Преподы могут поставить оценку и поставить состояние данной оценки
    # Возможные значения:
    # - late (Поздний) - Задание выполнили поздно
    # - missing (Отсутствующий) - Задание не выполнили
    # - none (Нет) - Отсутствует какое-либо состояние
    late_policy_status = Column(String(255))

    @validates('late_policy_status')
    def validate_late_policy_status(self, key, value):
        if value:
            assert value in ['late', 'missing', 'none']

        return value

    # Неизвестное поле
    points_deducted = Column(Integer)

    # Неизвестное поле
    grading_period_id = Column(Integer)

    # Неизвестное поле
    seconds_late_override = Column(Integer)

    # LTI-идентификатор пользователя
    lti_user_id = Column(String(255))

    # Идентификатор анонимности
    anonymous_id = Column(String(255))

    # Дата и время последнего комментария
    last_comment_at = Column(DateTime)

    # Количество дополнительных попыток
    extra_attempts = Column(Integer)

    # Неизвестное поле
    posted_at = Column(DateTime)

    # Неизвестное поле
    cached_quiz_lti = Column(Boolean, default=False)

    # Неизвестное поле
    cached_tardiness = Column(String(16))

    # Курс
    course_id = Column(ForeignKey('courses.id'))
    course = relationship('Course')

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    # Неизвестное поле
    redo_request = Column(Boolean, default=False)

    # Неизвестное поле
    resource_link_lookup_uuid = Column(String(255))

    def __repr__(self):
        return f'<Submission {self} (id={self.id} assignment_id={self.assignment_id} user_id={self.user_id})>'

    def __str__(self):
        return f'{self.score}'


class GradingStandard(Base):
    """
    Стандарт оценки
    """
    __tablename__ = 'grading_standards'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    title = Column(String(255))

    # Данные
    # Является YAML-форматом
    data = Column(String)

    # Идентификатор контекста
    context_id = Column(Integer)

    # Тип контекста
    # Возможные значения:
    # - Account (Учетная запись)
    context_type = Column(String(255))

    @validates('context_type')
    def validate_context_type(self, key, value):
        """
        Значением context_type может быть следующие значения:
        - Account (Учетная запись)
        """
        assert value in ['Account']
        return value

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Пользователь
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User')

    # Неизвестное поле
    usage_count = Column(Integer)

    # Код контекста
    # Основном имеет вид "account_1" и т.д.
    context_code = Column(String(255))

    # Статус
    # Возможные значения:
    # - active
    workflow_state = Column(String(255), default='active')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        assert value in ['active']
        return value

    # Неизвестное поле
    migration_id = Column(Integer)

    # Версия (Неизвестное поле)
    version = Column(Integer)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    def __repr__(self):
        return f'<GradingStandard {self} (id={self.id} context_id={self.context_id} context_type={self.context_type} workflow_state={self.workflow_state})>'

    def __str__(self):
        return f'{self.title}'


class AssignmentGroup(Base):
    """
    Группа задании
    """
    __tablename__ = 'assignment_groups'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    name = Column(String(255))

    # Правила (Неизвестное поле)
    rules = Column(String)

    # Наименование задании по-умолчанию
    # При создании задании в этом группе, они по-умолчанию получают это наименование
    default_assignment_name = Column(String(255))

    # Позиция
    # Позиция по которому они расположены в списке. Чем меньше значение, тем выше они расположены в списке
    # Необходимо учитывать также позиции других объектов в списке и не должны совпадать с ними
    position = Column(Integer)

    # Неизвестное поле
    assignment_weighting_scheme = Column(String(255))

    # Неизвестное поле
    group_weight = Column(Integer)

    # Идентификатор контекста
    context_id = Column(Integer)

    # Тип контекста
    # Возможные значения:
    # - Course (Курс)
    context_type = Column(String(255))

    @validates('context_type')
    def validate_context_type(self, key, value):
        """
        Значением context_type может быть следующие значения:
        - Course (Курс)
        """
        assert value in ['Course']
        return value

    # Статус
    # Возможные значения:
    # - available (Доступен)
    # - deleted (Удален)
    workflow_state = Column(String(255), default='available')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state может быть следующие значения:
        - available (Доступен)
        - deleted (Удален)
        """
        assert value in ['available', 'deleted']
        return value

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Неизвестное поле
    cloned_item_id = Column(Integer)

    # Код контекста
    # В основном выглядит как "course_6295", "course_18121" и т.д.
    context_code = Column(String(255))

    # Неизвестное поле
    migration_id = Column(String(255))

    # SIS-идентификатор
    # Идентификатор часто используемый в SIS-импорте
    sis_source_id = Column(String(255))

    # Неизвестное поле
    integration_data = Column(String)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    def __repr__(self):
        return f'<AssignmentGroup {self} (id={self.id} context_id={self.context_id} context_type={self.context_type} workflow_state={self.workflow_state})>'

    def __str__(self):
        return f'{self.name}'


class Assignment(Base):
    """
    Задание
    """
    __tablename__ = 'assignments'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    title = Column(String(255))

    # Описание
    description = Column(String)

    # Срок выполнения
    # Срок до которой студенты должны выполнить это задание
    due_at = Column(DateTime)

    # Доступно с
    # Срок после которой студентам будет разрешено выполнить это задание
    # Студенты не смогут начать выполнение задания до этого времени
    unlock_at = Column(DateTime)

    # Доступно до
    # Срок после которой студентам будет запрещено выполнить это задание
    lock_at = Column(DateTime)

    # Максимальный балл
    # Максимальный балл преподаватели который могут поставить студенту
    points_possible = Column(Float, default=0)

    # Неизвестное поле (Возможно минимальный балл)
    min_score = Column(Float)

    # Неизвестное поле (Возможно максимальный балл)
    max_score = Column(Float)

    # Неизвестное поле
    mastery_score = Column(Float)

    # Тип оценки
    # Возможные значения:
    # - percent (Процент)
    # - pass_fail (Завершено/Не завершено)
    # - points (Баллы)
    # - letter_grade (Успеваемость)
    # - gpa_scale (Шкала GPA)
    # - not_graded (Оценка не выставлена)
    grading_type = Column(String(255))

    @validates('grading_type')
    def validate_grading_type(self, key, value):
        """
        Значением grading_type может быть следующие значения
        - percent (Процент)
        - pass_fail (Завершено/Не завершено)
        - points (Баллы)
        - letter_grade (Успеваемость)
        - gpa_scale (Шкала GPA)
        - not_graded (Оценка не выставлена)

        Основным типом в Yessenov University используется "points"
        """
        assert value in ['percent', 'pass_fail', 'points',
                         'letter_grade', 'gpa_scale', 'not_graded']
        return value

    # Тип отправки
    # Способы по которому студенту разрешено отправлить работу
    # Разрешено выбрать несколько значении в пределах этих значении (online_text_entry, online_upload, online_url)
    # Возможные значения:
    # - discussion_topic (???)
    # - external_tool (Внешний инструмент)
    # - none (Нет отправки)
    # - not_graded (Оценка не выставлена)
    # - on_paper (На бумаге)
    # - online_quiz (Контрольная работа)
    # - online_text_entry (Текстовая запись)
    # - online_upload (Загрузки файла)
    # - online_url (URL-адрес веб-сайта)
    submission_types = Column(String(255))

    @validates('submission_types')
    def validate_submission_types(self, key, value):
        """
        Значением submission_types может быть следующие значениям:
        - discussion_topic (???)
        - external_tool (Внешний инструмент)
        - none (Нет отправки)
        - not_graded (Оценка не выставлена)
        - on_paper (На бумаге)
        - online_quiz (Контрольная работа)
        - online_text_entry (Текстовая запись)
        - online_upload (Загрузки файла)
        - online_url (URL-адрес веб-сайта)

        Причем online_text_entry, online_upload и online_url могут быть вместе указаны с помощью запятой ",".
        """
        if ',' in value:
            value_types = value.split(',')
            for value_type in value_types:
                assert value_type in ['online_text_entry',
                                      'online_upload', 'online_url']
        else:
            assert value in ['discussion_topic', 'external_tool', 'none', 'not_graded',
                             'on_paper', 'online_quiz', 'online_text_entry', 'online_upload', 'online_url']

        return value

    # Статус
    # Возможные значения:
    # - published (Опубликован)
    # - unpublished (Не опубликован)
    # - deleted (Удален)
    workflow_state = Column(String(255), default='unpublished')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state могут быть следующие значениям:
        - published (Опубликан)
        - unpublished (Не публикован)
        - deleted (Удален)
        """
        assert value in ['published', 'unpublished', 'deleted']
        return value

    # Идентификатор контекста
    context_id = Column(Integer)

    # Тип контекста
    # Возможные значения:
    # - Course (Курс)
    context_type = Column(String(255))

    @validates('context_type')
    def validate_context_type(self, key, value):
        """
        Значением context_type могут быть следующие значения:
        - Course (Курс)
        """
        assert value in ['Course']
        return value

    # Группа задании
    assignment_group_id = Column(ForeignKey('assignment_groups.id'))
    assignment_group = relationship('AssignmentGroup')

    # Стандарты оценки
    grading_standard_id = Column(ForeignKey('grading_standards.id'))
    grading_standard = relationship('GradingStandard')

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Неизвестное поле
    group_category = Column(String(255))

    # Неизвестное поле
    submissions_downloads = Column(Integer)

    # Неизвестное поле
    peer_review_count = Column(Integer)

    # Неизвестное поле
    peer_reviews_due_at = Column(DateTime)

    # Неизвестное поле
    peer_reviews_assigned = Column(Boolean)

    # Неизвестное поле
    peer_reviews = Column(Boolean)

    # Неизвестное поле
    automatic_peer_reviews = Column(Boolean)

    # Неизвестное поле
    all_day = Column(Boolean)

    # Неизвестное поле
    all_day_date = Column(Date)

    # Неизвестное поле
    could_be_locked = Column(Boolean)

    # Неизвестное поле
    cloned_item_id = Column(Integer)

    # Код контекста
    # Имеет в основном вид "course_26939", "course_24569" и т.д.
    context_code = Column(String(255))

    # Позиция в списке
    # Показывает порядок позиции в списке, чем меньше значение тем выше он находится
    # Необходимо учитывать порядок других задании находящихся в одном списке, не должно быть совпадении
    position = Column(Integer)

    # Неизвестное поле
    migration_id = Column(String(255))

    # Неизвестное поле
    grade_group_students_individually = Column(Boolean)

    # Неизвестное поле
    anonymous_peer_reviews = Column(Boolean)

    # Неизвестное поле
    time_zone_edited = Column(String(255))

    # Включен TurnItIn
    # В основном не используется
    turnitin_enabled = Column(Boolean)

    # Неизвестное поле
    allowed_extensions = Column(String(255))

    # Настройки TurnItIn
    # В основном не используется
    turnitin_settings = Column(String)

    # Неизвестное поле
    muted = Column(Boolean)

    # Неизвестное поле
    group_category_id = Column(Integer)

    # Неизвестное поле
    freeze_on_copy = Column(Boolean)

    # Неизвестное поле
    copied = Column(Boolean)

    # Неизвестное поле
    only_visible_to_overrides = Column(Boolean)

    # Неизвестное поле
    post_to_sis = Column(Boolean)

    # Неизвестное поле
    integration_id = Column(Integer)

    # Неизвестное поле
    integration_data = Column(String)

    # Идентификатор TurnItIn
    # В основном не используется
    turnitin_id = Column(Integer)

    # Неизвестное поле
    moderated_grading = Column(Boolean)

    # Неизвестное поле
    grades_published_at = Column(DateTime)

    # Не учитывать это задание при подсчете итоговой оценки
    omit_from_final_grade = Column(Boolean)

    # Включить Vericite
    # В основном не используется
    vericite_enabled = Column(Boolean)

    # Неизвестное поле
    intra_group_peer_reviews = Column(Boolean)

    # LTI-идентификатор
    # Используется для взаимодействия с LTI-приложениями
    lti_context_id = Column(String(255))

    # Неизвестное поле
    anonymous_instructor_annotations = Column(Boolean)

    # Неизвестное поле
    duplicate_of_id = Column(Integer)

    # Анонимное Оценивание
    # Оценщики не могут просматривать имена студентов
    anonymous_grading = Column(Boolean)

    # Неизвестное поле
    graders_anonymous_to_graders = Column(Boolean)

    # Неизвестное поле
    grader_count = Column(Integer)

    # Неизвестное поле
    grader_comments_visible_to_graders = Column(Boolean)

    # Неизвестное поле
    grader_section_id = Column(Integer)

    # Неизвестное поле
    final_grader_id = Column(Integer)

    # Неизвестное поле
    grader_names_visible_to_final_grader = Column(Boolean)

    # Неизвестное поле
    duplication_started_at = Column(DateTime)

    # Неизвестное поле
    importing_started_at = Column(DateTime)

    # Число попыток отправки
    # Если значение отсутствует - то Неограничено
    allowed_attempts = Column(Integer)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    # SIS-идентификатор
    # Идентификатор используемый в SIS-импорте
    sis_source_id = Column(String(255))

    # Неизвестное поле
    migrate_from_id = Column(Integer)

    # Настройки задания
    # В JSON-формате
    settings = Column(JSON)

    # Неизвестное поле
    annotatable_attachment_id = Column(Integer)

    def __repr__(self):
        return f'<Assignment {self} (id={self.id} workflow_state={self.workflow_state})>'

    def __str__(self):
        return f'{self.title}'


class QuestionBank(Base):
    """
    Банк вопросов
    """
    __tablename__ = 'assessment_question_banks'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Идентификатор контекста
    context_id = Column(Integer)

    # Тип контекста
    # Возможные значения:
    # - Course (Курс)
    # - Account (Учетная запись)
    context_type = Column(String(255))

    @validates('context_type')
    def validate_context_type(self, key, value):
        """
        Значением context_type может быть один из этих значении:
        - Course (Курс)
        - Account (Учетная запись)
        """
        assert value in ['Course', 'Account']
        return value

    # Наименование
    title = Column(String(255))

    # Статус
    # Возможные значения:
    # - active (Активный)
    # - deleted (Удален)
    workflow_state = Column(String(255), default='active')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state может быть один из этих значении:
        - active (Активный)
        - deleted (Удален)
        """
        assert value in ['active', 'deleted']
        return value

    # Дата и время удаления
    deleted_at = Column(DateTime)

    @validates('deleted_at')
    def validate_deleted_at(self, key, value):
        """
        deleted_at обязателен, если workflow_state='deleted'
        """
        if self.workflow_state == 'deleted':
            assert value is not None

        return value

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Неизвестное поле (Возможно идентификатор миграции)
    migration_id = Column(String(255))

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    def __repr__(self):
        return f'<QuestionBank {self} (id={self.id} context_id={self.context_id} context_type={self.context_type} workflow_state={self.workflow_state})>'

    def __str__(self):
        return f'{self.title}'


class Question(Base):
    """
    Вопрос
    """
    __tablename__ = 'assessment_questions'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    name = Column(String(255))

    # Данные вопроса
    # В формате YAML
    question_data = Column(String)

    # Идентификатор контекста
    context_id = Column(Integer)

    # Тип контекста
    context_type = Column(String(255))

    # Статус
    # Возможные значения:
    # - active (Активный)
    # - deleted (Удален)
    workflow_state = Column(String(255))

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state может быть следующие значения:
        - active (Активный)
        - deleted (Удален)
        """
        assert value in ['active', 'deleted']
        return value

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Банк вопросов
    question_bank_id = Column(
        'assessment_question_bank_id', ForeignKey('assessment_question_banks.id'))
    question_bank = relationship('QuestionBank')

    # Дата и время удаления
    # Обязательно, если workflow_state="deleted"
    deleted_at = Column(DateTime)

    @validates('deleted_at')
    def validate_deleted_at(self, key, value):
        if self.workflow_state == 'deleted':
            assert value is not None

        return value

    # Неизвестное поле
    migration_id = Column(String(255))

    # Позиция в банке вопросов
    # Определяет в каком позиции находится данный вопрос в списке вопросов внутри банка вопросов
    # Чем меньше значение, тем выше он находится
    # Не должен совпадать с значениями другим вопросов в пределах банка вопросов
    position = Column(Integer)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    def __repr__(self):
        return f'<Question {self} (id={self.id} question_bank_id={self.question_bank_id} workflow_state={self.workflow_state})>'

    def __str__(self):
        return f'{self.name}'


class Override(Base):
    """
    Модель "Назначение"
    """
    __tablename__ = 'assignment_overrides'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    assignment_id = Column(ForeignKey('assignments.id'))
    assignment = relationship('Assignment')
    assignment_version = Column(Integer)
    set_type = Column(String)
    set_id = Column(Integer)
    title = Column(String)
    workflow_state = Column(String)
    due_at_overridden = Column(Boolean)
    due_at = Column(DateTime)
    all_day = Column(Boolean)
    all_day_date = Column(DateTime)
    unlock_at_overridden = Column(Boolean)
    unlock_at = Column(DateTime)
    lock_at_overridden = Column(Boolean)
    lock_at = Column(DateTime)
    quiz_id = Column(ForeignKey('quizzes.id'))
    quiz = relationship('Quiz')
    quiz_version = Column(Integer)

    def __repr__(self):
        return '<Override {} (id={} assignment_id={} workflow_state={} quiz_id={})>'.format(self, self.id, self.assignment_id, self.workflow_state, self.quiz_id)

    def __str__(self):
        return self.title


class OverrideStudent(Base):
    """
    Модель "Студент в Назначении"
    """
    __tablename__ = 'assignment_override_students'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    assignment_id = Column(ForeignKey('assignments.id'))
    assignment = relationship('Assignment')
    override_id = Column('assignment_override_id',
                         ForeignKey('assignment_overrides.id'))
    override = relationship('Override')
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User')
    quiz_id = Column(ForeignKey('quizzes.id'))
    quiz = relationship('Quiz')
    workflow_state = Column(String)

    def __repr__(self):
        return '<OverrideStudent {} (id={} assignment_id={} override_id={} user_id={} quiz_id={} workflow_state={}>'.format(self, self.id, self.assignment_id, self.override_id, self.user_id, self.quiz_id, self.workflow_state)

    def __str__(self):
        return str(self.user)


class User(Base):
    """
    Пользователь
    """
    __tablename__ = 'users'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Полное имя (ФИО)
    name = Column(String(255))

    # Полное имя для сортировки
    sortable_name = Column(String(255))

    # Короткое имя
    short_name = Column(String(255))

    # Статус
    # Возможные значения:
    # - pre_registered (???)
    # - registered (Зарегистрирован)
    # - creation_pending (???)
    # - deleted (Удален)
    workflow_state = Column(String(255), default='registered')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state может быть следующие значения:
        - pre_registered (???)
        - registered (Зарегистрирован)
        - creation_pending (???)
        - deleted (Удален)
        """
        assert value in ['pre_registered',
                         'registered', 'creation_pending', 'deleted']
        return value

    # Временная зона
    # Необходимо написать на английском
    # Пример: Almaty, Astana, Baku, Berlin, Ekaterinburg, Islamabad, Moscow и т.д.
    time_zone = Column(String(255))

    # Уникальные UUID-идентификатор
    uuid = Column(String(255))

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # URL-адрес изображения к аватару (Фото пользователя)
    avatar_image_url = Column(String(255))

    # Источник аватара (Фото пользователя)
    # Возможные значения:
    # - attachment
    # - gravatar
    # - no_pic
    avatar_image_source = Column(String(255))

    @validates('avatar_image_source')
    def validate_avatar_image_source(self, key, value):
        if value:
            assert value in ['attachment', 'gravatar', 'no_pic']

        return value

    # Дата и время изменения аватара (Фото пользователя)
    # Если аватар изменился, нужно поменять дату и время
    avatar_image_updated_at = Column(DateTime)

    # Номер телефона
    phone = Column(String(255))

    # Наименование школы
    school_name = Column(String(255))

    # Позиция школы (???)
    school_position = Column(String(255))

    # Дата и время удаления
    # Обязателен, если workflow_state="deleted"
    deleted_at = Column(DateTime)

    @validates('deleted_at')
    def validate_deleted_at(self, key, value):
        if self.workflow_state == 'deleted':
            assert value is not None

        return value

    # Неизвестное поле
    show_user_services = Column(Boolean)

    # Неизвестное поле
    page_views_count = Column(Boolean)

    # Неизвестное поле
    reminder_time_for_due_dates = Column(Integer)

    # Неизвестное поле
    reminder_time_for_grading = Column(Integer)

    # Неизвестное поле (Возможно квота на хранилище файлов)
    storage_quota = Column(Integer)

    # Неизвестное поле
    visible_inbox_types = Column(String(255))

    # Неизвестное поле
    last_user_note = Column(DateTime)

    # Неизвестное поле (Возможно, подписывать на email)
    subscribe_to_emails = Column(Boolean)

    # Неизвестное поле
    features_used = Column(String)

    # Настройки
    # В формате YAML
    preferences = Column(String)

    # Неизвестное поле (Возможно статус аватара - фото пользователя)
    # Возможные значения:
    # - approved
    # - none
    # - reported
    # - submitted
    avatar_state = Column(String(255))

    @validates('avatar_state')
    def validate_avatar_state(self, key, value):
        """
        Значением avatar_state может быть следующие значения:
        - approved
        - none
        - reported
        - submitted
        """
        if value:
            assert value in ['approved', 'none', 'reported', 'submitted']

        return value

    # Выбранный язык интерфейса
    # Пример: en, en-GB, ru и т.д.
    locale = Column(String(255))

    # Неизвестное поле
    browser_locale = Column(String(255))

    # Количество непрочитанных сообщении во входящем
    unread_conversations_count = Column(Integer)

    # Неизвестное поле (Возможно означает какие данные не будут менятся при импорте через SIS-импорт)
    # Вводятся поля через запятую
    # Пример: name,sortable_name и т.д.
    stuck_sis_fields = Column(String)

    # Неизвестное поле
    public = Column(Boolean)

    # Неизвестное поле (Возможно относится к двухфакторному аутентификацию)
    otp_secret_key_enc = Column(String(255))

    # Неизвестное поле (Возможно относится к двухфакторному аутентификацию)
    otp_secret_key_salt = Column(String(255))

    # Неизвестное поле (Возможно относится к двухфакторному аутентификацию)
    otp_communication_channel_id = Column(Integer)

    # Неизвестное поле
    initial_enrollment_type = Column(String(255))

    # Неизвестное поле (Относится к сервису Crocodoc)
    crocodoc_id = Column(Integer)

    # Дата и время последнего выхода из системы
    last_logged_out = Column(DateTime)

    # Контекстный LTI-идентификатор
    lti_context_id = Column(String(255))

    # Идентификатор TurnItIn
    turnitin_id = Column(Integer)

    # LTI-идентификатор пользователя
    lti_id = Column(String(255))

    # Неизвестное поле
    pronouns = Column(String)

    # Неизвестное поле (Массив целых чисел)
    root_account_ids = Column(ARRAY(Integer))

    def __repr__(self):
        return f'<User {self} (id={self.id} workflow_state={self.workflow_state})>'

    def __str__(self):
        return f'{self.name}'


class Pseudonym(Base):
    """
    Модель "Псевдонимы"
    """

    __tablename__ = 'pseudonyms'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User')
    position = Column(Integer)
    sis_user_id = Column(String(255))

    def __repr__(self):
        return '<Pseudonym {} (id={})>'.format(self, self.id)

    def __str__(self):
        return str(self.user)


class Quiz(Base):
    """
    Контрольная работа
    """
    __tablename__ = 'quizzes'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Наименование
    title = Column(String(255))

    # Описание
    description = Column(String)

    # Данные контрольной работы
    # В формате YAML
    quiz_data = Column(String)

    # Максимальный балл
    points_possible = Column(Float)

    # Идентификатор контекста
    context_id = Column(Integer)

    # Тип контекста
    # Возможные значения:
    # - Course (Курс)
    context_type = Column(String(255))

    @validates('context_type')
    def validate_context_type(self, key, value):
        """
        Значением context_type могут быть следующие значения:
        - Course (Курс)
        """
        assert value in ['Course']
        return value

    # Задание
    assignment_id = Column(ForeignKey('assignments.id'))
    assignment = relationship('Assignment')

    # Статус
    # Возможные значения:
    # - active (Активный)
    # - available (Доступный)
    # - created (Создан)
    # - deleted (Удален)
    # - edited (Редактирован)
    # - unpublished (Не опубликован)
    workflow_state = Column(default='unpublished')

    @validates('workflow_state')
    def validate_workflow_state(self, key, value):
        """
        Значением workflow_state могут быть следующие значения:
        - active (Активный)
        - available (Доступный)
        - created (Создан)
        - deleted (Удален)
        - edited (Редактирован)
        - unpublished (Не опубликован)
        """
        assert value in ['active', 'available',
                         'created', 'deleted', 'edited', 'unpublished']
        return value

    # Перемешать ответы (Рандом)
    shuffle_answers = Column(Boolean, default=False)

    # Показывать правильные ответы
    show_correct_answers = Column(Boolean, default=False)

    # Ограничение по-времени (в минутах)
    time_limit = Column(Integer)

    # Количество разрешенных попыток
    allowed_attempts = Column(Integer, default=1)

    # Какую оценку выбрать из всех попыток
    # Возможные значения:
    # - keep_average (Выбрать среднюю оценку)
    # - keep_highest (Выбрать максимальную оценку)
    # - keep_latest (Выбрать последнюю оценку)
    scoring_policy = Column(String(255))

    @validates('scoring_policy')
    def validate_scoring_policy(self, key, value):
        """
        Значением scoring_policy могут быть следующие значения:
        - keep_average (Выбрать среднюю оценку)
        - keep_highest (Выбрать максимальную оценку)
        - keep_latest (Выбрать последнюю оценку)
        """
        assert value in ['keep_average', 'keep_highest', 'keep_latest']
        return value

    # Тип контрольной работы
    # Возможные значения:
    # - assignment (Задание)
    # - graded_survey (Оцениваемый опрос)
    # - practice_quiz (???)
    # - survey (Опрос)
    quiz_type = Column(String(255))

    @validates('quiz_type')
    def validate_quiz_type(self, key, value):
        """
        Значением quiz_type могут быть следующие значения:
        - assignment (Задание)
        - graded_survey (Оцениваемый опрос)
        - practice_quiz (???)
        - survey (Опрос)
        """
        assert value in ['assignment',
                         'graded_survey', 'practice_quiz', 'survey']
        return value

    # Дата и время создания
    # server_default - Автоматически устанавливает значение created_at на текущую дату и время при создании
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время изменения
    # onupdate - Автоматически изменяет updated_at на текущую дату и время
    updated_at = Column(DateTime, onupdate=func.now())

    # Дата и время "Доступен до"
    lock_at = Column(DateTime)

    # Дата и время "Доступен с"
    unlock_at = Column(DateTime)

    # Дата и время удаления
    deleted_at = Column(DateTime)

    @validates('deleted_at')
    def validate_deleted_at(self, key, value):
        if self.workflow_state == 'deleted':
            assert value is not None
        else:
            assert value is None

        return value

    # Неизвестное поле
    could_be_locked = Column(Boolean)

    # Неизвестное поле
    cloned_item_id = Column(Integer)

    # Неизвестное поле
    access_code = Column(String(255))

    # Неизвестное поле
    migration_id = Column(String(255))

    # Количество неопубликованных вопросов
    unpublished_question_count = Column(Integer)

    # Дата и время - Срок
    due_at = Column(DateTime)

    # Количество вопросов
    question_count = Column(Integer)

    # Неизвестное поле
    last_assignment_id = Column(Integer)

    # Дата и время публикации
    published_at = Column(DateTime)

    # Дата и время редактирования
    last_edited_at = Column(DateTime)

    # Неизвестное поле
    anonymous_submissions = Column(Boolean)

    # Неизвестное поле
    assignment_group_id = Column(Integer)

    # Неизвестное поле
    hide_results = Column(String(255))

    # Неизвестное поле
    ip_filter = Column(String(255))

    # Неизвестное поле
    require_lockdown_browser = Column(Boolean)

    # Неизвестное поле
    require_lockdown_browser_for_results = Column(Boolean)

    # По одному вопросу
    one_question_at_a_time = Column(Boolean)

    # Неизвестное поле
    cant_go_back = Column(Boolean)

    # Показывать правильные ответы после даты и времени
    show_correct_answers_at = Column(DateTime)

    # Скрывать правильные ответы после даты и времени
    hide_correct_answers_at = Column(DateTime)

    # Неизвестное поле
    require_lockdown_browser_monitor = Column(Boolean)

    # Неизвестное поле
    lockdown_browser_monitor_data = Column(String)

    # Неизвестное поле
    only_visible_to_overrides = Column(Boolean)

    # Неизвестное поле
    one_time_results = Column(Boolean)

    # Неизвестное поле
    show_correct_answers_last_attempt = Column(Boolean)

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    # Неизвестное поле
    disable_timer_autosubmission = Column(Boolean)

    def __repr__(self):
        return f'<Quiz {self} (id={self.id} workflow_state={self.workflow_state})>'

    def __str__(self):
        return f'{self.name}'


class Enrollment(Base):
    """
    Модель "Участник курса"
    """
    __tablename__ = 'enrollments'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Пользователь
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User', foreign_keys='Enrollment.user_id')

    # Курс
    course_id = Column(ForeignKey('courses.id'))
    course = relationship('Course')

    # Тип
    # StudentEnrollment - студент
    # TeacherEnrollment - преподаватель
    type = Column(String(255))

    # Уникальный идентификатор
    uuid = Column(String(255))

    # Статус
    # active - Активный
    # deleted - Удаленный
    workflow_state = Column(String(255), default='active')

    # Дата и время создания
    created_at = Column(DateTime)

    # Дата и время изменения
    updated_at = Column(DateTime)

    associated_user_id = Column(ForeignKey('users.id'))
    associated_user = relationship(
        'User', foreign_keys='Enrollment.associated_user_id')

    sis_batch_id = Column(ForeignKey('sis_batches.id'))
    sis_batch = relationship('SisBatch')

    start_at = Column(DateTime)
    end_at = Column(DateTime)

    # Секция курса
    course_section_id = Column(ForeignKey('course_sections.id'))
    course_section = relationship('CourseSection')

    # Корневая учетная запись
    root_account_id = Column(ForeignKey('accounts.id'))
    root_account = relationship('Account')

    completed_at = Column(DateTime)

    self_enrolled = Column(Boolean)

    grade_publishing_status = Column(String(255))

    last_publish_attempt_at = Column(DateTime)

    stuck_sis_fields = Column(String)

    grade_publishing_message = Column(String)

    limit_privileges_to_course_section = Column(Boolean)

    last_activity_at = Column(DateTime)

    total_activity_time = Column(Integer)

    # Роль
    role_id = Column(ForeignKey('roles.id'))
    role = relationship('Role')

    graded_at = Column(DateTime)

    sis_pseudonym_id = Column(ForeignKey('pseudonyms.id'))
    sis_pseudonym = relationship('Pseudonym')

    last_attended_at = Column(DateTime)

    def __repr__(self):
        return '<Enrollment {} (id={})>'.format(self, self.id)

    def __str__(self):
        return str(self.user)


class EnrollmentState(Base):
    """
    Модель "EnrollmentState"
    """
    __tablename__ = 'enrollment_states'

    # Участник
    enrollment_id = Column(ForeignKey('enrollments.id'), primary_key=True)
    enrollment = relationship('Enrollment')

    state = Column(String(255))

    state_is_current = Column(Boolean)

    state_started_at = Column(DateTime)

    state_valid_until = Column(DateTime)

    restricted_access = Column(Boolean)

    access_is_current = Column(Boolean)

    lock_version = Column(Integer)

    updated_at = Column(DateTime)

    def __repr__(self):
        return '<EnrollmentState {} (id={})>'.format(self, self.id)

    def __str__(self):
        return str(self.enrollment)


class YU_OverrideLink(Base):
    """
    Кастомная таблица для связи между группами из Univer и идентификатором Override
    """
    __tablename__ = 'yu_override_link'

    # Идентификатор
    id = Column(Integer, primary_key=True)

    # Секция курса (Группа)
    course_section = Column(String(255))

    # Задание (Идентификатор)
    assignment = Column(Integer)

    # Override (Идентификатор)
    override = Column(Integer)

    def __repr__(self):
        return f'<YU_OverrideLink {self} ({self.id})>'

    def __str__(self):
        return f'{self.course_section}: {self.assignment}'
