from requests import Session, Request
from urllib.parse import urlencode, urljoin
from requests.adapters import Response
from requests.adapters import CaseInsensitiveDict as Header
from json import dumps as json_dump
from json import loads as json_load
from requests.sessions import PreparedRequest

_NO_JSON_DATA = object()

class Client(object):
    def __init__(self, session=None, base_url=None, timeout=None):
        self._session = session if session is not None else Session()
        self._base_url = base_url
        
    def get(self, url, **kwargs):
        return self.request("GET", url=url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request("POST", url=url, data=data, json=json, **kwargs)

    def request(
        self, method: str, url: str,
        headers=None, params=None, data=None,
        json=None, timeout=None
    ):
        headers = self.__generate_headers(headers)
        parsed_url = self.__generate_url(url, params)
        body, content_type = self.__generate_req_body(data, json)

        if content_type is not None:
            headers.update({"Content-Type": content_type})

        req: Request = Request(method, parsed_url, data=body, headers=headers)
        prepped: PreparedRequest = req.prepare()

        resp: Response = self._session.send(prepped, timeout=timeout)

        return resp
        
    def __generate_headers(self, headers: dict):
        if isinstance(headers, dict):
            req_header = Header()
            for key, value in headers.items():
                if isinstance(value, (bytes, str)):
                    req_header.update({key: value})
                elif isinstance(value, list[str]):
                    req_header.update({key, value})
                else:
                    raise TypeError(
                        "value of key['{}'] has non-string type {}".format(key, type(value))
                    )
            return req_header
            
        if headers is None:
            return Header()

        raise TypeError(
            "headers must be a dict, CaseInsensitiveDict, or None. input: {}"
            .format(type(headers))
        )

    def __generate_req_body(self, data, json):
        if json is not _NO_JSON_DATA and data is not None:
            raise TypeError("data and json cannot co-exist")
        if isinstance(data, (dict, list, tuple)):
            return (
                urlencode(data, doseq=True),
                b'application/x-www-form-urlencoded',
            )
        elif data:
            return (
                self._to_body_producer(data),
                None,
            )
        if json is not _NO_JSON_DATA:
            return (
                json_dump(json).encode('utf-8'),
                b'application/json; charset=UTF-8',
            )
        return None, None

    def __generate_url(self, url, params):
        parsed_url = urljoin(self._base_url, url, params)
        return parsed_url

