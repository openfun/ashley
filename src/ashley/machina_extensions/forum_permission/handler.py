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

        if user.is_superuser:
            readable_forums = forums.filter(archived=False)
        else:
            # Fetches the forums that can be read by the given user.
            readable_forums = self._get_forums_for_user_with_lti_forums(
                forums,
                user,
                [
                    "can_read_forum",
                ],
                True,
            )
            readable_forums = (
                forums.filter(id__in=[f.id for f in readable_forums])
                if isinstance(forums, (models.Manager, models.QuerySet))
                else list(filter(lambda f: f in readable_forums, forums))
            )

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

        return readable_forums

    def _get_forums_for_user(self, user, perm_codenames, use_tree_hierarchy=False):
        """Returns all the forums that satisfy the given list of permission codenames.

        User and group forum permissions are used.

        If the ``use_tree_hierarchy`` keyword argument is set the granted forums will be filtered
        so that a forum which has an ancestor which is not in the granted forums set will not be
        returned.

        We override django machina's method to filter forums based on the
        current LTI context of the User, if any and to automatically exclude archived forums.

        """
        forums = Forum.objects.filter(archived=False)
        if self.current_lti_context_id:
            forums = forums.filter(lti_contexts__id=self.current_lti_context_id)
        return self._get_forums_for_user_with_lti_forums(
            forums, user, perm_codenames, use_tree_hierarchy
        )

    def _get_forums_for_user_with_lti_forums(
        self, filtered_forums, user, perm_codenames, use_tree_hierarchy=False
    ):
        """Returns for the list of forum based on filtered_forums that satisfy the given
        list of permission codenames.

        User and group forum permissions are used.

        If the ``use_tree_hierarchy`` keyword argument is set the granted forums will be filtered
        so that a forum which has an ancestor which is not in the granted forums set will not be
        returned.

        """
        granted_forums_cache_key = "{}__{}".format(
            ":".join(perm_codenames),
            user.id if not user.is_anonymous else "anonymous",
        )

        if granted_forums_cache_key in self._granted_forums_cache:
            return self._granted_forums_cache[granted_forums_cache_key]

        # First check if the user is a superuser and if so, returns the forum queryset immediately.
        if user.is_superuser:  # pragma: no cover
            self._granted_forums_cache[granted_forums_cache_key] = filtered_forums
            return filtered_forums

        checker = self._get_checker(user)
        perms = checker.get_perms_for_forumlist(filtered_forums, perm_codenames)
        allowed_forums = []
        # Check if the requested permissions are in the set of permissions for the forum
        for _f in filtered_forums:
            if set(perm_codenames).issubset(perms[_f]):
                allowed_forums.append(_f)

        if use_tree_hierarchy:
            allowed_forums = self._filter_granted_forums_using_tree(allowed_forums)

        self._granted_forums_cache[granted_forums_cache_key] = allowed_forums
        return allowed_forums

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
