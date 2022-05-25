from django.conf import settings
from django.utils.formats import date_format
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _

from django_ical.utils import build_rrule_from_text
from django_ical.views import ICalFeed

from aleksis.core import models
from aleksis.core.util.core_helpers import get_site_preferences, queryset_rules_filter


class PersonalICalFeedBase(ICalFeed):
    """Base class for personal iCal feeds."""

    @property
    def product_id(self):
        lang = self.request.LANGUAGE_CODE
        title = get_site_preferences()["general__title"]
        return f"-//AlekSIS//{title}//{lang}"

    link = settings.BASE_URL
    timezone = settings.TIME_ZONE
    person = None
    request = None

    def get_object(self, request, *args, **kwargs):
        if kwargs.get("person"):
            self.person = kwargs.pop("person")
        self.request = request
        return super().get_object(request, *args, **kwargs)

    @classproperty
    def subclasses_list(cls):
        return cls.__subclasses__()

    @classproperty
    def subclasses_dict(cls):
        return {subclass.__name__: subclass for subclass in cls.subclasses_list}

    @classproperty
    def subclass_choices(cls):
        return [
            (subclass.__name__, f"{subclass.title} – {subclass.description}")
            for subclass in cls.subclasses_list
        ]


class BirthdayFeed(PersonalICalFeedBase):
    """Birthday calendar feed."""

    title = _("Birthday Calendar")
    description = _("A Calendar of Birthdays")
    file_name = "birthdays.ics"

    def items(self):
        from aleksis.core.models import Person

        return queryset_rules_filter(
            obj=self.person.user,
            perm="core.view_personal_details_rule",
            queryset=Person.objects.filter(date_of_birth__isnull=False),
        )

    def item_title(self, item: "models.Person"):
        return _("%(name)s's birthday") % {
            "name": item.addressing_name,
        }

    def item_description(self, item: "models.Person"):
        return _("%(name)s was born on %(birthday)s") % {
            "name": item.addressing_name,
            "birthday": date_format(item.date_of_birth),
        }

    def item_start_datetime(self, item):
        return item.date_of_birth

    def item_rrule(self, item):
        return build_rrule_from_text("FREQ=YEARLY")
