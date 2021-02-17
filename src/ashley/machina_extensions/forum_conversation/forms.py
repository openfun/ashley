"""
    Forum conversation forms
    ========================

    This module defines forms provided by the ``forum_conversation`` application.

"""
import logging

from django.contrib.auth import get_user_model
from machina.apps.forum_conversation.forms import PostForm as MachinaPostForm
from machina.core.loading import get_class

get_forum_member_display_name = get_class(
    "forum_member.shortcuts", "get_forum_member_display_name"
)
User = get_user_model()
logger = logging.getLogger(__name__)


class PostForm(MachinaPostForm):
    """ Overload Machina PostForm to send extra variables to the widget editor """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # collect active users for this topic
        active_post_users = (
            User.objects.filter(
                is_active=True, posts__topic=self.topic, posts__approved=True
            )
            .exclude(pk=self.user.pk)
            .distinct()
        )

        list_active_users = [
            {
                "name": get_forum_member_display_name(user),
                "user": user.pk,
            }
            for user in active_post_users
        ]
        self.fields["content"].widget.attrs["mention_users"] = sorted(
            list_active_users, key=lambda i: i["name"]
        )

        logger.debug(
            "List active users %s", self.fields["content"].widget.attrs["mention_users"]
        )
