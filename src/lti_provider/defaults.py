"""This module contains default settings for lti_provider application."""

from django.conf import settings

# When a LTI launch request is successfully verified, the handler function defined
# in the LTI_LAUNCH_SUCCESS_HANDLER setting is called with 2 parameters :
# 1. The request (django.http.request.HttpRequest)
# 2. The verified LTI request (lti_provider.lti.LTI)
#
# The handler should return a valid HTTP response (django.http.HttpResponse)
# A default implementation is given in this application as an exemple
#
# If you use the default implementation, you must add the following
# authentication backend in your AUTHENTICATION_BACKENDS setting:
#   "lti_provider.default.backend.AuthBackend"
#

LTI_LAUNCH_SUCCESS_HANDLER = getattr(
    settings, "LTI_LAUNCH_SUCCESS_HANDLER", "lti_provider.default.handlers.success"
)

# When a LTI launch request is invalid, the handler function defined in the
# LTI_LAUNCH_FAILURE_HANDLER is called with the following parameters:
# 1. The request (django.http.request.HttpRequest)
# 2. The LTIException
#
# The handler should return a valid HTTP response (django.http.HttpResponse)
# A default implementation is given in this application as an example.
LTI_LAUNCH_FAILURE_HANDLER = getattr(
    settings, "LTI_LAUNCH_FAILURE_HANDLER", "lti_provider.default.handlers.failure"
)
