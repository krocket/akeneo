#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Akeneo API Class
"""

from __future__ import print_function
import base64
import json
import logging
import os
try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

import requests
from requests import Request
from requests_toolbelt.multipart.encoder import MultipartEncoder

from version import __version__

__all__ = ['AkeneoAPI']
AKENEO_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
USER_AGENT = 'Akeneo API Python Client/{}'.format(__version__)
REQUESTS_CODES_VALID = [requests.codes.ok,
                        requests.codes.accepted,
                        requests.codes.no_content]


class NoQuotedCommasSession(requests.Session):

    def send(self, *a, **kw):
        a[0].url = unquote(a[0].url)
        print('ici')
        print(a[0].url)
        return requests.Session.send(self, *a, **kw)


class AkeneoAPIException(Exception):
    def __init__(self, message, *args):
        self.message = message
        super(AkeneoAPIException, self).__init__(message, *args)


class AkeneoAPI(object):
    """ AkeneoAPI Class

        cf. https://api.akeneo.com/api-reference.html
    """

    # api/rest/v1/
    def __init__(self, url, client_id, secret, username, password, **kwargs):
        self.__dict__.update(kwargs)

        self.url = url
        self.client_id = client_id
        self.secret = secret
        self.username = username
        self.password = password

        try:
            self.api_type
        except AttributeError:
            self.api_type = 'rest'

        try:
            self.version
        except AttributeError:
            self.version = 'v1'

        try:
            self.verbose
        except AttributeError:
            self.verbose = False

        # Setup log
        self.__setup_log()

        # cf. http://docs.python-requests.org/en/master/user/advanced/#session-objects
        self.session = requests.Session()

        self.__authenticate()

    def __setup_log(self):
        self.log = logging.getLogger('akeneo_api_client')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        steam_handler = logging.StreamHandler()
        steam_handler.setFormatter(formatter)

        if self.verbose:
            self.log.setLevel(logging.DEBUG)
            steam_handler.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)
            steam_handler.setLevel(logging.INFO)

        self.log.addHandler(steam_handler)

        return self.log

    def __enter__(self):
        """
        Entry point for with statement
        """
        return self

    def __exit__(self, type, value, traceback):
        """
        Exit point

        Closes session with akeneo
        """
        self.close_session()

    def __get_url_authenticate(self):
        url = '{}/'.format(self.url) if not self.url.endswith('/') else self.url

        return "{}api/{}/{}/{}".format(url, 'oauth', self.version, 'token')

    def __authenticate(self):
        secret = base64.standard_b64encode("{}:{}".format(self.client_id, self.secret).encode())
        headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json',
            'Authorization': 'Basic {}'.format(secret.decode())
        }
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
        }
        r = self.session.post(url=self.__get_url_authenticate(),
                              headers=headers, json=data)

        res = self.__handle_api_response(r)

        try:
            self.token = res['access_token']
            self.refresh_token = res['refresh_token']
        except KeyError:
            raise AkeneoAPIException(message="Can't read auth tokens from Akeneo API Authenticate response! "
                                     "Is Akeneo OK?!")

        self.headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.token)
        }

    def __get_url(self, endpoint, id=None):
        """ Get URL for requests """

        # Deal with trailing slash in url
        url = '{}/'.format(self.url) if not self.url.endswith('/') else self.url

        # Build the complete url
        url = '{}api/{}/{}/{}'.format(url, self.api_type, self.version, endpoint)

        # Deal with id param (cf. when we make a DELETE request)
        return '{}/{}'.format(url, id) if id else url

    def __handle_api_response(self, api_response, multiline=False):
        """ In some cases, we have to deal with errors in the response from the Akeneo API!
        """
        status_code = api_response.status_code
        response_data = None

        if status_code in REQUESTS_CODES_VALID:
            try:
                response_data = api_response.json()
            except ValueError:  # includes simplejson.decoder.JSONDecodeError
                response_data = [json.loads(l) for l in api_response.text.split("\n")]
        elif status_code == requests.codes.created:
            response_data = {'Location': api_response.headers['Location']}
        elif status_code == requests.codes.no_content:
            response_data = {}

        if multiline and response_data:
            status_lines = isinstance(response_data, list) and response_data or [response_data]
        else:
            status_lines = [{'status_code': status_code}]

        for line in status_lines:
            status_code = line.get('status_code', requests.codes.ok)
            if status_code not in REQUESTS_CODES_VALID:
                message = 'AkeneoAPIException in {} - {}: {} - {}'.format(
                    api_response.request.method, api_response.url, api_response, api_response.text)
                self.log.critical(message)
                raise AkeneoAPIException(message=message)

        # We don't have errors in our response, we can go on... and handle the response in our code
        self.log.debug('response_data for {} - {}: {}'.format(api_response.request.method,
                                                              api_response.url, response_data))
        return response_data

    def __request(self, method, endpoint, data=None, file=None, id=None):
        url = self.__get_url(endpoint, id)

        if method.lower() == 'get':
            r = self.__get_request(url, data, id)
        elif method.lower() == 'patch':
            r = self.__patch_request(url, data)
        elif method.lower() == 'post' and endpoint.lower() == 'media-files':
            r = self.__post_media_request(url, data, file)
        else:
            r = getattr(self.session, method.lower())(url, json=data, headers=self.headers)

        return self.__handle_api_response(r, multiline=method.lower() == 'patch')

    def __patch_request(self, url, data):
        headers = self.headers
        headers.update({'Content-Type': 'application/vnd.akeneo.collection+json'})

        if isinstance(data, dict):
            data = [data]

        data = "\n".join([json.dumps(item) for item in data])

        return self.session.patch(url, data=data, headers=headers)

    def __get_request(self, url, data=None, id=None):
        """ GET requests """
        if id:
            return self.session.get(url, headers=self.headers)

        if data:
            for i in data:
                if isinstance(data[i], dict) or isinstance(data[i], list):
                    data[i] = json.dumps(data[i])

        req = Request('GET', url, params=data, headers=self.headers)

        prepped = self.session.prepare_request(req)
        prepped.url = unquote(prepped.url)

        return self.session.send(prepped)

    def __post_media_request(self, url, product, file):
        """ POST media-files/ requests """
        if not file:
            message = "AkeneoAPIException in POST {}. You need to provide a 'file' parameter".format(url)
            self.log.critical(message)
            raise AkeneoAPIException(message=message)

        m = MultipartEncoder(
            fields={'product': json.dumps(product),
                    'file': (os.path.basename(file.name), file, 'application/octet-stream')}
        )

        headers = self.headers
        headers.update({'Content-Type': m.content_type})

        return self.session.post(url, data=m, headers=headers)

    def get(self, endpoint, data=None, id=None):
        """ GET requests """
        return self.__request('GET', endpoint, data=data, id=id)

    def filter(self, endpoint, **kwargs):
        """ Filter requests: Basically GET requests with filters/pagination capabilities.

            cf. Filters Akeneo API Doc:
            https://api.akeneo.com/documentation/filter.html
        """
        data = {}

        search_by = kwargs.get('search_by', False)
        search_operator = kwargs.get('search_operator', False)
        search_value = kwargs.get('search_value', False)

        if search_by and search_operator and search_value:
            try:
                search_date = search_value.strftime(AKENEO_DATETIME_FORMAT)
            except AttributeError:
                raise AkeneoAPIException("search_value param *MUST* be a datetime object!")

            # Example from the docs: {'search': {'created': [{'operator': '=', 'value': '2016-07-04 10:00:00'}]}}11
            data.update({'search': {search_by: [{'operator': search_operator, 'value': search_date}]}})

        # Pagination
        data.update({'page': kwargs.get('page', 1)})

        return self.__request('GET', endpoint, data=data)

    def post(self, endpoint, data, file=None):
        """ POST requests """
        return self.__request('POST', endpoint, data=data, file=file)

    def patch(self, endpoint, data):
        """ PATCH requests """
        return self.__request('PATCH', endpoint, data=data)

    def delete(self, endpoint, id):
        """ DELETE requests """
        return self.__request('DELETE', endpoint, id=id)


    def options(self, endpoint):
        """ OPTIONS requests """
        return self.__request('OPTIONS', endpoint)

    def close_session(self):
        """ Close requests.Session object """
        self.token = False
        self.refresh_token = False
        self.session.close()
