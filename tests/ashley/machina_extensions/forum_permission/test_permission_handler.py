from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import ForumFactory, LTIContextFactory, UserFactory


class PermissionHandlerTestCase(TestCase):
    """Test the ForumPermission middleware"""

    def test_forum_list(self):
        user = UserFactory()
        lti_context_a = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context_b = LTIContextFactory(lti_consumer=user.lti_consumer)

        # Create 2 forums for context A
        forum_a1 = ForumFactory(name="Forum A1")
        forum_a1.lti_contexts.add(lti_context_a)
        forum_a2 = ForumFactory(name="Forum A2")
        forum_a2.lti_contexts.add(lti_context_a)
        # Create 2 forums for context B
        forum_b1 = ForumFactory(name="Forum B1")
        forum_b1.lti_contexts.add(lti_context_b)
        forum_b2 = ForumFactory(name="Forum B2")
        forum_b2.lti_contexts.add(lti_context_b)

        # Grant read-only access for forums A1, A2 and B1 to our user
        assign_perm("can_see_forum", user, forum_a1, True)
        assign_perm("can_read_forum", user, forum_a1, True)
        assign_perm("can_see_forum", user, forum_a2, True)
        assign_perm("can_read_forum", user, forum_a2, True)
        assign_perm("can_see_forum", user, forum_b1, True)
        assign_perm("can_read_forum", user, forum_b1, True)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session

        # Make a request to get the forum list, with an empty session
        response = self.client.get("/forum/")
        # We should see all forums we have access to
        self.assertContains(response, "Forum A1")
        self.assertContains(response, "Forum A2")
        self.assertContains(response, "Forum B1")
        self.assertNotContains(response, "Forum B2")

        # Update the client session to limit the user to the LTIContext A
        # Make a request to get he forum list again
        session[SESSION_LTI_CONTEXT_ID] = lti_context_a.id
        session.save()
        response = self.client.get("/forum/")

        # We should see only forums related to LTIContext A
        self.assertContains(response, "Forum A1")
        self.assertContains(response, "Forum A2")
        self.assertNotContains(response, "Forum B1")
        self.assertNotContains(response, "Forum B2")

        # Update the client session to limit the user to the LTIContext B
        # Make a request to get he forum list again
        session[SESSION_LTI_CONTEXT_ID] = lti_context_b.id
        session.save()
        response = self.client.get("/forum/")

        # We should see only forum B1
        self.assertNotContains(response, "Forum A1")
        self.assertNotContains(response, "Forum A2")
        self.assertContains(response, "Forum B1")
        self.assertNotContains(response, "Forum B2")
