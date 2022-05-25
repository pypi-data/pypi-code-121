
from django.utils.translation import ugettext_lazy as _

UNIT_TYPE_PCS = 'pcs'

UNIT_TYPES = (
    (UNIT_TYPE_PCS, _('pcs.')),
    ('l', _('l')),
    ('ml', _('ml')),
    ('g', _('g')),
    ('kg', _('kg')),
    ('pgs', _('pgs')),
)
