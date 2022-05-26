from pydantic import BaseModel
import typing


class Error(BaseModel):
    """Error object"""

    code: str
    description: str


class UsersRoles(BaseModel):
    """full user roles"""

    Id: typing.Optional[int] = None
    RoleId: typing.Optional[int] = None
    UserId: typing.Optional[int] = None
    RoleName: typing.Optional[str] = None
    EntityType: typing.Optional[str] = None
    EntityName: typing.Optional[str] = None
    ChildId: typing.Optional[str] = None


class UsersFull(BaseModel):
    """full user info"""

    Id: typing.Optional[int] = None
    Login: typing.Optional[str] = None
    Password: typing.Optional[str] = None
    Email: typing.Optional[str] = None
    INN: typing.Optional[str] = None
    SNILS: typing.Optional[str] = None
    BornDate: typing.Optional[str] = None
    Photo: typing.Optional[str] = None
    FirstName: typing.Optional[str] = None
    LastName: typing.Optional[str] = None
    MiddleName: typing.Optional[str] = None
    Token: typing.Optional[str] = None
    Roles: typing.List[UsersRoles] = None


class LoginTokenGetModel(BaseModel):
    status: str
    error: Error
    result: UsersFull = None


class UsersMin(BaseModel):
    """full user info"""

    Id: typing.Optional[int] = None
    Firstname: typing.Optional[str] = None
    Surname: typing.Optional[str] = None
    Patronumic: typing.Optional[str] = None
    Email: typing.Optional[str] = None


class LoginUsersGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[UsersMin] = None


class SystemPeriod(BaseModel):
    """информация о текущем периоде обучения"""
    Id: typing.Optional[int] = None
    StartYear: typing.Optional[str] = None
    EndYear: typing.Optional[str] = None


class SystemPeriodGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[SystemPeriod] = None


class NewsGetInfo(BaseModel):
    """информация о новостях на сайте"""
    Id: typing.Optional[int] = None
    Title: typing.Optional[str] = None
    ShortContent: typing.Optional[str] = None
    StartDate: typing.Optional[str] = None
    EndDate: typing.Optional[str] = None
    CreatedByThisUser: typing.Optional[int] = None
    Visible: typing.Optional[bool] = None
    UserId: typing.Optional[int] = None
    Readed: typing.Optional[int] = None
    IsParent: typing.Optional[int] = None
    HasAccess: typing.Optional[bool] = None


class NewsGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[NewsGetInfo] = None


class BillGetInfo(BaseModel):
    """информация о счетах"""
    Id: typing.Optional[int] = None
    BillType: typing.Optional[str] = None
    UserId: typing.Optional[str] = None
    Num: typing.Optional[str] = None
    Balance: typing.Optional[int] = None
    Active: typing.Optional[bool] = None


class BillGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[BillGetInfo] = None


class MarkDairyInfo(BaseModel):
    """информация о оценке с урока"""
    Id: typing.Optional[int] = None
    Mark: typing.Optional[int] = None
    MarkKindTitle: typing.Optional[str] = None
    MarkCreateDate: typing.Optional[str] = None
    ConfirmedParentId: typing.Optional[str] = None
    LessonId: typing.Optional[int] = None


class TeacherFilesInfo(BaseModel):
    """информация о загруженном файле к уроку от учителя"""
    Id: typing.Optional[int] = None
    LessonId: typing.Optional[int] = None
    TeacherFileExtension: typing.Optional[str] = None
    TeacherFileName: typing.Optional[str] = None


class LearnerFilesInfo(BaseModel):
    """информация о загруженном файле учителю к уроку"""
    Id: typing.Optional[int] = None
    LearnerId: typing.Optional[int] = None
    LearnerFileExtension: typing.Optional[str] = None
    LearnerFileName: typing.Optional[str] = None


class DairyGetInfo(BaseModel):
    """информация о уроке"""
    LessonId: typing.Optional[int] = None
    LessonKindId: typing.Optional[int] = None
    ScheduleId: typing.Optional[int] = None
    ScheduleActive: typing.Optional[bool] = None
    Student: typing.Optional[int] = None
    Year: typing.Optional[int] = None
    YearWeekNumber: typing.Optional[int] = None
    WeekDayTypeKeyword: typing.Optional[str] = None
    Date: typing.Optional[str] = None
    DepartmentId: typing.Optional[int] = None
    Discipline: typing.Optional[str] = None
    LessonOrder: typing.Optional[int] = None
    RoomTitle: typing.Optional[str] = None
    StartTime: typing.Optional[str] = None
    EndTime: typing.Optional[str] = None
    Homework: typing.Optional[str] = None
    Late: typing.Optional[str] = None
    Marks: typing.List[MarkDairyInfo] = None  # список оценок
    AbsenceId: typing.Optional[str] = None
    Presence: typing.Optional[str] = None
    TeacherComment: typing.Optional[str] = None
    TeacherId: typing.Optional[int] = None
    TeacherFirstName: typing.Optional[str] = None
    TeacherLastName: typing.Optional[str] = None
    TeacherMiddleName: typing.Optional[str] = None
    PastLessonId: typing.Optional[int] = None
    PastHomework: typing.Optional[str] = None
    IsLoadHomework: typing.Optional[int] = None
    TeacherFiles: typing.List[TeacherFilesInfo] = None  # список прикрепленных файлов учителя
    LearnerFiles: typing.List[LearnerFilesInfo] = None  # список прикрепленных файлов ученика
    TestName: typing.Optional[str] = None
    TestMessage: typing.Optional[str] = None
    TestUrl: typing.Optional[str] = None
    Webinar: typing.Optional[str] = None
    WebinarDate: typing.Optional[str] = None
    Materials: typing.Optional[str] = None
    FormType: typing.Optional[int] = None


class DairyGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[DairyGetInfo] = None


class CardGetInfo(BaseModel):
    Id: typing.Optional[int] = None
    CardNumber: typing.Optional[int] = None
    UserId: typing.Optional[int] = None


class CardGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[CardGetInfo] = None


class SkudGetInfo(BaseModel):
    """не нашел информации"""
    pass


class SkudGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[SkudGetInfo] = None


class BillReplenishmentGetInfo(BaseModel):
    """не нашел информации"""


class BillReplenishmentGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[BillReplenishmentGetInfo] = None


class FoodTransactionGetInfo(BaseModel):
    """не нашел информации"""
    pass


class FoodTransactionGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[FoodTransactionGetInfo] = None


class PresenceGetInfo(BaseModel):
    """список информация об отсутствии на уроке"""
    LessonId: typing.Optional[int] = None
    Value: typing.Optional[str] = None
    IsIllness: typing.Optional[bool] = None
    Date: typing.Optional[str] = None
    ScheduleId: typing.Optional[int] = None
    DisciplineId: typing.Optional[int] = None
    UserId: typing.Optional[int] = None


class PresenceGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[PresenceGetInfo] = None


class MarkExamGetInfo(BaseModel):
    """не нашел информации"""
    pass


class MarkExamGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[MarkExamGetInfo] = None


class MarkResultGetInfo(BaseModel):
    """не нашел информации"""
    Id: typing.Optional[int] = None
    UserId: typing.Optional[int] = None
    DepartmentId: typing.Optional[int] = None
    MarkTypeValueId: typing.Optional[int] = None
    MarkResultTypeKeyword: typing.Optional[str] = None
    CreatedDate: typing.Optional[str] = None
    CreateUserId: typing.Optional[int] = None
    DepartmentToInstituteBellScheduleTypeId: typing.Optional[int] = None
    InstituteToDisciplineId: typing.Optional[int] = None
    Active: typing.Optional[bool] = None
    IsVerificated: typing.Optional[bool] = None
    SystemPeriodId: typing.Optional[int] = None
    DepartmentGroupId: typing.Optional[int] = None
    PeriodId: typing.Optional[int] = None


class MarkResultGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[MarkResultGetInfo] = None


class MarkValueGetInfo(BaseModel):
    """оценка из общего списка"""
    Id: typing.Optional[int] = None
    TeacherId: typing.Optional[int] = None
    MarkTypeValueId: typing.Optional[int] = None
    CreatedDate: typing.Optional[str] = None
    LessonId: typing.Optional[int] = None
    UserId: typing.Optional[int] = None
    Active: typing.Optional[bool] = None
    Comment: typing.Optional[str] = ""


class MarkValueGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[MarkValueGetInfo] = None


class DepartmentGroupGetInfo(BaseModel):
    """информация о подгруппах"""
    Id: typing.Optional[int] = None
    Title: typing.Optional[str] = None
    DepartmentId: typing.Optional[int] = None
    UserId: typing.Optional[int] = None
    StartDate: typing.Optional[str] = None
    EndDate: typing.Optional[str] = None
    InstituteToDisciplineId: typing.Optional[int] = None


class DepartmentGroupGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[DepartmentGroupGetInfo] = None


class DepartmentGetInfo(BaseModel):
    """информация об обучении"""
    KeyId: typing.Optional[int] = None
    Id: typing.Optional[int] = None
    Number: typing.Optional[int] = None
    Letter: typing.Optional[str] = None
    UserId: typing.Optional[int] = None
    EducationPeriodTypeKeyword: typing.Optional[str] = None
    SystemPeriodId: typing.Optional[int] = None
    InstituteId: typing.Optional[int] = None
    Title: typing.Optional[str] = None
    Current: typing.Optional[bool] = None


class DepartmentGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[DepartmentGetInfo] = None


class DictionaryTypeGetInfo(BaseModel):
    """информация об обучении"""
    Keyword: typing.Optional[str] = None
    Title: typing.Optional[str] = None


class DictionaryTypeGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[DictionaryTypeGetInfo] = None


class MarkKindGetInfo(BaseModel):
    """информация за какой тип работы поставили оценку (эссе, зачет и т.п.)"""
    Id: typing.Optional[int] = None
    Title: typing.Optional[str] = None


class MarkKindGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[MarkKindGetInfo] = None


class PayAgentGetInfo(BaseModel):
    """нет информации"""
    Keyword: typing.Optional[str] = None
    Title: typing.Optional[str] = None


class PayAgentGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[PayAgentGetInfo] = None


class FoodTransactionTypeGetInfo(BaseModel):
    """нет информации"""
    Keyword: typing.Optional[str] = None
    Title: typing.Optional[str] = None
    TransferPayment: typing.Optional[bool] = None


class FoodTransactionTypeGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[FoodTransactionTypeGetInfo] = None


class MarkTypeValueGetInfo(BaseModel):
    """нет информации"""
    Id: typing.Optional[int] = None
    MarkTypeKeyword: typing.Optional[str] = None
    Value: typing.Optional[str] = None
    Order: typing.Optional[int] = None


class MarkTypeValueGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[MarkTypeValueGetInfo] = None


class LessonGetInfo(BaseModel):
    """информация об уроке"""
    Id: typing.Optional[int] = None
    PeriodId: typing.Optional[int] = None
    DateTime: typing.Optional[str] = None
    BellId: typing.Optional[int] = None
    DepartmentId: typing.Optional[int] = None
    RoomId: typing.Optional[int] = None
    DepartmentGroupId: typing.Optional[int] = None
    DisciplineId: typing.Optional[int] = None
    TeacherId: typing.Optional[int] = None
    Theme: typing.Optional[str] = None
    Homework: typing.Optional[str] = None
    IsLoadHomework: typing.Optional[bool] = None
    TestStart: typing.Optional[str] = None
    TestEnd: typing.Optional[str] = None
    TestMessage: typing.Optional[str] = None
    TestUrl: typing.Optional[str] = None
    Active: typing.Optional[bool] = None
    Materials: typing.Optional[str] = None
    FormType: typing.Optional[int] = None


class LessonGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[LessonGetInfo] = None


class PeriodGetInfo(BaseModel):
    """информация об обучающимся году"""
    Id: typing.Optional[int] = None
    Title: typing.Optional[str] = None
    StartDate: typing.Optional[str] = None
    EndDate: typing.Optional[str] = None
    StartYear: typing.Optional[int] = None
    EndYear: typing.Optional[int] = None
    EducationPeriodTypeKeyword: typing.Optional[str] = None
    InstituteId: typing.Optional[int] = None
    SystemPeriodId: typing.Optional[int] = None


class PeriodGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[PeriodGetInfo] = None


class ContingentGetInfo(BaseModel):
    """информация об одноклассниках"""
    firstname: typing.Optional[str] = None
    surname: typing.Optional[str] = None
    middlename: typing.Optional[str] = None
    isstudent: typing.Optional[int] = None


class ContingentGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[ContingentGetInfo] = None


class TeacherGetInfo(BaseModel):
    """информация об учителях"""
    Id: typing.Optional[int] = None
    Firstname: typing.Optional[str] = None
    Surname: typing.Optional[str] = None
    Patronumic: typing.Optional[str] = None


class TeacherGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[TeacherGetInfo] = None


class ScheduleGetInfo(BaseModel):
    """нет информации"""
    Id: typing.Optional[int] = None
    BellId: typing.Optional[int] = None
    DepartmentId: typing.Optional[int] = None
    RoomId: typing.Optional[int] = None
    DepartmentGroupId: typing.Optional[int] = None
    PeriodId: typing.Optional[int] = None
    DayOrder: typing.Optional[int] = None
    TeacherId: typing.Optional[int] = None
    Active: typing.Optional[bool] = None


class ScheduleGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[ScheduleGetInfo] = None


class CalendarGetInfo(BaseModel):
    """информация об выходных днях"""
    Id: typing.Optional[int] = None
    CalendarDate: typing.Optional[str] = None
    DateTypeKeyword: typing.Optional[str] = None
    InstituteId: typing.Optional[int] = None
    DepartmentId: typing.Optional[int] = None


class CalendarGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[CalendarGetInfo] = None


class InstituteToDisciplineGetInfo(BaseModel):
    """нет информации"""
    Id: typing.Optional[int] = None
    InstituteId: typing.Optional[int] = None
    DisciplineId: typing.Optional[int] = None
    IsElective: typing.Optional[bool] = None
    IsSpecial: typing.Optional[bool] = None
    Active: typing.Optional[bool] = None


class InstituteToDisciplineGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[InstituteToDisciplineGetInfo] = None


class DisciplineGetInfo(BaseModel):
    """названия предметов"""
    Id: typing.Optional[int] = None
    Title: typing.Optional[str] = None
    ShortTitle: typing.Optional[str] = None


class DisciplineGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[DisciplineGetInfo] = None


class DisciplineToPeriodGetInfo(BaseModel):
    """названия предметов"""
    KeyId: typing.Optional[int] = None
    PeriodId: typing.Optional[int] = None
    InstituteToDisciplineId: typing.Optional[int] = None
    DepartmentId: typing.Optional[int] = None


class DisciplineToPeriodGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[DisciplineToPeriodGetInfo] = None


class AbsencesByPeriodGetInfo(BaseModel):
    """информация об отсутствии на уроках"""
    DisciplineId: typing.Optional[int] = None
    DisciplineName: typing.Optional[str] = None
    LessonStartTime: typing.Optional[str] = None
    LessonEndTime: typing.Optional[str] = None
    LessonNumber: typing.Optional[int] = None
    Theme: typing.Optional[str] = None
    Title: typing.Optional[str] = None


class AbsencesByPeriodGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[AbsencesByPeriodGetInfo] = None


class AvgMarksByPeriodGetInfo(BaseModel):
    """информация об среднем балле за N дней"""
    StartDate: typing.Optional[str] = None
    EndDate: typing.Optional[str] = None
    AvgMark: typing.Optional[float] = None


class AvgMarksByPeriodGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[AvgMarksByPeriodGetInfo] = None


class AbsencesByDisciplinGetInfo(BaseModel):
    """информация об среднем балле за N дней"""
    DisciplineId: typing.Optional[int] = None
    DisciplineName: typing.Optional[str] = None
    AbsencesCount: typing.Optional[int] = None


class AbsencesByDisciplinGetModel(BaseModel):
    status: str
    error: Error
    result: typing.List[AbsencesByDisciplinGetInfo] = None


class TwoFactorCheckGetModel(BaseModel):
    status: str
    error: Error
    result: typing.Optional[bool] = None


Error.update_forward_refs()
