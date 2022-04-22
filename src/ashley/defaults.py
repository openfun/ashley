"""This module contains default settings for Ashley application."""

from django.conf import settings
from django.utils.functional import lazy
from draftjs_exporter.defaults import BLOCK_MAP as DEFAULT_BLOCK_MAP
from draftjs_exporter.defaults import STYLE_MAP as DEFAULT_STYLE_MAP
from draftjs_exporter.dom import DOM

from ashley.editor.decorators import emoji, image, link, mention

_FORUM_ROLE_ADMINISTRATOR = "administrator"
_FORUM_ROLE_INSTRUCTOR = "instructor"
_FORUM_ROLE_MODERATOR = "moderator"
_FORUM_ROLE_STUDENT = "student"

_FORUM_BASE_READ_PERMISSIONS = [
    "can_see_forum",
    "can_read_forum",
]

_FORUM_BASE_WRITE_PERMISSIONS = [
    "can_start_new_topics",
    "can_reply_to_topics",
    "can_edit_own_posts",
    "can_post_without_approval",
    "can_vote_in_polls",
]


_FORUM_BASE_PERMISSIONS = _FORUM_BASE_READ_PERMISSIONS + _FORUM_BASE_WRITE_PERMISSIONS

_FORUM_MODERATOR_PERMISSIONS = _FORUM_BASE_PERMISSIONS + [
    "can_approve_posts",
    "can_create_polls",
    "can_delete_own_posts",
    "can_delete_posts",
    "can_edit_posts",
    "can_lock_topics",
    "can_move_topics",
    "can_post_announcements",
    "can_post_stickies",
    "can_reply_to_locked_topics",
]

_FORUM_ADMIN_PERMISSIONS = _FORUM_MODERATOR_PERMISSIONS + [
    "can_archive_forum",
    "can_lock_course",
    "can_manage_moderator",
    "can_rename_forum",
]

DEFAULT_FORUM_BASE_READ_PERMISSIONS = lazy(
    lambda: getattr(
        settings,
        "ASHLEY_DEFAULT_FORUM_READ_PERMISSIONS",
        _FORUM_BASE_READ_PERMISSIONS,
    ),
    list,
)()

DEFAULT_FORUM_BASE_WRITE_PERMISSIONS = lazy(
    lambda: getattr(
        settings,
        "ASHLEY_DEFAULT_FORUM_WRITE_PERMISSIONS",
        _FORUM_BASE_WRITE_PERMISSIONS,
    ),
    list,
)()


DEFAULT_FORUM_BASE_PERMISSIONS = lazy(
    lambda: getattr(
        settings, "ASHLEY_DEFAULT_FORUM_BASE_PERMISSIONS", _FORUM_BASE_PERMISSIONS
    ),
    list,
)()

DEFAULT_FORUM_ROLES_PERMISSIONS = lazy(
    lambda: getattr(
        settings,
        "ASHLEY_DEFAULT_FORUM_ROLES_PERMISSIONS",
        {
            _FORUM_ROLE_ADMINISTRATOR: _FORUM_ADMIN_PERMISSIONS,
            _FORUM_ROLE_INSTRUCTOR: _FORUM_ADMIN_PERMISSIONS,
            _FORUM_ROLE_MODERATOR: _FORUM_MODERATOR_PERMISSIONS,
        },
    ),
    dict,
)()

DEFAULT_DRAFTJS_EXPORTER_CONFIG = {
    "entity_decorators": {
        "LINK": link,
        "emoji": emoji,
        "mention": mention,
        "IMAGE": image,
    },
    "composite_decorators": [],
    "block_map": DEFAULT_BLOCK_MAP,
    "style_map": DEFAULT_STYLE_MAP,
    "engine": DOM.STRING,
}

DRAFTJS_EXPORTER_CONFIG = lazy(
    lambda: {
        **DEFAULT_DRAFTJS_EXPORTER_CONFIG,
        **getattr(settings, "ASHLEY_DRAFTJS_EXPORTER_CONFIG", {}),
    },
    dict,
)()


INDEXABLE_USER_DISPLAY_NAME_METHOD = getattr(
    settings, "ASHLEY_INDEXABLE_USER_DISPLAY_NAME_METHOD", "get_public_username"
)
