import arrow
from dateutil.relativedelta import relativedelta
from edc_consent.consent import Consent
from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE, MALE

v1 = Consent(
    "adverse_event_app.subjectconsent",
    version="1",
    start=arrow.utcnow().floor("hour") - relativedelta(years=1),
    end=arrow.utcnow().ceil("hour") + relativedelta(years=1),
    age_min=18,
    age_is_adult=18,
    age_max=110,
    gender=[MALE, FEMALE],
)

site_consents.register(v1)
