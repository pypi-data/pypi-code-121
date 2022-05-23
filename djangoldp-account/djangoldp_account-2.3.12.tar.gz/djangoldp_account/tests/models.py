from django.conf import settings
from django.db import models
from djangoldp.models import Model
from djangoldp_account.models import LDPUser


# a resource in which only the owner has permissions
class OwnedResource(Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(LDPUser, blank=True, null=True, related_name="owned_resources",
                             on_delete=models.CASCADE)

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = []
        owner_perms = ['view', 'delete', 'add', 'change', 'control']
        owner_field = 'user'
        serializer_fields = ['@id', 'description', 'user']
        depth = 1
