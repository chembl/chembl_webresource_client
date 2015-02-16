__author__ = 'mnowotka'

#-----------------------------------------------------------------------------------------------------------------------

class BaseHttpException(Exception):
    def __init__(self, url, content):
        super(BaseHttpException, self).__init__(url)

        self.url = url
        self.content = content

    def __repr__(self):
        return 'Error for url %s, server response: %s' % (self.url, self.content)

#-----------------------------------------------------------------------------------------------------------------------

class HttpBadRequest(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpUnauthorized(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpForbidden(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpNotFound(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpMethodNotAllowed(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpConflict(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpGone(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpUnprocessableEntity(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpTooManyRequests(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpApplicationError(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

class HttpNotImplemented(BaseHttpException):
    pass

#-----------------------------------------------------------------------------------------------------------------------

status_to_exception = {
    400: HttpBadRequest,
    401: HttpUnauthorized,
    403: HttpForbidden,
    404: HttpNotFound,
    405: HttpMethodNotAllowed,
    409: HttpConflict,
    410: HttpGone,
    422: HttpUnprocessableEntity,
    429: HttpTooManyRequests,
    500: HttpApplicationError,
    501: HttpNotImplemented
}

#-----------------------------------------------------------------------------------------------------------------------

def handle_http_error(request):
    if not request.ok:
        exception_class = status_to_exception.get(request.status_code, BaseHttpException)
        if request.text:
            raise exception_class(request.url, request.text)
        raise exception_class(request.url, request.content)

#-----------------------------------------------------------------------------------------------------------------------
