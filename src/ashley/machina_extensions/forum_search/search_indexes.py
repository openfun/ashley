"""
    Forum search indexes
    ====================
    This module defines search indexes allowing to perform searches among forum topics and posts.
"""

from haystack import indexes
from machina.core.db.models import get_model

from ashley import defaults

Post = get_model("forum_conversation", "Post")


def get_indexable_forum_member_display_name(user):
    """Given a specific user, returns their related display name."""
    return getattr(user, defaults.INDEXABLE_USER_DISPLAY_NAME_METHOD)()


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Defines the data stored in the Post indexes.

    Derives from Django Machina's PostIndex to define "forum_name" and "topic_name" as Edge Ngrams
    """

    text = indexes.EdgeNgramField(
        document=True,
        use_template=True,
        template_name="forum_search/post_text.txt",
    )

    poster = indexes.IntegerField(model_attr="poster_id", null=True)
    poster_name = indexes.EdgeNgramField(null=True)

    forum = indexes.IntegerField(model_attr="topic__forum_id")
    forum_slug = indexes.CharField()
    forum_name = indexes.EdgeNgramField()

    topic = indexes.IntegerField(model_attr="topic_id")
    topic_slug = indexes.CharField()
    topic_subject = indexes.EdgeNgramField()

    created = indexes.DateTimeField(model_attr="created")
    updated = indexes.DateTimeField(model_attr="updated")

    def get_model(self):
        return Post

    @staticmethod
    def prepare_poster_name(obj):
        """Returns the poster's name"""
        return (
            get_indexable_forum_member_display_name(obj.poster)
            if obj.poster
            else obj.username
        )

    @staticmethod
    def prepare_forum_slug(obj):
        """Returns the forum's slug"""
        return obj.topic.forum.slug

    @staticmethod
    def prepare_forum_name(obj):
        """Returns the forum's name"""
        return obj.topic.forum.name

    @staticmethod
    def prepare_topic_slug(obj):
        """Returns the topic's slug"""
        return obj.topic.slug

    @staticmethod
    def prepare_topic_subject(obj):
        """Returns the topic's subject"""
        return obj.topic.subject

    def index_queryset(self, using=None):
        return (
            Post.objects.all()
            .exclude(approved=False)
            .exclude(topic__forum__archived=True)
        )

    def read_queryset(self, using=None):
        return (
            Post.objects.all()
            .exclude(approved=False)
            .exclude(topic__forum__archived=True)
            .select_related("topic", "poster")
        )
