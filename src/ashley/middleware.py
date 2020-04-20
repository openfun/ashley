"""Declare the middlewares related to Ashley ."""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SameSiteNoneMiddleware(MiddlewareMixin):
    """
    This middleware forces the attribute SameSite="None" for CSRF and SESSION
    cookies.

    Django < 3.1 does not allow to set the SameSite="None" for the
    session and CSRF cookies. As a result, it causes issues with modern
    browsers that consider SameSite="Lax" by default.

    This middleware is a temporary fix until this feature is available
    in a stable version of Django.
    """

    @staticmethod
    def process_response(request, response):
        """Force the samesite=None on session and CSRF cookies if defined."""

        if settings.SESSION_COOKIE_NAME in response.cookies:
            response.cookies[settings.SESSION_COOKIE_NAME]["samesite"] = "None"
        if settings.CSRF_COOKIE_NAME in response.cookies:
            response.cookies[settings.CSRF_COOKIE_NAME]["samesite"] = "None"
        return response
