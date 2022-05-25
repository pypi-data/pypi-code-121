
from pyexpat import model
from ninja import NinjaAPI
from ninja.security import django_auth
from ninja.responses import codes_4xx

from django.conf import settings
from corptools.models import Structure, CorpAsset
from . import models

import logging

logger = logging.getLogger(__name__)


api = NinjaAPI(title="IndyDash API", version="0.0.1",
               urls_namespace='indydash:api', auth=django_auth, csrf=True,
               openapi_url=settings.DEBUG and "/openapi.json" or "")


@api.get(
    "structure/list",
    tags=["Structures"]
)
def get_structure_list(request):
    if request.user.has_perm('indydash.view_dash'):
        inc_groups = [1404, 1406]
        inc_services = ['Material Efficiency Research',
                        'Blueprint Copying',
                        'Time Efficiency Research',
                        'Composite Reactions',
                        'Reprocessing',
                        'Biochemical Reactions',
                        'Hybrid Reactions',
                        'Invention',
                        'Manufacturing (Standard)',
                        'Manufacturing (Capitals)',
                        'Manufacturing (Super Capitals)',
                        ]
        corps = models.IndyDashConfiguration.objects.get(pk=1).corporations.all()
        strs = Structure.objects.filter(structureservice__name__in=inc_services,
                                        type_name__group_id__in=inc_groups,
                                        corporation__corporation__in=corps).distinct()
        output = []
        for s in strs:
            services = s.structureservice_set.filter(name__in=inc_services).values_list('name', flat=True)
            r = CorpAsset.objects.filter(location_id=s.structure_id, 
                                         location_flag__icontains="rig"
                                         ).values_list('type_name__name', flat=True).distinct()

            output.append({
                        "system":s.system_name.name,
                        "name":s.name,
                        "type":s.type_name.name,
                        "services": list(services),
                        "rigs": list(r)})

        return output
    else:
        return []
