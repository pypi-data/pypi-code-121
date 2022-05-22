import omise
from .utils.core_utils import setting

omise.api_secret = setting("OMISE_SECRET_KEY")
omise.api_public = setting("OMISE_PUBLIC_KEY")
