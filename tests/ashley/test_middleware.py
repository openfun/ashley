"""Test suite for Ashley's middlewares"""
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase

from ashley.middleware import SameSiteNoneMiddleware


class SameSiteNoneMiddlewareTestCase(TestCase):
    """Test the SameSiteNoneMiddleware middleware"""

    def setUp(self):
        """Override the setUp method to instanciate and serve a request factory."""
        super().setUp()
        self.request_factory = RequestFactory()

    def test_samesite_override(self):
        """Test that the samesite attribute is rewritten for session and CSRF cookies"""

        def get_response(request: HttpRequest) -> HttpResponse:
            test_response = HttpResponse("OK")
            # Set a session cookie with samesite=lax
            test_response.set_cookie(
                settings.SESSION_COOKIE_NAME, value="session_cookie", samesite="lax"
            )
            # Set a CSRF cookie with no samesite attribute
            test_response.set_cookie(settings.CSRF_COOKIE_NAME, value="csrf_cookie")
            # Set another custom cookie with samesite=strict attribute
            test_response.set_cookie(
                "another_cookie", value="some_value", samesite="strict"
            )
            return test_response

        middleware = SameSiteNoneMiddleware(get_response)
        response = middleware(self.request_factory.get("/"))

        # The middleware should have transformed samesite=lax into samesite=None
        # for the session cookie
        self.assertEqual(
            "None", response.cookies[settings.SESSION_COOKIE_NAME]["samesite"]
        )
        # The middleware should have added a samesite=None attribute to the CSRF cookie
        self.assertEqual(
            "None", response.cookies[settings.CSRF_COOKIE_NAME]["samesite"]
        )
        # The middleware should not have changed the samesite attribute for the custom cookie
        self.assertEqual("strict", response.cookies["another_cookie"]["samesite"])
