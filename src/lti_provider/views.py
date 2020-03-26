"""Views of the lti_provider django application."""
from abc import ABC, abstractmethod

from django import http
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from lti_provider.exceptions import LTIException

from .defaults import LTI_LAUNCH_FAILURE_HANDLER, LTI_LAUNCH_SUCCESS_HANDLER
from .lti import LTI


@csrf_exempt
def launch(request: HttpRequest) -> HttpResponse:
    """Verify LTI launch request and call hook depending on the result."""
    lti = LTI(request)
    try:
        lti.verify()
        response = import_string(LTI_LAUNCH_SUCCESS_HANDLER)(request, lti)
        # If no response is given by the callback, send an empty HTTP 200 response
        return (
            response if isinstance(response, http.HttpResponse) else http.HttpResponse()
        )
    except LTIException as error:
        response = import_string(LTI_LAUNCH_FAILURE_HANDLER)(request, error)
        if isinstance(response, http.HttpResponse):
            return response
        # If no response is given by the callback, send an empty HTTP 403 response
        return http.HttpResponseForbidden()


@method_decorator(csrf_exempt, name="dispatch")
class BaseLTIView(ABC, View):
    """
    Abstract view to help building LTI authenticated views.
    It is convenient if you want to handle dynamic LTI launch URLs.
    """

    def post(self, request, *args, **kwargs) -> HttpResponse:  # pylint: disable=W0613
        """Handler for POST requests."""
        lti_request = LTI(request)
        try:
            lti_request.verify()
            user = authenticate(request, lti_request=lti_request)
            if user is not None:
                login(request, user)
                return self._do_on_login(lti_request)
            return HttpResponseForbidden()
        except LTIException:
            return HttpResponseForbidden()

    @abstractmethod
    def _do_on_login(self, lti_request: LTI) -> HttpResponse:
        """Process the request when the user is logged in via LTI"""
        raise NotImplementedError()
