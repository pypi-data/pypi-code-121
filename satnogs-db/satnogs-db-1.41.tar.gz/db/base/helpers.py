"""Helper functions for SatNOGS DB"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token

UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWX'
LOWER = 'abcdefghijklmnopqrstuvwx'


def gridsquare(lat, lng):
    """Calculates a maidenhead grid square from a lat/long

    Used when we get a SiDS submission, we want to store and display the
    location of the submitter as a grid square.

    :returns: a string of the grid square, ie: EM69uf
    """
    try:
        if not -180 <= lng < 180:
            return 'Unknown'
        if not -90 <= lat < 90:
            return 'Unknown'
    except TypeError:
        return 'Unknown'

    adj_lat = lat + 90.0
    adj_lon = lng + 180.0

    grid_lat_sq = UPPER[int(adj_lat / 10)]
    grid_lon_sq = UPPER[int(adj_lon / 20)]

    grid_lat_field = str(int(adj_lat % 10))
    grid_lon_field = str(int((adj_lon / 2) % 10))

    adj_lat_remainder = (adj_lat - int(adj_lat)) * 60
    adj_lon_remainder = ((adj_lon) - int(adj_lon / 2) * 2) * 60

    grid_lat_subsq = LOWER[int(adj_lat_remainder / 2.5)]
    grid_lon_subsq = LOWER[int(adj_lon_remainder / 5)]

    qth = '{}'.format(
        grid_lon_sq + grid_lat_sq + grid_lon_field + grid_lat_field + grid_lon_subsq
        + grid_lat_subsq
    )

    return qth


def get_api_token(user):
    """If necessary, create, then return an API Token for a user

    :param user: a SatNOGS DB User object
    :returns: user API token
    """
    try:
        token = Token.objects.get(user=user)
    except ObjectDoesNotExist:
        token = Token.objects.create(user=user)
    return token
