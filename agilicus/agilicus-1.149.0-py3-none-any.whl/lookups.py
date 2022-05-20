from . import context
from .input_helpers import get_org_from_input_or_ctx


def lookup(ctx, org_id, guid, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)

    res = apiclient.lookups_api.lookup_org_guid(org_id, guid)
    return res
