from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Crf, FormsCollection, Schedule, Visit, VisitSchedule

crfs = FormsCollection(Crf(show_order=1, model="adverse_event_app.crfone", required=True))

visit = Visit(
    code="1000",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    title="Baseline",
    requisitions=None,
    crfs=crfs,
    requisitions_unscheduled=None,
    crfs_unscheduled=None,
    allow_unscheduled=False,
    facility_name="5-day-clinic",
)

schedule = Schedule(
    name="schedule1",
    onschedule_model="adverse_event_app.onschedule",
    offschedule_model="adverse_event_app.StudyTerminationConclusion",
    appointment_model="edc_appointment.appointment",
    consent_model="adverse_event_app.subjectconsent",
)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="adverse_event_app.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule.add_visit(visit)

visit_schedule.add_schedule(schedule)
