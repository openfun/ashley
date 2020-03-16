"""
This package contains features related to permission management in Ashley.
"""

DEFAULT_GROUP_FORUM_PERMISSIONS = [
    "can_see_forum",
    "can_read_forum",
    "can_start_new_topics",
    "can_reply_to_topics",
    "can_edit_own_posts",
    "can_post_without_approval",
    "can_vote_in_polls",
]

DEFAULT_ADMIN_GROUP_FORUM_PERMISSIONS = DEFAULT_GROUP_FORUM_PERMISSIONS + [
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

DEFAULT_INSTRUCTOR_GROUP_FORUM_PERMISSIONS = DEFAULT_ADMIN_GROUP_FORUM_PERMISSIONS
