"""Declare the models related to the forum_conversation app ."""
from django.contrib.auth import get_user_model
from django.db import models  # pylint: disable=all
from django.utils.translation import gettext_lazy as _
from machina.apps.forum_conversation.abstract_models import (
    AbstractTopic as MachinaAbstractTopic,
)
from machina.core.db.models import model_factory
from machina.core.loading import get_class

get_forum_member_display_name = get_class(
    "forum_member.shortcuts", "get_forum_member_display_name"
)
User = get_user_model()


class AbstractTopic(MachinaAbstractTopic):
    # The number of posts included in this topic (only those that are approved).
    # Add Index for sorting
    posts_count = models.PositiveIntegerField(
        editable=False,
        blank=True,
        default=0,
        verbose_name=_("Posts count"),
        db_index=True,
    )

    # The number of time the topic has been viewed.
    # Add Index for sorting
    views_count = models.PositiveIntegerField(
        editable=False,
        blank=True,
        default=0,
        verbose_name=_("Views count"),
        db_index=True,
    )

    class Meta(MachinaAbstractTopic.Meta):
        abstract = True

    def get_active_users(self, user):
        # collect active users for this topic and exclude current user
        active_post_users = (
            User.objects.filter(is_active=True, posts__topic=self, posts__approved=True)
            .exclude(pk=user.pk)
            .distinct()
        )

        list_active_users = [
            {
                "name": get_forum_member_display_name(user),
                "user": user.pk,
            }
            for user in active_post_users
        ]

        return sorted(list_active_users, key=lambda i: i["name"])


Topic = model_factory(AbstractTopic)

from machina.apps.forum_conversation.models import *  # noqa
