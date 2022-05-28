#!/usr/bin/python3

# Copyright 2015-2018 by Chris Forrette
# Copyright 2022 by Louis-Philippe Véronneau
#
# This file was originally part of python-bandsintown.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Bandintown API provider
"""

try:
    from urllib.parse import quote, urljoin
except ImportError:
    from urllib import quote
    from urlparse import urljoin

import sys
import requests

from packaging import version

if version.parse(requests.__version__) < version.parse("2.27"):
    try:
        import simplejson
    except ImportError:
        sys.exit("Your version of requests is older than 2.27. You either need"
                  " to update it to a version >=2.27 or to install simplejson.")


class BandsintownError(Exception):
    """Base class for other exceptions"""
    def __init__(self, message, response=None):
        super().__init__()
        self.message = message
        self.response = response


    def __str__(self):
        return self.message


class BandsintownInvalidAppIdError(BandsintownError):
    """Raised whenever a request is made with an invalid app id"""


class BandsintownInvalidDateFormatError(BandsintownError):
    """
    Raised by the artists_events method when a date parameter is passed in an
    invalid format
    """


class Client():
    """Main class for the Bandsintown provider"""
    api_base_url = 'https://rest.bandsintown.com'


    def __init__(self, app_id):
        """
        Args:
            app_id: Required app id, can be any string
        """
        self.app_id = app_id
        self.default_params = {'app_id': self.app_id}


    def request(self, path, params = None):
        """
        Executes a request to the Bandsintown API and returns the response
        object from `requests`

        Args:
            path: The API path to append to the base API URL for the request
            params: Optional dict to tack on query string parameters to request

        Returns:
            Response object from `requests`
        """
        url = urljoin(self.api_base_url, path)
        request_params = self.default_params.copy()
        request_params.update(params)
        response = requests.get(
            url,
            headers={'Accept': 'application/json'},
            params=request_params
        )
        # TODO: Some responses aren't always valid JSON? This probably happens
        # because we're not passing the right info? To debug.
        if version.parse(requests.__version__) < version.parse("2.27"):
            try:
                data = response.json()
            except simplejson.errors.JSONDecodeError:  # requests <2.27
                data = []
        else:
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError: # pylint: disable=E0701  # requests >=2.27
                data = []

        invalid_appid_message = ('User is not authorized to access this resource '
                                 'with an explicit deny')
        if 'Message' in data and data['Message'] == invalid_appid_message:
            message = 'Invalid Bandsintown App ID (API key)'
            raise BandsintownInvalidAppIdError(message, response)

        missing_appid_message = 'Missing Authentication Token'
        if 'message' in data and data['message'] == missing_appid_message:
            message = 'Missing Bandsintown App ID (API key)'
            raise BandsintownInvalidAppIdError(message, response)
        return data


    def artists_events(self, artistname, date=None):
        """
        Searches for events for a single artist, with an optional date range,
        using this endpoint:

            https://app.swaggerhub.com/apis/Bandsintown/PublicAPI/3.0.0#/upcoming_artist_events/artistEvents

        Args:
            artistname: Artist name to search for
            date: Optional date string filter, can be a specific date in the
            format: "yyyy-mm-dd", a range "yyyy-mm-dd,yyyy-mm-dd", or can be a
            few keyword values like "upcoming" or "all"


        Returns:
            A list of event data, which could be empty, None if artist not
            found, raises `BandsintownInvalidDateFormatError` for bad `date`
            param, or raises `BandsintownError` for other unknown error

        Usage:
            client = Client(app_id=1234)
            client.artists_events('Bad Religion')
            client.artists_events('Bad Religion', date='2018-02-01,2018-02-28')
        """
        params = {}

        if date:
            params['date'] = date

        data = self.request(f'artists/{quote(artistname)}/events', params)

        if 'errorMessage' in data:
            if data['errorMessage'] == '[NotFound] The artist was not found':
                return None
            raise BandsintownError('Unknown error with request', data)

        return data
