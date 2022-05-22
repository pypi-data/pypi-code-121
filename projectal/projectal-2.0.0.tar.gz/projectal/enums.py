"""
Enums use readable names for string values expected by the Projectal
API.

```
# Example usage
from projectal.enums import ConstraintType

task = projectal.Task.create(project, {
    'name': 'Example Task',
    'constraintType': ConstraintType.ASAP,
    'taskType': TaskType.Task
})
```
"""

class Currency:
    USD = "USD"
    AUD = "AUD"
    EUR = "EUR"
    PLN = "PLN"
    MYR = "MYR"
    INR = "INR"
    IRR = "IRR"
    JPY = "JPY"
    GBP = "GBP"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    HKD = "HKD"
    NZD = "NZD"
    SEK = "SEK"
    KRW = "KRW"
    SGD = "SGD"
    NOK = "NOK"
    MXN = "MXN"
    RUB = "RUB"
    ZAR = "ZAR"
    TRY = "TRY"
    BRL = "BRL"


class TaskType:
    Project = "Project"
    Task = "Task"
    Milestone = "Milestone"


class ConstraintType:
    ASAP = "As_soon_as_possible"
    ALAP = "As_late_as_possible"
    SNET = "Start_no_earlier_than"
    SNLT = "Start_no_later_than"
    FNET = "Finish_no_earlier_than"
    FNLT = "Finish_no_later_than"
    MSO = "Must_start_on"
    MFO = "Must_finish_on"


class StaffType:
    Casual = "Casual"
    Contractor = "Contractor"
    Consultant = "Consultant"
    Freelance = "Freelance"
    Intern = "Intern"
    FullTime = "Full_Time"
    PartTime = "Part_Time"


class PayFrequency:
    # OneShot = "One_shot"
    Annually = "Annually"
    Monthly = "Monthly"
    Hourly = "Hourly"
    Daily = "Daily"
    Weekly = "Weekly"


class DateLimit:
    Min = "1970-01-01"
    Max = "9999-12-31"


class CompanyType:
    Master = "Master"
    Subsidiary = "Subsidiary"
    Contractor = "Contractor"
    Partner = "Partner"
    Affiliate = "Affiliate"
    Office = "Office"


class CalendarType:
    Leave = "Leave"
    Sunday = "Sunday"
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Working = "Working"


class SkillLevel:
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Expert = "Expert"


class GanttLinkType:
    FinishToStart = "Finish_to_start"
    StartToStart = "Start_to_start"
    FinishToFinish = "Finish_to_finish"
    StartToFinish = "Start_to_finish"
