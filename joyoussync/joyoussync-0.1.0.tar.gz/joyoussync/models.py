import logging
import requests
from django.db import models
from ls.joyous.models import CalendarPage
from ls.joyous.formats.ical import VCalendar
from django_q.tasks import schedule
from django_q.models import Schedule
from .utils import FakeRequest


logger = logging.getLogger('joyoussync')


class SyncJob(models.Model):
    link = models.URLField(max_length=511)
    active = models.BooleanField(default=True)
    target_calendar = models.ForeignKey(
        CalendarPage,
        on_delete=models.CASCADE,
    )

    @property
    def name(self):
        return f'joyoussync.SyncJob.{self.id}'

    def sync(self):
        logger.debug('Running sync job for "%s"',
            self.target_calendar.title)
        vcal = VCalendar(self.target_calendar)

        response = requests.get(self.link)

        if response.status_code < 400:
            vcal.load(FakeRequest(), response.text)
        else:
            logger.error('Sync job for "%s" failed due to HTTP error on %s',
                self.target_calendar.title, self.link)

    def save(self, *args, **kwargs):
        if filter_set := Schedule.objects.filter(name=self.name):
            filter_set.first().delete()
        if self.active:
            logger.info('Scheduling sync job for "%s"',
                self.target_calendar.title)
            schedule('joyoussync.models.sync', self.id,
                     name=self.name,
                     schedule_type='I', # minutes
                     minutes=1)
        super().save(*args, **kwargs)


def sync(job_id):
    SyncJob.objects.get(id=job_id).sync()
