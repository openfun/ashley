"""This module contains default settings for Ashley application."""

from django.conf import settings

_FORUM_BASE_PERMISSIONS = [
    "can_see_forum",
    "can_read_forum",
    "can_start_new_topics",
    "can_reply_to_topics",
    "can_edit_own_posts",
    "can_post_without_approval",
    "can_vote_in_polls",
]

_FORUM_ADMIN_PERMISSIONS = _FORUM_BASE_PERMISSIONS + [
    "can_post_announcements",
    "can_post_stickies",
    "can_delete_own_posts",
    "can_create_polls",
    "can_lock_topics",
    "can_edit_posts",
    "can_delete_posts",
    "can_approve_posts",
    "can_reply_to_locked_topics",
]

DEFAULT_FORUM_BASE_PERMISSIONS = getattr(
    settings, "ASHLEY_DEFAULT_FORUM_BASE_PERMISSIONS", _FORUM_BASE_PERMISSIONS
)

DEFAULT_FORUM_ROLES_PERMISSIONS = getattr(
    settings,
    "ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS",
    {
        "administrator": _FORUM_ADMIN_PERMISSIONS,
        "instructor": _FORUM_ADMIN_PERMISSIONS,
    },
)
