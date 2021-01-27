from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import LTIContextFactory, UserFactory
from ashley.machina_extensions.forum_permission.middleware import (
    ForumPermissionMiddleware,
)


class ForumPermissionMiddlewareTestCase(TestCase):
    """Test the ForumPermission middleware"""

    def test_lti_context_id(self):
        """
        When the `SESSION_LTI_CONTEXT_ID` is set in the user session, it should
        be injected into the PermissionHandler instance that is stored in the
        request object.
        """

        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)

        # Generate a request
        request = RequestFactory().get("/")

        # Attach a user to the request
        request.user = user

        # Attach a session to the request
        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request)

        # Store the LTIContext id in the session
        request.session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        self.assertEqual(request.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id)

        # Execute the ForumPermissionMiddleware on the request
        permission_middleware = ForumPermissionMiddleware(lambda r: None)
        permission_middleware.process_request(request)

        # The permission handler instance should have been injected, with the
        # right current_lti_context_id
        self.assertEqual(
            request.forum_permission_handler.current_lti_context_id, lti_context.id
        )

    def test_lti_context_id_anonymous(self):
        """
        The ForumPermissionMiddleware should not inject any LTIContext id in
        the permission handler for request made by anonymous users.
        """
        lti_context = LTIContextFactory()

        # Generate an anonymous request (with no LTIContext ID in session)
        request_without_lti_context = RequestFactory().get("/")
        request_without_lti_context.user = AnonymousUser()
        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request_without_lti_context)
        permission_middleware = ForumPermissionMiddleware(lambda r: None)
        permission_middleware.process_request(request_without_lti_context)

        # The permission handler should have been injected, without the current_lti_context_id
        self.assertIsNotNone(request_without_lti_context.forum_permission_handler)
        self.assertIsNone(
            request_without_lti_context.forum_permission_handler.current_lti_context_id
        )

        # Generate an anonymous request (with a LTIContext ID in session)
        request_with_lti_context = RequestFactory().get("/")
        request_with_lti_context.user = AnonymousUser()
        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request_with_lti_context)
        request_with_lti_context.session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        self.assertEqual(
            request_with_lti_context.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )
        permission_middleware = ForumPermissionMiddleware(lambda r: None)
        permission_middleware.process_request(request_with_lti_context)

        # The permission handler should have been injected, without the current_lti_context_id
        self.assertIsNotNone(request_with_lti_context.forum_permission_handler)
        self.assertIsNone(
            request_with_lti_context.forum_permission_handler.current_lti_context_id
        )
