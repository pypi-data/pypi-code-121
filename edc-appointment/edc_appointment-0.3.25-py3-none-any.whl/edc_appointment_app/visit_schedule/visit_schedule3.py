from dateutil.relativedelta import relativedelta
from edc_visit_schedule import Schedule, Visit, VisitSchedule

from .crfs import crfs, crfs_missed, requisitions

visit_schedule3 = VisitSchedule(
    name="visit_schedule3",
    offstudy_model="edc_appointment_app.subjectoffstudy",
    death_report_model="edc_appointment_app.deathreport",
)

schedule3 = Schedule(
    name="three_monthly_schedule",
    onschedule_model="edc_appointment_app.onschedulethree",
    offschedule_model="edc_appointment_app.offschedulethree",
    appointment_model="edc_appointment.appointment",
    consent_model="edc_appointment_app.subjectconsent",
)

visits = [
    Visit(
        code="1000",
        title="Baseline",
        timepoint=0,
        rbase=relativedelta(days=0),
        rlower=relativedelta(days=0),
        rupper=relativedelta(days=0),
        requisitions=requisitions,
        crfs=crfs,
        crfs_missed=crfs_missed,
        facility_name="7-day-clinic",
    )
]
for index, visit_code in [(3, "1030"), (6, "1060"), (9, "1090"), (12, "1120")]:
    visits.append(
        Visit(
            code=visit_code,
            title=f"Month {index}",
            timepoint=index,
            rbase=relativedelta(months=index),
            rlower=relativedelta(days=14),
            rupper=relativedelta(days=45),
            requisitions=requisitions,
            crfs=crfs,
            crfs_missed=crfs_missed,
            facility_name="7-day-clinic",
            allow_unscheduled=True,
        )
    )
for visit in visits:
    schedule3.add_visit(visit)

visit_schedule3.add_schedule(schedule3)
