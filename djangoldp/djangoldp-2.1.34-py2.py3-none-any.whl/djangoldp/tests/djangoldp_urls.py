from django.conf.urls import re_path

from djangoldp.permissions import LDPPermissions
from djangoldp.tests.models import Skill, JobOffer, Message, Conversation, Dummy, PermissionlessDummy, Task, DateModel, LDPDummy
from djangoldp.views import LDPViewSet

urlpatterns = [
    re_path(r'^messages/', LDPViewSet.urls(model=Message, permission_classes=[LDPPermissions], fields=["@id", "text", "conversation"], nested_fields=['conversation'])),
    re_path(r'^conversations/', LDPViewSet.urls(model=Conversation, nested_fields=["message_set", "observers"], permission_classes=[LDPPermissions])),
    re_path(r'^tasks/', LDPViewSet.urls(model=Task, permission_classes=[LDPPermissions])),
    re_path(r'^dates/', LDPViewSet.urls(model=DateModel, permission_classes=[LDPPermissions])),
    re_path(r'^dummys/', LDPViewSet.urls(model=Dummy, permission_classes=[LDPPermissions], lookup_field='slug',)),
    re_path(r'^ldpdummys/', LDPViewSet.urls(model=LDPDummy, permission_classes=[LDPPermissions], nested_fields=['anons'])),
    re_path(r'^permissionless-dummys/', LDPViewSet.urls(model=PermissionlessDummy, permission_classes=[LDPPermissions], lookup_field='slug',)),
]

