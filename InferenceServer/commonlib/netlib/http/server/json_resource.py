from json5 import loads as json_load
from twisted.internet.defer import CancelledError, Deferred, maybeDeferred
from twisted.internet.error import ConnectError, ConnectionDone, ConnectionLost
from commonlib.glog import glog
from twisted.python.failure import Failure
from twisted.web.error import Error
from twisted.web.resource import Resource
from twisted.web.http import INTERNAL_SERVER_ERROR
from twisted.web.server import Request, NOT_DONE_YET
from commonlib.netlib.http.server.response import HttpResponse


class JsonResource(Resource):   

    def __init__(self):
        super().__init__()
 

    def post(self, request: Request):
        raise NotImplementedError()

    def get(self, request: Request):
        raise NotImplementedError()

    def patch(self, request: Request):
        raise NotImplementedError()

    def delete(self, request: Request):
        raise NotImplementedError()


    def parse_body(self, request: Request):
        body_string = request.content.read().decode("utf-8")
        body = json_load(body_string)
        return body


    def render(self, request: Request):
        try:
            request.body = self.parse_body(request)
        except Exception:
            self.__handle_exception(request)
            return NOT_DONE_YET
        else:
            return super().render(request)
 

    def render_POST(self, request: Request):
        deferred: Deferred = maybeDeferred(self.post, request)
        deferred.addCallback(self.__send_response, request)
        deferred.addErrback(self.__handle_failure, request)

        request.notifyFinish().addErrback(self.on_connection_lost, deferred)

        return NOT_DONE_YET

    def on_connection_lost(self, deferred):
        deferred.cancel()

    def render_GET(self, request: Request):
        deferred: Deferred = maybeDeferred(self.get, request)
        deferred.addCallback(self.__send_response, request)
        deferred.addErrback(self.__handle_failure, request)

        request.notifyFinish().addErrback(self.on_connection_lost, deferred)

        return NOT_DONE_YET


    def render_PATCH(self, request: Request):
        deferred: Deferred = maybeDeferred(self.patch, request)
        deferred.addCallback(self.__send_response, request)
        deferred.addErrback(self.__handle_failure, request)

        request.notifyFinish().addErrback(self.on_connection_lost, deferred)

        return NOT_DONE_YET


    def render_DELETE(self, request: Request):
        deferred: Deferred = maybeDeferred(self.delete, request)

        deferred.addCallback(self.__send_response, request)
        deferred.addErrback(self.__handle_failure, request)

        request.notifyFinish().addErrback(self.on_connection_lost, deferred)

        return NOT_DONE_YET    


    def on_connection_lost(self, failure: Failure, deferred: Deferred):
        glog.error(f"connection lost: {failure.value}. cancel api handler")
        deferred.cancel()


    def __send_response(self, response: HttpResponse, request: Request, status_code: int = 200, status_message: bytes = None):
        try:
            request.setResponseCode(status_code, status_message)
            if response is not None and response.headers is not None:
                for key, value in response.headers.items():
                    request.setHeader(key ,value)

                if response.content is not None:
                    request.write(response.content)
        except Exception as e:
            glog.error(f"[{e.__class__.__name__}] at __send_response: {e}")
            request.finish()
            return

        request.finish()
    

    def __handle_exception(self, request: Request):
        self.__handle_failure(Failure(), request)


    def __handle_failure(self, failure: Failure, request: Request):
        exception = failure.value

        if isinstance(exception, (CancelledError, ConnectError, ConnectionDone, ConnectionLost)):
            return

        if isinstance(exception, Error):
            status_code = int(exception.status)
            if status_code >= 400 and status_code < 500:
                message = b"{} {}".format(status_code, exception.message.decode("utf-8"))
                self.__send_error(status_code, message, request)
                return

        # 처리가 되지 않은 exception
        glog.error(f"Unhandled Exception: {exception}")
        self.__send_error(INTERNAL_SERVER_ERROR, b"Internal Error", request)


    def __send_error(self, status_code, message, request):
        self.__send_response(None, request, status_code=status_code, status_message=message)
