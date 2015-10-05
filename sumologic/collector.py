import sumologic.exceptions


class Collector(object):
    client = None
    id_ = None
    _source = {}
    etag = None

    attributes = {
        'id': {
            'type': int,
            'mutable': False
        },
        'name': {
            'type': str,
        },
        'description': {
            'type': str
        },
        'category': {
            'type': str
        },
        'hostName': {
            'type': str
        },
        'timeZone': {
            'type': str
        },
        'ephemeral': {
            'type': bool
        },
        'targetCpu': {
            'type': int
        },
        'collectorType': {
            'type': str,
            'mutable': False
        },
        'collectorVersion': {
            'type': str,
            'mutable': False
        },
        'alive': {
            'type': bool,
            'mutable': False,
            'transient': True
        },
        'cutoffTimestamp': {
            'type': int,
        },
        'cutoffRelativeTime': {
            'type': str
        },
        'sources': {
            'type': list,
            'mutable': False
        }
    }

    installable_collector_attributes = {
        'osName': {
            'type': str,
            'mutable': False
        },
        'osVersion': {
            'type': str,
            'mutable': False
        },
        'osArch': {
            'type': str,
            'mutable': False
        },
        'upTime': {
            'type': int,
            'mutable': False,
            'transient': True
        }
    }

    def __init__(self, id_, client):
        self.client = client
        self.id_ = id_

        self.reload()

    def reload(self):
        r = self.client.get('collectors/{id_}'.format(id_=self.id_))

        try:
            self.etag = r.headers['ETag']
        except KeyError:
            raise sumologic.exceptions.InvalidHTTPResponseError()

        try:
            collector = r.json()['collector']

            for key in self.attributes:
                if key in collector:
                    if isinstance(collector[key],
                                  self.attributes[key]['type']):
                        self._source[key] = collector[key]
                    else:
                        raise sumologic.exceptions.InvalidJSONResponseError()

            if self._source.get("collectorType", "") == "Installable":
                for key in self.installable_collector_attributes:
                    if key in collector:
                        if isinstance(collector[key],
                                      self.installable_collector_attributes[key]['type']):
                            self._source[key] = collector[key]
                        else:
                            raise sumologic.exceptions.InvalidJSONResponseError()

        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()

        r = self.client.get('collectors/{id_}/sources'.format(id_=self.id_))

        try:
            self._source['sources'] = r.json()['sources']
        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()

    def __getattr__(self, key):
        if key in self.attributes:
            try:
                return self._source[key]
            except KeyError:
                return None
        else:
            super().__getattribute__(key)

    def __setattr__(self, key, value):
        if key in self.attributes:
            if self.attributes[key].get('mutable', False):
                self._source[key] = value
            else:
                raise sumologic.exceptions.AttemptedMutationOfImmatubleAttributeError()
        else:
            super().__setattr__(key, value)
