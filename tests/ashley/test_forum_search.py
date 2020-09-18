"""
Tests for the forum_search feature.
"""
import logging
from datetime import datetime
from unittest import mock

import haystack
from configurations import values
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley.factories import PostFactory, UserFactory

logging.disable(logging.CRITICAL)

Forum = get_model("forum", "Forum")

TEST_INDEX = {
    "default": {
        "ENGINE": "haystack.backends.elasticsearch5_backend.Elasticsearch5SearchEngine",
        "URL": "{:s}:{:s}".format(
            values.Value(
                "elasticsearch",
                environ_name="ELASTICSEARCH_HOST",
                environ_prefix=None,
            ),
            values.Value(
                "9200", environ_name="ELASTICSEARCH_PORT", environ_prefix=None
            ),
        ),
        "INDEX_NAME": "test_ashley",
    },
}


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class ForumSearchTestCase(TestCase):
    """Test the post search feature of a forum"""

    def test_forum_search_authorized(self):
        """A user with the rights to read a forum should be able to search."""
        created_on = datetime(2020, 10, 5, 8, 13, tzinfo=timezone.utc)
        with mock.patch.object(timezone, "now", return_value=created_on):
            post = PostFactory(text="Who is Ashley!")

        poster = post.poster
        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=*")

        # Check the format of the results
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post.subject)
        self.assertContains(response, "Who is Ashley!")
        self.assertContains(
            response,
            f'By: <a href="/forum/member/profile/{poster.id:d}/">{poster.public_username:s}</a>',
        )
        self.assertContains(
            response,
            "on Oct. 5, 2020, 8:13 a.m.",
        )

    def test_forum_search_unauthorized(self):
        """A user missing the rights to read a forum should not get any results."""
        PostFactory()
        user = UserFactory()

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=*")
        self.assertContains(
            response, "Your search has returned <b>0</b> results", html=True
        )

    def test_forum_search_anonymous(self):
        """Anonymous users should not get any results."""
        PostFactory()

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        response = self.client.get("/forum/search/?q=*")
        self.assertContains(
            response, "Your search has returned <b>0</b> results", html=True
        )

    def test_forum_search_post_content_partial(self):
        """Searching for part of a word contained in the post content should find it."""
        post = PostFactory(text="a5g3g6k75")

        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=a5g3")
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post, html=True)

    def test_forum_search_post_subject_partial(self):
        """Searching for part of a word contained in the post subject should find it."""
        post = PostFactory(subject="f61f59ky2")

        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=f61f")
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post.subject, html=True)

    def test_forum_search_post_poster_partial(self):
        """Searching for part of the poster public username should find the post."""
        post = PostFactory(poster__public_username="3vj9tq3gc")
        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=&search_poster_name=3vj9t")
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post.subject)

    def test_forum_search_post_topic_partial(self):
        """Searching for part of a word contained in the post topic should find it."""
        post1 = PostFactory(subject="497jk1sav")
        post2 = PostFactory(topic=post1.topic)

        # A third post in the same forum with a different topic
        PostFactory(subject="7bh86k", topic__forum=post1.topic.forum)

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=497jk")

        self.assertContains(
            response, "Your search has returned <b>2</b> results", html=True
        )
        self.assertContains(response, post1.subject)
        self.assertContains(response, post2.subject)

    def test_forum_search_post_failure(self):
        """Searching for a word not present in post, topic or username should return no result."""
        post = PostFactory(text="a5g3g6k75", subject="497jk1sav")
        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=blabla")

        self.assertContains(
            response, "Your search has returned <b>0</b> results", html=True
        )

    def test_forum_search_only_topics(self):
        """
        If the "search only topics" checkbox is ticked, matching content elsewhere should not
        return any result.
        """
        post = PostFactory(subject="a5g3g6k75")
        PostFactory(subject="x56d4z7", text="a5g3g6k75")

        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=a5g3&search_topics=on")

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )

    def test_forum_search_several_forums_cross_search(self):
        """By default, forum searches span several forums."""
        post1 = PostFactory(text="Hello world", subject="a5g3g6k75")
        post2 = PostFactory(text="Good morning world", subject="497jk1sav")

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)
        assign_perm("can_read_forum", user, post2.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=world")

        self.assertContains(
            response, "Your search has returned <b>2</b> results", html=True
        )
        self.assertContains(response, post1.subject)
        self.assertContains(response, post2.subject)

        # Search for the first post
        response = self.client.get("/forum/search/?q=hello")

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post1.subject)

        # Search for the second post
        response = self.client.get("/forum/search/?q=morning")

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post2.subject)

    def test_forum_search_several_forums_restrict_to_one(self):
        """Forum searches can be restricted to only one forum."""
        post1 = PostFactory(text="Hello world", subject="a5g3g6k75")
        post2 = PostFactory(text="Good morning world", subject="497jk1sav")

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)
        assign_perm("can_read_forum", user, post2.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get(
            f"/forum/search/?q=world&search_forums={post1.topic.forum.pk}"
        )

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post1.subject)

        response = self.client.get(
            f"/forum/search/?q=world&search_forums={post2.topic.forum.pk}"
        )
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post2.subject)

    def test_forum_search_post_poster_restrict_forums(self):
        """Forum searches can be restricted to only one forum
        when searching for a specific poster."""
        post1 = PostFactory()
        post2 = PostFactory(poster=post1.poster, topic__forum=post1.topic.forum)
        post3 = PostFactory(poster=post1.poster)

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)
        assign_perm("can_read_forum", user, post3.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get(
            f"/forum/search/?q=&search_poster_name={post1.poster.public_username}\
            &search_forums={post1.topic.forum.pk}"
        )

        self.assertContains(
            response, "Your search has returned <b>2</b> results", html=True
        )
        self.assertContains(response, post1.subject)
        self.assertContains(response, post2.subject)

        response = self.client.get(
            f"/forum/search/?q=&search_poster_name={post1.poster.public_username}\
                &search_forums={post3.topic.forum.pk}"
        )
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post3.subject)

    def test_forum_search_restrict_poster_name(self):
        """Forum searches can be restricted poster"""
        post1 = PostFactory(subject="x45g87")
        PostFactory(subject="x45g87", topic__forum=post1.topic.forum)

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get(
            f"/forum/search/?q=x45g87&search_poster_name={post1.poster.public_username}"
        )

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post1.poster.public_username)

    def test_forum_search_restrict_poster_topic_forums(self):
        """Forum searches can be restricted to forums, topic names, and posters"""
        post1 = PostFactory(poster__username="4t4f5g8t", subject="a1b2c3")

        # Different subject
        PostFactory(
            poster=post1.poster, topic__forum=post1.topic.forum, subject="d4e5f6"
        )

        # Different forum
        post3 = PostFactory(poster=post1.poster, subject="a1b2c3")

        # Different poster
        PostFactory(topic__forum=post1.topic.forum, subject="a1b2c3")

        # Same poster, same forum, similar topic name
        post5 = PostFactory(
            poster=post1.poster, topic__forum=post1.topic.forum, subject="a1b2d4"
        )

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)
        assign_perm("can_read_forum", user, post3.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False, verbosity=3)

        self.client.force_login(user)
        response = self.client.get(
            f"/forum/search/?q=a1b2&search_topics=on\
                &search_poster_name={post1.poster.public_username}\
                &search_forums={post1.topic.forum.pk}"
        )

        self.assertContains(
            response, "Your search has returned <b>2</b> results", html=True
        )
        self.assertContains(response, post1.topic.slug)
        self.assertContains(response, post5.topic.slug)

    def tearDown(self):
        haystack.connections["default"].get_backend().clear()
