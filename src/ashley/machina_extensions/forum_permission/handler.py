"""
This module defines a ``PermissionHandler`` abstraction that allows to
implement filter or access logic related to forums.
"""
from typing import Optional

from django.db import models
from machina.apps.forum_permission.handler import (
    PermissionHandler as BasePermissionHandler,
)
from machina.core.db.models import get_model

Forum = get_model("forum", "Forum")

# pylint: disable = consider-using-f-string


class PermissionHandler(BasePermissionHandler):
    """Add ashley specific permission checks to the machina permission handler."""

    def __init__(self):
        """Constructor"""
        super().__init__()
        # This attribute is used to store the LTIContext of the current user.
        # (see middleware.ForumPermission)
        # It allows the permission checking functions to be aware of the current LTIContext
        # we are scoped into, if any.
        self.current_lti_context_id: Optional[int] = None

    def can_archive_forum(self, forum, user):
        """Given a forum, checks whether the user can archive it."""
        return self._perform_basic_permission_check(forum, user, "can_archive_forum")

    def can_lock_course(self, forum, user):
        """Given a forum, checks whether the user can lock it."""
        return self._perform_basic_permission_check(forum, user, "can_lock_course")

    def can_rename_forum(self, forum, user):
        """Given a forum, checks whether the user can rename it."""
        return self._perform_basic_permission_check(forum, user, "can_rename_forum")

    def can_manage_moderator(self, forum, user):
        """
        Given a forum, checks whether the user can promote or revoke a user to moderator.
        """
        return self._perform_basic_permission_check(forum, user, "can_manage_moderator")

    def forum_list_filter(self, qs, user):
        """
        Filters the given queryset in order to return a list of forums that
        can be seen and read by the specified user (at least).

        We override django machina's method to filter forums based on the
        current LTI context of the User, if any.
        """
        forums_to_show = super().forum_list_filter(qs, user)
        if self.current_lti_context_id:
            return forums_to_show.filter(
                archived=False, lti_contexts__id=self.current_lti_context_id
            )

        return forums_to_show

    def get_readable_forums(self, forums, user):
        """
        Given a QuerySet (or list) of forums, it returns the subset of
        forums that can be read by the considered user, with the same type.

        We override django machina's method to filter forums based on the
        current LTI context of the User, if any.

        """

        readable_forums = super().get_readable_forums(forums, user)
        if self.current_lti_context_id:
            if isinstance(readable_forums, (models.Manager, models.QuerySet)):
                return readable_forums.filter(
                    archived=False, lti_contexts__id=self.current_lti_context_id
                )
            return list(
                filter(
                    lambda f: any(
                        x
                        for x in f.lti_contexts.all()
                        if x.id == self.current_lti_context_id and not f.archived
                    ),
                    readable_forums,
                )
            )

        if isinstance(readable_forums, (models.Manager, models.QuerySet)):
            return readable_forums.filter(archived=False)

        return list(filter(lambda f: f.archived is False, readable_forums))

    # pylint:disable = W0201
    def _get_all_forums(self):
        """Return all forums accessible for the LTIContext of the user."""
        if not hasattr(self, "_all_forums"):
            if self.current_lti_context_id:
                self._all_forums = list(
                    Forum.objects.filter(
                        archived=False, lti_contexts__id=self.current_lti_context_id
                    )
                )
            else:
                super()._get_all_forums()

        return self._all_forums
