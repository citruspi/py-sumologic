class AuthenticationError(Exception):
    pass


class HTTPError(Exception):
    pass


class InvalidHTTPMethodError(Exception):
    pass


class InvalidHTTPResponseError(Exception):
    pass


class InvalidJSONResponseError(Exception):
    pass


class InvalidCollectorIdError(Exception):
    pass