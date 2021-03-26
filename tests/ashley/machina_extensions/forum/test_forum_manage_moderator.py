from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

Forum = get_model("forum", "Forum")


class ForumButtonManageModeratorTestCase(TestCase):
    """Test the display button to manage moderator on forum view"""

    def test_forum_display_button_manage_moderator(self):
        """
        Connects a user with standard forum permission and controls that CTA to manage
        moderator is not present, then add the permission can_manage_moderator and
        control that we now see the CTA as expected
        """
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory(name="Initial forum name")
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum)

        # Connects user and go on the forum page
        self.client.force_login(user)
        response = self.client.get(f"/forum/forum/{forum.name}-{forum.id}/")

        # Check the CTA to manage moderators is not present
        self.assertNotContains(
            response,
            (
                '<a href="/moderators/" title="Manage moderators" class="dropdown-item">'
                "Manage moderators</a>"
            ),
            html=True,
        )
        # Assign permission can_manage_moderator
        assign_perm("can_manage_moderator", user, forum)
        response = self.client.get(f"/forum/forum/{forum.name}-{forum.id}/")

        # Check the CTA to manage moderators is now present
        self.assertContains(
            response,
            (
                '<a href="/moderators/" title="Manage moderators" class="dropdown-item">'
                "Manage moderators</a>"
            ),
            html=True,
        )
