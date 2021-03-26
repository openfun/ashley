"""
Tests for the ashley.models.LTIContext model.
"""
from django.conf import settings
from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

GroupForumPermission = get_model(  # pylint: disable=C0103
    "forum_permission", "GroupForumPermission"
)
LTIContext = get_model("ashley", "LTIContext")  # pylint: disable=C0103
Forum = get_model("forum", "Forum")  # pylint: disable=C0103


class ManageModeratorTestCase(TestCase):
    """Test the access of the manage moderators dashboard"""

    def test_browsing_with_can_manage_moderator_forum_permission(self):
        """
        A user with the `can_manage_moderator_forum` permission and
        `SESSION_LTI_CONTEXT_ID` should be able to access it.
        """
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        assign_perm("can_manage_moderator", user, forum, True)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/moderators/")
        # Controls the page is forbidden as session is not set
        self.assertEqual(403, response.status_code)

        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        # Now session and permission are set, we should be able to access it
        response = self.client.get("/moderators/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Manage forum's moderators")

    def test_browsing_basic_user(self):
        """
        A user without the `can_manage_moderator` permission should not be able
        to access the page .
        """
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        # Check user can access forum view
        response = self.client.get("/forum/")
        self.assertEqual(200, response.status_code)
        # Check user can't access moderators view
        response = self.client.get("/moderators/")
        self.assertEqual(302, response.status_code)
        # Check user gets redirected to login page
        self.assertIn(settings.LOGIN_URL, response.url)

        # Authenticate user
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/moderators/")
        # Controls the page is forbidden
        self.assertEqual(403, response.status_code)

        # Add session manually
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/moderators/")
        # Controls the page is still forbidden
        self.assertEqual(403, response.status_code)
