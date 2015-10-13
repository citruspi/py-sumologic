import sumologic.exceptions

class Dashboard(object):
    id_ = None
    _raw = {}

    def __init__(self, id_, client):
        self.id_ = id_
        self.client = client

        self.reload()

    def reload(self):
        r = self.client.get('dashboards/{id_}'.format(id_=self.id_),
                            params={'monitors': 'yes'})

        try:
            self._raw = r.json()['dashboard']
        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()

    @property
    def title(self):
        return self._raw['title'] or None

    @property
    def description(self):
        return self._raw['description'] or None

    @property
    def properties(self):
        return self._raw['properties'] or {}

    @property
    def monitors(self):
        return self._raw['dashboardMonitors'] or []

    @property
    def data(self):
        r = self.client.get('dashboards/{id_}/data'.format(id_=self.id_))

        try:
            return r.json()['dashboardMonitorDatas']
        except KeyError:
            raise sumologic.exceptions.InvalidJSONResponseError()