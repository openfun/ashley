from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

Forum = get_model("forum", "Forum")  # pylint: disable=C0103


class ForumArchiveTestCase(TestCase):
    """Test the rename admin feature of a forum"""

    def setUp(self):
        super().setUp()

    def test_basic_user(self):
        """
        A user without the `can_archive_forum` permission
        should not be able to archive it.
        """
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum)

        self.assertFalse(forum.archived)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")

        # The user can read the forum
        response = self.client.get(f"/forum/forum/{forum.slug}-{forum.pk}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, forum.name)

        # but he's not allowed to archive it
        response = self.client.get(f"/forum/admin/archive/{forum.pk}/")
        self.assertEqual(403, response.status_code)

        update_response = self.client.post(f"/forum/admin/archive/{forum.pk}/")
        self.assertEqual(403, update_response.status_code)

        self.assertFalse(Forum.objects.get(pk=forum.pk).archived)

    def test_with_can_archive_forum_permission(self):
        """
        A user with the `can_archive_forum` permission should be able
        to archive it.
        """

        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        assign_perm("can_read_forum", user, forum, True)
        assign_perm("can_archive_forum", user, forum, True)

        self.assertFalse(forum.archived)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")

        # The user can access the forum
        response = self.client.get(f"/forum/forum/{forum.slug}-{forum.pk}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, forum.name)

        # He can access the form that allows to archive it
        response = self.client.get(f"/forum/admin/archive/{forum.pk}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Delete the forum")

        # He can archive it
        update_response = self.client.post(f"/forum/admin/archive/{forum.pk}/")
        self.assertEqual(302, update_response.status_code)
        self.assertTrue(Forum.objects.get(pk=forum.pk).archived)

        # And once it's done, he can no longer access it
        response = self.client.get(f"/forum/forum/{forum.slug}-{forum.pk}/")
        self.assertEqual(404, response.status_code)
