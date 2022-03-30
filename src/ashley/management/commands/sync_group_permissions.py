"""
This module provides a management command `sync_group_permissions`
to help ashley operators maintaining a consistent set of forum permission
across all LTI related groups.
"""

from django.core.management.base import BaseCommand
from machina.apps.forum_permission.shortcuts import assign_perm, remove_perm
from machina.core.db.models import get_model

from ashley.defaults import DEFAULT_FORUM_ROLES_PERMISSIONS

Forum = get_model("forum", "Forum")  # pylint: disable=C0103
GroupForumPermission = get_model(
    "forum_permission", "GroupForumPermission"
)  # pylint: disable=C0103
LTIContext = get_model("ashley", "LTIContext")  # pylint: disable=C0103


class Command(BaseCommand):
    """
    Implementation of the sync_group_permission Command.
    """

    help = (
        "Update group permissions in database with permissions defined "
        "in ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS. By default, only missing "
        "permissions are added and no permission is removed."
    )
    apply_updates = False
    remove_extra_permissions = False

    def add_arguments(self, parser):
        """Set custom arguments for this command."""

        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the update in database (by default, the command runs in dry mode)",
        )
        parser.add_argument(
            "--remove-extra-permissions",
            action="store_true",
            help="Revoke group permissions that are not defined in the settings",
        )

    def handle(self, *args, **options):
        """Command handler, that execute the actual logic of the command."""

        self.apply_updates = bool(options["apply"])
        self.remove_extra_permissions = bool(options["remove_extra_permissions"])

        self.stdout.write("Synchronizing group permissions")
        if not self.apply_updates:
            self.stdout.write("(DRY RUN)")

        for forum in Forum.objects.iterator():
            self.sync_forum_permissions(forum)

        self.stdout.write("Done.")

    def sync_forum_permissions(self, forum):
        """Synchronize permissions for every LTI role group related to a forum."""

        # Exclude lti_context that have locked the course
        for lti_context in forum.lti_contexts.iterator():
            # pylint: disable=no-member
            for role, permissions in DEFAULT_FORUM_ROLES_PERMISSIONS.items():
                role_group = lti_context.get_role_group(role)
                self.sync_forum_group_permissions(forum, role_group, permissions)

    def sync_forum_group_permissions(self, forum, group, expected_permissions):
        """Set permissions for a group in a specific forum"""
        current_permissions = GroupForumPermission.objects.filter(
            forum=forum, group=group, has_perm=True
        ).values_list("permission__codename", flat=True)

        # Add missing permissions
        for permission in expected_permissions:
            if permission not in current_permissions:
                self.grant_permission(permission, group, forum)
        # Remove extra permissions
        if self.remove_extra_permissions:
            for permission in current_permissions:
                if permission not in expected_permissions:
                    self.revoke_permission(permission, group, forum)

    def grant_permission(self, permission, group, forum):
        """Grant a permission to a group in the specified forum."""
        if self.apply_updates:
            assign_perm(permission, group, forum, True)
        self.stdout.write(
            f"ADDED {permission} for group {group.name} in forum {forum.pk} ({forum.slug})"
        )

    def revoke_permission(self, permission, group, forum):
        """Revoke a permission from a group in the specified forum."""
        if self.apply_updates:
            remove_perm(permission, group, forum)
        self.stdout.write(
            f"REMOVED {permission} for group {group.name} in forum {forum.pk} ({forum.slug})"
        )
