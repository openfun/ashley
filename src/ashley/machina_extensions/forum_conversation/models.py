"""Declare the models related to the forum_conversation app ."""

from django.db import models  # pylint: disable=all
from django.utils.translation import gettext_lazy as _
from machina.apps.forum_conversation.abstract_models import AbstractTopic


class Topic(AbstractTopic):
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

    class Meta(AbstractTopic.Meta):
        abstract = True


from machina.apps.forum_conversation.models import *  # noqa
