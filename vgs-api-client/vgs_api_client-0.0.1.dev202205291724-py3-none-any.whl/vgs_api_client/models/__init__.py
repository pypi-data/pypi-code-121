# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from vgs_api_client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from vgs_api_client.model.alias import Alias
from vgs_api_client.model.alias_format import AliasFormat
from vgs_api_client.model.api_error import ApiError
from vgs_api_client.model.create_aliases_request import CreateAliasesRequest
from vgs_api_client.model.create_aliases_request_new import CreateAliasesRequestNew
from vgs_api_client.model.create_aliases_request_reference import CreateAliasesRequestReference
from vgs_api_client.model.inline_response200 import InlineResponse200
from vgs_api_client.model.inline_response2001 import InlineResponse2001
from vgs_api_client.model.inline_response201 import InlineResponse201
from vgs_api_client.model.inline_response_default import InlineResponseDefault
from vgs_api_client.model.revealed_data import RevealedData
from vgs_api_client.model.update_alias_request import UpdateAliasRequest
from vgs_api_client.model.update_alias_request_data import UpdateAliasRequestData
