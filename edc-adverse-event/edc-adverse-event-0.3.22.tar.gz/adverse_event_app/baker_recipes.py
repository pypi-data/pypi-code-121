from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_constants.constants import MALE, NO, NOT_APPLICABLE, YES
from edc_reportable import GRADE4
from edc_utils import get_utcnow
from faker import Faker
from model_bakery.recipe import Recipe, seq

from .models import (
    AeFollowup,
    AeInitial,
    AeSusar,
    AeTmg,
    DeathReport,
    DeathReportTmg,
    DeathReportTmgSecond,
    SubjectConsent,
)

fake = Faker()

subjectconsent = Recipe(
    SubjectConsent,
    consent_datetime=get_utcnow,
    dob=get_utcnow() - relativedelta(years=25),
    first_name=fake.first_name,
    last_name=fake.last_name,
    initials="AA",
    gender=MALE,
    identity=seq("12315678"),
    confirm_identity=seq("12315678"),
    identity_type="passport",
    is_dob_estimated="-",
    site=Site.objects.get_current(),
)

aeinitial = Recipe(
    AeInitial,
    action_identifier=None,
    tracking_identifier=None,
    ae_description="A description of this event",
    ae_grade=GRADE4,
    ae_study_relation_possibility=YES,
    ae_start_date=get_utcnow().date(),
    ae_awareness_date=get_utcnow().date(),
    sae=NO,
    susar=NO,
    susar_reported=NOT_APPLICABLE,
    ae_cause=NO,
    ae_cause_other=None,
)

aetmg = Recipe(AeTmg, action_identifier=None, tracking_identifier=None)

aesusar = Recipe(AeSusar, action_identifier=None, tracking_identifier=None)

aefollowup = Recipe(
    AeFollowup, relevant_history=NO, action_identifier=None, tracking_identifier=None
)


deathreport = Recipe(DeathReport, action_identifier=None, tracking_identifier=None)


deathreporttmg = Recipe(DeathReportTmg, action_identifier=None, tracking_identifier=None)


deathreporttmgsecond = Recipe(
    DeathReportTmgSecond, action_identifier=None, tracking_identifier=None
)
