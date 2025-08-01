from json5 import dumps as json_dump
from twisted.web.http import OK

from commonlib.gerror import GError

class HttpResponse(object):

    status_code = OK
    status_message = "OK"
    charset = "utf-8"

    def __init__(self, status_code=None, status_message=None, headers=None, content_type=None, content=None):
        self.headers = headers or dict()
        self.content_type = content_type
        self.content = content
        
        if content_type and 'Content-Type' in self.headers:
            raise AttributeError(
                "Content-Type in headers and content-type parameter must not coexist" 
            )

        if 'Content-Type' not in self.headers:
            if content_type is None:
                content_type = 'text/html; charset=%s' % self.charset
            self.headers['Content-Type'] = content_type

        if status_code is not None:
            try:
                self.status_code = int(status_code)
            except (ValueError, TypeError):
                raise TypeError('HTTP status code must be an integer.')

        if not 100 <= self.status_code <= 599:
            raise ValueError('HTTP status code must be an integer from 100 to 599.')

        # default header setting for CORS

        self.headers["Access-Control-Allow-Origin"] = "*"
        self.headers["Access-Control-Allow-Methods"] = "GET, POST"
        self.headers["Access-Control-Allow-Headers"] = "x-prototype-version,x-requested-with"
        self.headers["Access-Control-Max-Age"] = "1200"

        self.status_message = status_message

    def _apply_to_request(self, request):
        request.setResponseCode(self.code)
        for headerName, headerValueOrValues in self.headers.items():
            if not isinstance(headerValueOrValues, (str, bytes)):
                headerValues = headerValueOrValues
            else:
                headerValues = [headerValueOrValues]
            request.responseHeaders.setRawHeaders(headerName, headerValues)
        return self.content


class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        kwargs.setdefault('content_type', 'application/json; charset=utf-8')
        data['result'] = True
        data: bytes = json_dump(data).encode("utf-8")
        super().__init__(content=data, **kwargs)


class GErrorResponse(JsonResponse):
    def __init__(self, gerror: GError):
        data = {
            "result": False,
            "err_code": gerror.gcode,
            "err_msg": gerror.message,
        }
        super().__init__(data)