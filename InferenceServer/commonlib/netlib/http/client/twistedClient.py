# from twisted.internet import defer
# from twisted.internet.defer import Deferred, returnValue, succeed
# from twisted.web._newclient import Response
# from twisted.python.components import proxyForInterface, registerAdapter
# from twisted.web.client import Agent, FileBodyProducer, HTTPConnectionPool
# from twisted.web.http_headers import Headers
# from twisted.web.iweb import UNKNOWN_LENGTH, IBodyProducer, IResponse
# from urllib.parse import urlencode, urljoin
# from json import dumps as json_dump
# from json import loads as json_load

# from twisted.internet.protocol import Protocol
# from twisted.web.client import ResponseDone
# import io

# _NO_JSON_DATA = object()


# # Received 된 body 정보를 가져오고,
# # 해당 response의 body가 전부 받아졌는지 체크 후 connectionLost까지 수행
# class _ResponseBodyReader(Protocol):
#     # finished: Deferred 오브젝트
#     # dataReceived가 불릴때 데이터를 가져다 붙이는 메써드
#     def __init__(self, finished: Deferred, collector):
#         self.finished = finished
#         self.collector = collector

#     def dataReceived(self, data):
#         self.collector(data)

#     # Response Body Deferred 트리거
#     def connectionLost(self, reason):
#         if reason.check(ResponseDone):
#             self.finished.callback(None)
#         else:
#             self.finished.errback(reason)

# # Response Content 관련 핸들러
# def collect_content(response: Response, collector):
#     if response.length == 0:
#         return succeed(None)

#     # Response Body Deferred 등록
#     deferred = Deferred()
#     response.deliverBody(_ResponseBodyReader(deferred, collector))
#     return deferred


# def content(response: Response):
#     response_body = []
#     deferred = collect_content(response, response_body.append)

#     def join_body(_):
#         return b''.join(response_body)

#     deferred.addCallback(join_body)
#     return deferred


# def text_content(response: Response, encoding='utf-8'):

#     def decode_content(content):
#         return content.decode(encoding)

#     deferred = content(response)
#     deferred.addCallback(decode_content)

#     return deferred


# def json_content(response: Response, **kwargs):
#     deferred = text_content(response, encoding='utf-8')

#     def load_json(text):
#         return json_load(text, **kwargs)

#     deferred.addCallback(load_json)

#     return deferred


# # agent.request() Deferred의 Callback으로 등록할 Response Proxy객체
# # IResponse에 연결된 메써드를 모두 _Response로 proxy 해준다.
# class _Response(proxyForInterface(IResponse)):
#     def __init__(self, original_response: Response):
#         self.original = original_response

#     def __repr__(self):
#         if self.original.length == UNKNOWN_LENGTH:
#             size = 'UNKNOWN_LENGTH'
#         else:
#             size = '{} bytes'.format(self.original.length)

#         content_type_bytes = b', '.join(
#             self.original.headers.getRawHeaders(b'Content-Type', ())
#         )
#         content_type = repr(content_type_bytes).lstrip('b')[1:-1]
#         return "[ {} ] Content-Type: '{}', size: {}".format(
#             self.original.code,
#             content_type,
#             size,
#         )
    
#     def json(self, **kwargs):
#         return json_content(self.original, **kwargs)

#     def text(self, encoding):
#         return text_content(self.original, encoding)


# class Client(object):
#     def __init__(self, reactor=None, body_producer=IBodyProducer, pool=None, connectionTimeout=None, base_url=None):
#         # reactor를 밖에서 가지고 오지 않고도 사용할 수 있도록
#         if reactor is None:
#             from twisted.internet import reactor
#         self._reactor = reactor
#         self.pool =  pool if pool is not None else HTTPConnectionPool(self._reactor)
#         self._agent = Agent(self._reactor, connectTimeout=connectionTimeout, pool=self.pool)
#         self._body_producer = body_producer
#         self._base_url = base_url
        

#     def get(self, url, **kwargs):
#         return self.request(b"GET", url=url, **kwargs)


#     def post(self, url, data=None, json=None, **kwargs):
#         return self.request(b"POST", url=url, data=data, json=json, **kwargs)


#     def patch(self, url, data=None, json=None, **kwargs):
#         return self.request(b"PATCH", url=url, data=data, json=json, **kwargs)


#     def request(
#         self, method, url,
#         headers=None, params=None, data=None,
#         json=_NO_JSON_DATA, timeout=2000
#     ):

#         # request header 새성
#         req_header = self.__generate_headers(headers)

#         # request url 생성
#         parsed_url = self.__generate_url(url, params).encode('ascii')
        
#         # request body 생성
#         body_producer, content_type = self.__generate_req_body(data, json)
#         if content_type is not None:
#             req_header.setRawHeaders(b'Content-Type', [content_type])
            
#         # 요청 Deferred 등록
#         deferred = self._agent.request(method, parsed_url, req_header, body_producer)

#         # timeout Deferred 등록
#         if timeout is not None:
#             # timeout 시간만큼 기다렸다가 deferred.cancel를 부르도록 등록
#             timeout_call = self._reactor.callLater(timeout, deferred.cancel)

#             # 응답이 도착했을때 timeout_call이 등록되어있으면 취소
#             def cancel_on_response(result):
#                 if timeout_call.active():
#                     timeout_call.cancel()
#                 return result

#             deferred.addBoth(cancel_on_response)

#         # 사용-편의를 위해 custom Response 객체를 콜백으로 등록
#         return deferred.addCallback(_Response)

#     def __generate_headers(self, headers: dict) -> Headers:
#         if isinstance(headers, dict):
#             req_header: Headers = Headers({})
#             for key, value in headers.items():
#                 if isinstance(value, (bytes, str)):
#                     req_header.addRawHeader(key, value)
#                 elif isinstance(value, list[str]):
#                     req_header.setRawHeaders(key, value)
#                 else:
#                     raise TypeError(
#                         "value of key['{}'] has non-string type {}".format(key, type(value))
#                     )
#             return req_header

#         if isinstance(headers, Headers):
#             return headers
            
#         if headers is None:
#             return Headers({})

#         raise TypeError(
#             "headers must be a dict, twisted.web.http_headers.Headers, or None. input: {}"
#             .format(type(headers))
#         )


#     def __generate_req_body(self, data, json):
#         if json is not _NO_JSON_DATA and data is not None:
#             raise TypeError("data and json cannot co-exist")
#         if isinstance(data, (dict, list, tuple)):
#             return (
#                 self._body_producer(urlencode(data, doseq=True)),
#                 b'application/x-www-form-urlencoded',
#             )
#         elif data:
#             return (
#                 self._body_producer(data),
#                 None,
#             )
#         if json is not _NO_JSON_DATA:
#             return (
#                 self._body_producer(json_dump(json).encode('utf-8')),
#                 b'application/json; charset=UTF-8',
#             )
#         return None, None


#     def __generate_url(self, url, params) -> str:
        
#         # TODO 이거 만들어야함..
#         # query string + post form + endpoint 연결 등등.. 파싱 등등
#         parsed_url = urljoin(self._base_url, url, params)
#         print(f"parsed_url : {parsed_url}")
#         return parsed_url


# # register different type of BodyProducer
# def __from_bytes(orig_bytes: bytes):
#     return FileBodyProducer(io.BytesIO(orig_bytes))

# registerAdapter(__from_bytes, bytes, IBodyProducer)
