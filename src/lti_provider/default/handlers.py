"""This module contains default handlers for LTI launch request."""

from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from ..exceptions import LTIException
from ..lti import LTI


def success(request: HttpRequest, lti_request: LTI) -> HttpResponse:
    """
    Default handler for successfully verified LTI launch requests.
    You are encouraged to define your own handler according to your project needs.
    It can be used to call an authentication backend, to redirect the user...etc

    See LTI_LAUNCH_SUCCESS_HANDLER setting.

    Args:
        request: The HTTP request
        lti_request: The verified LTI request

    Returns:
        HttpResponse: An HTTP response
    """

    user = authenticate(request, lti_request=lti_request)
    if user is not None:
        login(request, user)
        return HttpResponse("Welcome, user {}".format(user.username))
    return HttpResponseForbidden("Permission denied")


# pylint: disable=unused-argument
def failure(request: HttpRequest, error: LTIException) -> HttpResponse:
    """
    Default handler for invalid LTI launch requests.
    You are encouraged to define your own handler according to your project needs.

    See LTI_LAUNCH_FAILURE_HANDLER setting.

    Args:
        request: the HTTP request
        error: The LTIException encountered

    Returns:
        HttpResponse: An HTTP response
    """
    return HttpResponseForbidden("Invalid LTI launch request")
