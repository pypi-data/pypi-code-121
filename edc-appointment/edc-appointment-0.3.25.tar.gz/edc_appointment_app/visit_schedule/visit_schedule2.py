from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Schedule, Visit, VisitSchedule

from .crfs import crfs, crfs_missed, requisitions

visit_schedule2 = VisitSchedule(
    name="visit_schedule2",
    offstudy_model="edc_appointment_app.subjectoffstudy2",
    death_report_model="edc_appointment_app.deathreport",
    locator_model="edc_appointment_app.subjectlocator",
)

schedule2 = Schedule(
    name="schedule2",
    onschedule_model="edc_appointment_app.onscheduletwo",
    offschedule_model="edc_appointment_app.offscheduletwo",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_appointment_app.subjectconsent",
)


visits = []
for index in range(4, 8):
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
            facility_name="7-day-clinic",
        )
    )
for visit in visits:
    schedule2.add_visit(visit)

visit_schedule2.add_schedule(schedule2)
