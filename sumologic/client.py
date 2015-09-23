#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import configparser
import json.decoder
import time

import requests

import sumologic.exceptions
import sumologic.collector

class Client(object):

    api_base = 'https://api.us2.sumologic.com/api'
    api_version = 'v1'
    auth = ()

    def __init__(self, access_id=None, access_key=None):
        """
        :param access_id: The Access ID to connect with
        :param access_key: The Access Key to connect with
        """
        self.load_authentication(access_id, access_key)

        self.session = requests.Session()

        self.session.auth = self.auth
        self.session.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def load_authentication(self, access_id=None, access_key=None):
        """
        Load the Access ID and Access Key to be used for authentication.
        The arguments will be checked first, followed by environment
        variables and finally the file at "~/.sumologic."

        :param access_id: The Access ID to connect with.
        :type access_id: basestring
        :param access_key: The Access Key to connect with.
        :type access_key: basestring
        :raises sumologic.exceptions.AuthenticationError: When it fails
            to load authentication information
        :rtype: None
        """
        if access_id is None:
            access_id = os.environ.get('SUMOLOGIC_ACCESS_ID', None)

        if access_key is None:
            access_key = os.environ.get('SUMOLOGIC_ACCESS_KEY', None)

        if access_id is None or access_key is None:
            config = configparser.ConfigParser()
            config.read(os.path.expanduser('~/.sumologic'))

            try:
                credentials = config['credentials']
            except KeyError:
                raise sumologic.exceptions.AuthenticationError()

            if access_id is None:
                try:
                    access_id = credentials['access_id']
                except KeyError:
                    raise sumologic.exceptions.AuthenticationError()

            if access_key is None:
                try:
                    access_key = credentials['access_key']
                except KeyError:
                    raise sumologic.exceptions.AuthenticationError()

        self.auth = (access_id, access_key)

    def request(self, path, method='GET', params=None, headers=None,
                data=None, success=lambda r: r.status_code == 200,
                retry=True):
        """
        Perform an HTTP request and return its response.

        :param path: The path to request.
        :param method: The HTTP method to use.
        :param params: URL parameters to include with GET and DELETE
            requests.
        :param headers: HTTP headers to include with requests.
        :param data: Body data to include with POST and PUT requests.
        :param success: A callable which accepts a response and
            determines whether or not it was successful.
        :param retry: Whether or not to retry unsuccessful requests.
        :raises sumologic.exceptions.InvalidHTTPMethodError: When an
            invalid HTTP method is provided.
        :raises sumologic.exceptions.HTTPError: When the request isn't
            successful.
        :raises sumologic.exceptions.InvalidHTTPResponseError: When a
            response cannot be deserialized as valid JSON.
        :return: Response from HTTP request, if successful.
        :rtype: requests.models.Response
        """
        uri = '{base}/{version}/{path}'.format(base=self.api_base,
                                               version=self.api_version,
                                               path=path)
        args = {'url': uri, 'headers': headers}

        if method in ['GET', 'DELETE']:
            args['params'] = params
        elif method in ['POST', 'PUT']:
            args['data'] = data

        if method == 'GET':
            r = self.session.get(**args)
        elif method == 'POST':
            r = self.session.post(**args)
        elif method == 'PUT':
            r = self.session.put(**args)
        elif method == 'DELETE':
            r = self.session.delete(**args)
        else:
            raise sumologic.exceptions.InvalidHTTPMethodError()

        while not success(r):
            if not retry:
                break
            time.sleep(5)

        if not success(r):
            raise sumologic.exceptions.HTTPError()

        try:
            r.json()
        except json.decoder.JSONDecodeError:
            raise sumologic.exceptions.InvalidHTTPResponseError()

        return r

    def get(self, path, params=None, headers=None,
            success=lambda r: r.status_code == 200, retry=True):
        return self.request(path, method='GET', params=params, headers=headers,
                            success=success, retry=retry)

    def post(self, path, data=None, headers=None,
             success=lambda r: r.status_code == 200, retry=True):
        return self.request(path, method='POST', data=data, headers=headers,
                            success=success, retry=retry)

    def put(self, path, data=None, headers=None,
            success=lambda r: r.status_code == 200, retry=True):
        return self.request(path, method='PUT', data=data, headers=headers,
                            success=success, retry=retry)

    def delete(self, path, params=None, headers=None,
               success=lambda r: r.status_code == 200, retry=True):
        return self.request(path, method='DELETE', params=params, headers=headers,
                            success=success, retry=retry)

    def ping(self):
        """
        Determine if it's possible to communicate with Sumo Logic.

        :return: Whether or not it's possible to establish a connection to Sumo Logic
        :rtype: bool
        """
        try:
            self.get('collectors')
            return True
        except Exception:
            return False

    def get_collectors(self,  limit=1000, ids=None):
        """
        Retrieve a list of collectors.

        :param limit: The number of collectors to ask for in each
            request. If you're looking for a specific server, it might
            makes sense to only retrieve a few collectors. However, if
            you have a lot of collectors and want them all, it would
            make sense to set the limit super high and get them all in
            a single request.
        :type limit: int
        :param ids: The IDs of the collectors to be retrieved. If the
            argument isn't set, all of the collectors will be returned.
        :return: A list of dicts representing collectors.
        :rtype: generator
        :raises sumologic.exceptions.InvalidJSONResponseError: When it
            fails to retrieve necessary data from the JSON response.
        """
        offset = 0

        while True:
            r = self.get('collectors', params={
                'limit': limit,
                'offset': offset
            })

            try:
                if len(r.json()['collectors']) == 0:
                    break

                for collector in r.json()['collectors']:
                    if ids is None:
                        yield sumologic.collector.Collector(collector['id'], self)
                    elif collector['id'] in ids:
                        ids.remove(collector['id'])
                        yield sumologic.collector.Collector(collector['id'], self)
            except KeyError:
                raise sumologic.exceptions.InvalidJSONResponseError()

            offset += limit

        if ids is not None and len(ids) > 0:
            raise sumologic.exceptions.InvalidCollectorIdError(', '.join(ids))
