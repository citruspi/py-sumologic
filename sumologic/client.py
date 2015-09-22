#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Client(object):

    api_base = 'https://api.us2.sumologic.com/api'
    api_version = 'v1'
    auth = ()

    def __init__(self, access_id=None, access_key=None):
        """
        :param access_id: The Access ID to connect with
        :param access_key: The Access Key to connect with
        """
        self.auth=(access_id, access_key)