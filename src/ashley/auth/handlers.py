"""This module contains default handlers for LTI launch request"""

from django.contrib.auth import authenticate, login
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.urls import reverse

from lti_provider.exceptions import LTIException
from lti_provider.lti import LTI


# pylint: disable=unused-argument
def success(request: HttpRequest, lti_request: LTI) -> HttpResponse:
    """
    Handler for successfully verified LTI launch requests.

    First, it calls the authentication backends to try to authenticate
    the user with the LTI request.

    It will then redirect the user to the right forum, or
    display an error message.

    Args:
        request: The HTTP request
        lti_request: The verified LTI request

    Returns:
        HttpResponse: An HTTP response
    """

    user = authenticate(request, lti_request=lti_request)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("forum:index"))
    return HttpResponseForbidden("Forbidden")


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
