"""Views of the lti_provider django application."""

from django import http
from django.http import HttpRequest, HttpResponse
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt

from lti_provider.exceptions import LTIException

from .lti import LTI
from .settings import settings


@csrf_exempt
def launch(request: HttpRequest) -> HttpResponse:
    """Verify LTI launch request and call hook depending on the result."""
    lti = LTI(request)
    try:
        lti.verify()
        response = import_string(settings.LTI_LAUNCH_SUCCESS_HANDLER)(request, lti)
        # If no response is given by the callback, send an empty HTTP 200 response
        return (
            response if isinstance(response, http.HttpResponse) else http.HttpResponse()
        )
    except LTIException as error:
        response = import_string(settings.LTI_LAUNCH_FAILURE_HANDLER)(request, error)
        if isinstance(response, http.HttpResponse):
            return response
        # If no response is given by the callback, send an empty HTTP 403 response
        return http.HttpResponseForbidden()
