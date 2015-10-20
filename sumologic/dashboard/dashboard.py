import sumologic.exceptions


class Dashboard(object):

    _raw = {
        'id': None,
        'title': None,
        'description': None,
        'properties': {},
        'monitors': []
    }

    def __init__(self, id, client):
        self._raw['id'] = id
        self.client = client

        self.reload()

    def reload(self):
        r = self.client.get('dashboards/{id_}'.format(id_=self._raw['id']),
                            params={'monitors': 'yes'})

        try:
            self._raw.update(r.json()['dashboard'])
        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()

    @property
    def title(self):
        return self._raw['title']

    @property
    def description(self):
        return self._raw['description']

    @property
    def properties(self):
        return self._raw['properties']

    @property
    def monitors(self):
        return self._raw['dashboardMonitors']

    @property
    def data(self):
        r = self.client.get('dashboards/{id_}/data'.format(id_=self._raw['id']))

        try:
            return r.json()['dashboardMonitorDatas']
        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()