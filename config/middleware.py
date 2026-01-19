import uuid
import threading

_request_local = threading.local()


def get_request_id():
    return getattr(_request_local, "request_id", None)


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        _request_local.request_id = request_id

        request.request_id = request_id
        response = self.get_response(request)

        response["X-Request-ID"] = request_id
        return response
