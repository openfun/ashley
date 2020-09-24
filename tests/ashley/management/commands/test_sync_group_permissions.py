"""Test suite for the management command sync_group_permissions."""

from django.core.management import call_command
from django.test import TestCase, override_settings
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley.factories import ForumFactory, LTIContextFactory
from ashley.machina_extensions.forum.models import AbstractForum
from ashley.models import AbstractLTIContext

GroupForumPermission = get_model(
    "forum_permission", "GroupForumPermission"
)  # pylint: disable=C0103


class TestSyncGroupPermissionsCommand(TestCase):
    """Test the sync_group_permissions management command."""

    def setUp(self):
        super().setUp()

        # Instanciate factories
        self.lti_context_factory = LTIContextFactory
        self.forum_factory = ForumFactory

    def test_command(self):
        """Check the sync_group_permission behavior."""

        # Create a LTI context and a forum
        lti_context: AbstractLTIContext = self.lti_context_factory.create()
        forum: AbstractForum = self.forum_factory.create()
        forum.lti_contexts.add(lti_context)

        # Setup a group for the LTI role `instructor` with some initial permissions
        instructor_group = lti_context.get_role_group("instructor")
        assign_perm("can_see_forum", instructor_group, forum)
        assign_perm("can_read_forum", instructor_group, forum)

        # Setup a group for the LTI role `another_role` with some initial permissions
        another_group = lti_context.get_role_group("another_role")
        assign_perm("can_see_forum", another_group, forum)
        assign_perm("can_read_forum", another_group, forum)
        assign_perm("can_approve_posts", another_group, forum)

        # Check that our groups have the expected initial permissions
        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            self._get_group_forum_permissions(instructor_group, forum),
        )
        self.assertEqual(
            ["can_see_forum", "can_read_forum", "can_approve_posts"],
            self._get_group_forum_permissions(another_group, forum),
        )

        with override_settings(
            ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS={
                "instructor": ["can_see_forum", "can_lock_topics"]
            }
        ):
            # Run the command without argument
            call_command("sync_group_permissions")

            # By default, the command is in dry-run mode, so it should not have done anything
            # in database.

            self.assertEqual(
                ["can_see_forum", "can_read_forum"],
                self._get_group_forum_permissions(instructor_group, forum),
            )
            self.assertEqual(
                ["can_see_forum", "can_read_forum", "can_approve_posts"],
                self._get_group_forum_permissions(another_group, forum),
            )

            # Run the command with the --apply argument, to execute real database updates
            call_command("sync_group_permissions", "--apply")

            # Check that missing groups have been added to our instructor group, according to
            # the ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS setting
            self.assertEqual(
                ["can_see_forum", "can_read_forum", "can_lock_topics"],
                self._get_group_forum_permissions(instructor_group, forum),
            )
            # another_group should have its initial permissions, since it's
            # not mentionned in the ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS setting.
            self.assertEqual(
                ["can_see_forum", "can_read_forum", "can_approve_posts"],
                self._get_group_forum_permissions(another_group, forum),
            )

            # Run the command with the --remove-extra-permissions to revoke group
            # permissions that are not defined in the settings
            call_command(
                "sync_group_permissions", "--apply", "--remove-extra-permissions"
            )

            # Check that extra groups have been revoked from instructor group, according to
            # the ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS setting
            self.assertEqual(
                ["can_see_forum", "can_lock_topics"],
                self._get_group_forum_permissions(instructor_group, forum),
            )
            # another_group should have its initial permissions, since it's
            # not mentionned in the ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS setting.
            self.assertEqual(
                ["can_see_forum", "can_read_forum", "can_approve_posts"],
                self._get_group_forum_permissions(another_group, forum),
            )

    @staticmethod
    def _get_group_forum_permissions(group, forum):
        return list(
            GroupForumPermission.objects.filter(
                forum=forum, group=group, has_perm=True
            ).values_list("permission__codename", flat=True)
        )
