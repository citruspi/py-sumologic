import sumologic.exceptions


class Collector(object):
    client = None
    id_ = None
    _source = None
    etag = None

    expected_attributes = [
        'id',
        'name',
        'description',
        'category',
        'hostName',
        'timeZone',
        'ephemeral',
        'targetCpu',
        'collectorType',
        'collectorVersion',
        'alive',
        'cutoffTimestamp',
        'cutoffRelativeTime',
        'sources'
    ]

    def __init__(self, id, client):
        self.client = client
        self.id_ = id

        self.reload()

    def reload(self):
        r = self.client.get('collectors/{id_}'.format(id_=self.id_))

        try:
            self.etag = r.headers['ETag']
        except KeyError:
            raise sumologic.exceptions.InvalidHTTPResponseError()

        try:
            self._source = r.json()['collector']
        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()

        r = self.client.get('collectors/{id_}/sources'.format(id_=self.id_))

        try:
            self._source['sources'] = r.json()['sources']
        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()

    def __getattr__(self, key):
        if key in self.expected_attributes:
            try:
                return self._source[key]
            except KeyError:
                return None
        else:
            super().__getattribute__(key)

    def __setattr__(self, key, value):
        if key in self.expected_attributes:
            self._source[key] = value
        else:
            super().__setattr__(key, value)
