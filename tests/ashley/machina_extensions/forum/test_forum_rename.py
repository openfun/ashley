from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

Forum = get_model("forum", "Forum")  # pylint: disable=C0103


class ForumRenameTestCase(TestCase):
    """Test the rename admin feature of a forum"""

    def setUp(self):
        super().setUp()

    def test_basic_user(self):
        """
        A user without the `can_rename_forum` permission
        should not be able to rename it.
        """
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory(name="Initial forum name")
        forum.lti_contexts.add(lti_context)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get(f"/forum/admin/rename/{forum.pk}/")
        self.assertEqual(403, response.status_code)

        update_response = self.client.post(
            f"/forum/admin/rename/{forum.pk}/", data={"name": "Modified forum name"}
        )
        self.assertEqual(403, update_response.status_code)

        self.assertEqual("Initial forum name", Forum.objects.get(pk=forum.pk).name)

    def test_with_can_rename_forum_permission(self):
        """
        A user with the `can_rename_forum` permission should be able
        to rename it.
        """

        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory(name="Initial forum name")
        forum.lti_contexts.add(lti_context)

        assign_perm("can_rename_forum", user, forum, True)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get(f"/forum/admin/rename/{forum.pk}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Rename the forum")

        update_response = self.client.post(
            f"/forum/admin/rename/{forum.pk}/", data={"name": "Modified forum name"}
        )
        self.assertEqual(302, update_response.status_code)

        self.assertEqual("Modified forum name", Forum.objects.get(pk=forum.pk).name)
