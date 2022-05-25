from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Schedule, Visit, VisitSchedule

from .crfs import crfs, crfs_missed, crfs_unscheduled, requisitions

visit_schedule1 = VisitSchedule(
    name="visit_schedule1",
    offstudy_model="edc_appointment_app.subjectoffstudy",
    death_report_model="edc_appointment_app.deathreport",
    locator_model="edc_appointment_app.subjectlocator",
)

schedule1 = Schedule(
    name="schedule1",
    onschedule_model="edc_appointment_app.onscheduleone",
    offschedule_model="edc_appointment_app.offscheduleone",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_appointment_app.subjectconsent",
)


visits = []
for index in range(0, 4):
    visits.append(
        Visit(
            code=f"{1 if index == 0 else index + 1}000",
            title=f"Day {1 if index == 0 else index + 1}",
            timepoint=index,
            rbase=relativedelta(days=7 * index),
            rlower=relativedelta(days=0),
            rupper=relativedelta(days=6),
            requisitions=requisitions,
            crfs=crfs,
            crfs_missed=crfs_missed,
            requisitions_unscheduled=requisitions,
            crfs_unscheduled=crfs_unscheduled,
            allow_unscheduled=True,
            facility_name="5-day-clinic",
        )
    )
for visit in visits:
    schedule1.add_visit(visit)
visit_schedule1.add_schedule(schedule1)
