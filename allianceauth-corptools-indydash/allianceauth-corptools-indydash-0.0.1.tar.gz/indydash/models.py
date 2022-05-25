from django.core.exceptions import ValidationError
from django.db import models

from allianceauth.eveonline.models import EveCorporationInfo

class IndyDashConfiguration(models.Model):

    corporations = models.ManyToManyField(EveCorporationInfo, blank=True)

    def __str__(self):
        return "Configuration"

    def save(self, *args, **kwargs):
        if not self.pk and IndyDashConfiguration.objects.exists():
            # Force a single object
            raise ValidationError(
                'Only one Settings Model can there be at a time! No Sith Lords there are here!')
        self.pk = self.id = 1  # If this happens to be deleted and recreated, force it to be 1
        return super().save(*args, **kwargs)

    class Meta:
        default_permissions = ()
        permissions = (
            ('view_dash', 'Can View Indy Dashboard'),
        )

