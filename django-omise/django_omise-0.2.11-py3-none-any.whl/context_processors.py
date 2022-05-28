from django.conf import settings


def omise_keys(request):
    data = {}
    data["omise_public_key"] = settings.OMISE_PUBLIC_KEY
    return data
