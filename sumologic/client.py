#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import configparser

import requests

import sumologic.exceptions


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