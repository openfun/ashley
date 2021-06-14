"""
Tests for the forum_search feature.
"""
from datetime import datetime
from unittest import mock

import haystack
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import (
    ForumFactory,
    LTIContextFactory,
    PostFactory,
    TopicFactory,
    UserFactory,
)
from ashley.machina_extensions.forum_search.forms import SearchForm

Forum = get_model("forum", "Forum")

# Change index name so we don't mess up the site index for development
TEST_INDEX = settings.HAYSTACK_CONNECTIONS.copy()
TEST_INDEX["INDEX_NAME"] = "test_ashley"


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class ForumSearchTestCase(TestCase):
    """Test the post search feature of a forum"""

    def test_forum_search_authorized(self):
        """A user with the rights to read a forum should be able to search."""
        created_on = datetime(2020, 10, 5, 8, 13, tzinfo=timezone.utc)
        with mock.patch.object(timezone, "now", return_value=created_on):
            post = PostFactory()

        poster = post.poster
        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=*")

        # Check the format of the results
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post.subject)
        self.assertContains(response, post.topic.subject)
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
        call_command("rebuild_index", interactive=False)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=*")
        self.assertContains(
            response, "Your search has returned <b>0</b> results", html=True
        )

    def test_forum_search_anonymous(self):
        """Anonymous users should not get any results."""
        PostFactory()

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

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
        call_command("rebuild_index", interactive=False)

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
        call_command("rebuild_index", interactive=False)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=f61f")
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post.subject, html=True)

    def test_forum_search_post_poster_partial_public_username(self):
        """Searching for part of the poster public username should find the post."""
        post = PostFactory(poster__public_username="3vj9tq3gc")
        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=&search_poster_name=3vj9t")
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post.subject)

    def test_forum_search_post_topic_partial(self):
        """
        The topic subject is not directly indexed but Django Machina forces it with the post
        subject when creating the first post of a topic:
        # see: apps/forum_conversation/abstract_models.py#L314

        So in the end, searching for a topic subject will return the first post as result.
        """
        # First, let's secure Django Machina's overriding mechanism
        topic = TopicFactory(subject="5f3gh8ka1")
        forum = topic.forum
        self.assertEqual(topic.subject, "5f3gh8ka1")

        # When we create the first post for this topic...
        PostFactory(subject="497jk1sav", topic=topic)
        # The topic subject should be overriden
        topic.refresh_from_db()
        self.assertEqual(topic.subject, "497jk1sav")

        PostFactory(topic=topic)
        # Creating a second post does not change the topic subject again
        topic.refresh_from_db()
        self.assertEqual(topic.subject, "497jk1sav")

        # A third post in the same forum with a different topic
        PostFactory(topic__forum=forum)

        user = UserFactory()
        assign_perm("can_read_forum", user, forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

        self.client.force_login(user)
        response = self.client.get("/forum/search/?q=497jk1sav")

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(
            response,
            (
                f'<a href="/forum/forum/{forum.slug:s}-{forum.id:d}/topic/{topic.slug:s}-'
                f'{topic.id:d}/" class="topic-name-link">{topic.subject:s}</a>'
            ),
            html=True,
        )

    def test_forum_search_post_failure(self):
        """Searching for a word not present in post, topic or username should return no result."""
        post = PostFactory(text="a5g3g6k75", subject="497jk1sav")
        user = UserFactory()
        assign_perm("can_read_forum", user, post.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

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
        post1 = PostFactory(subject="497jk1sav", text="497jk1sav")
        forum = post1.topic.forum
        post2 = PostFactory(topic__subject="497jk1sav", topic__forum=forum)

        user = UserFactory()
        assign_perm("can_read_forum", user, forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

        self.client.force_login(user)

        # Searching without the "search_topics" flag returns post1 because it contains
        # the search string in its text body.
        response = self.client.get("/forum/search/?q=497jk")

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post1.topic.slug)

        # Searching with the "search_topics" flag returns post2 because it contains
        # the search string in the related topic subject.
        response = self.client.get("/forum/search/?q=497jk&search_topics=on")

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertContains(response, post2.topic.slug)

    def test_forum_search_several_forums_cross_search(self):
        """By default, forum searches span several forums."""
        post1 = PostFactory(text="Hello world", subject="a5g3g6k75")
        post2 = PostFactory(text="Good morning world", subject="497jk1sav")

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)
        assign_perm("can_read_forum", user, post2.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

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
        call_command("rebuild_index", interactive=False)

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
        """
        Forum searches can be restricted to only one forum
        when searching for a specific poster.
        """
        post1 = PostFactory()
        post2 = PostFactory(poster=post1.poster, topic__forum=post1.topic.forum)
        post3 = PostFactory(poster=post1.poster)

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)
        assign_perm("can_read_forum", user, post3.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

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
        """Forum searches can be restricted to a poster"""
        # Make sure public user names on post1 and post2 are orthogonal
        post1 = PostFactory(subject="x45g87", poster__public_username="123")
        forum = post1.topic.forum
        PostFactory(subject="x45g87", topic__forum=forum, poster__public_username="abc")

        user = UserFactory()
        assign_perm("can_read_forum", user, forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

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
        post1 = PostFactory(poster__public_username="4t4f5g8t", subject="a1b2c3")

        # Same forum, different subject, same poster
        PostFactory(
            poster=post1.poster, topic__forum=post1.topic.forum, subject="d4e5f6"
        )

        # Different forum, same subject, same poster
        post3 = PostFactory(poster=post1.poster, subject="a1b2c3")

        # Same forum, same subject, different poster
        PostFactory(topic__forum=post1.topic.forum, subject="a1b2c3")

        # Same forum, subject starts similarly, same poster
        post5 = PostFactory(
            poster=post1.poster, topic__forum=post1.topic.forum, subject="a1b2d4"
        )

        user = UserFactory()
        assign_perm("can_read_forum", user, post1.topic.forum)
        assign_perm("can_read_forum", user, post3.topic.forum)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

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

    def test_forum_search_empty_public_username(self):
        """
        A topic posted by a user that has not defined a public_username
        should be indexed with no error.
        """

        user = UserFactory(public_username="")
        forum = ForumFactory()

        # Create a topic and a post
        topic = TopicFactory(subject="yahl2vooPh", poster=user, forum=forum)
        post = PostFactory(subject="dooV7ei3ju", topic=topic, poster=user)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

        user2 = UserFactory()
        assign_perm("can_read_forum", user2, post.topic.forum)
        self.client.force_login(user2)
        response = self.client.get(
            f"/forum/search/?q=dooV7ei3ju&search_poster_name={post.poster.get_public_username()}\
                    &search_forums={post.topic.forum.pk}"
        )

        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )

        # Ensure that the default display name is present
        user_profile_url = reverse("forum_member:profile", kwargs={"pk": user.id})
        self.assertContains(
            response, f'<a href="{user_profile_url}">Anonymous</a>', html=True
        )

        # Ensure that the default display name is not indexed
        response = self.client.get(
            f"/forum/search/?q=dooV7ei3ju&search_poster_name={post.poster.get_public_username()}\
                            &search_forums={post.topic.forum.pk}&search_poster_name=Anonymous"
        )
        self.assertContains(
            response, "Your search has returned <b>0</b> results", html=True
        )

    def tearDown(self):
        haystack.connections["default"].get_backend().clear()

    def test_forum_search_several_forums_lti_context_search(self):
        """
        Creates forum in different lti_context, make sure user can't
        search into it, even if he has access to this forum.
        """
        user = UserFactory()

        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context2 = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum2 = ForumFactory()
        forum3 = ForumFactory()
        forum.lti_contexts.add(lti_context)
        forum2.lti_contexts.add(lti_context)
        forum3.lti_contexts.add(lti_context2)

        post1 = PostFactory(
            topic=TopicFactory(forum=forum),
            subject="Forum same lti_context",
            text="Hello world",
        )

        post2 = PostFactory(
            topic=TopicFactory(forum=forum2),
            subject="Forum2 same lti_context",
            text="Good morning world",
        )
        post3 = PostFactory(
            topic=TopicFactory(forum=forum3),
            subject="Forum3 different lti_context",
            text="Welcome world",
        )
        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        assign_perm("can_read_forum", user, forum)
        assign_perm("can_read_forum", user, forum2)
        assign_perm("can_read_forum", user, forum3)

        # Index the post in Elasticsearch
        call_command("rebuild_index", interactive=False)

        response = self.client.get("/forum/search/?q=world")

        self.assertContains(
            response, "Your search has returned <b>2</b> results", html=True
        )
        self.assertContains(response, post1.subject)
        self.assertContains(response, post2.subject)
        self.assertNotContains(response, post3.subject)

        # Change the session to connect user to lti_context2
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context2.id
        session.save()

        response = self.client.get("/forum/search/?q=world")
        # We should only have one result
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
        self.assertNotContains(response, post1.subject)
        self.assertNotContains(response, post2.subject)
        self.assertContains(response, post3.subject)

    def test_forum_search_with_unautorized_forum_from_other_lti_context(self):
        """
        Try to search in a forum that is not part of our LTIContext by submitting
        in the search form a forum from another LTIContext.
        """
        user = UserFactory()

        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context2 = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum2 = ForumFactory()
        forum.lti_contexts.add(lti_context)
        forum2.lti_contexts.add(lti_context2)

        PostFactory(
            topic=TopicFactory(forum=forum),
            text="Good morning world",
        )

        PostFactory(
            topic=TopicFactory(forum=forum2),
            text="Hello world",
        )
        # Index posts in Elasticsearch
        call_command("rebuild_index", interactive=False)

        # Connects and gets acces to the forum
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        assign_perm("can_read_forum", user, forum)
        assign_perm("can_read_forum", user, forum2)
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        form = SearchForm(user=user, lti_context=lti_context)

        # Checks that only the forum that is allowed is proposed as choice
        self.assertEqual(
            form.fields["search_forums"].choices,
            [(forum.id, "{} {}".format("-" * forum.margin_level, forum.name))],
        )
        # Despite that, we force the request on the forum that is not allowed
        response = self.client.get(f"/forum/search/?q=world&search_forums={forum2.id}")
        self.assertEqual(response.status_code, 200)
        # Controls that we get an error and the search is not executed
        self.assertContains(
            response,
            f"Select a valid choice. {forum2.id} is not one of the available choices.",
            html=True,
        )

        # Valid request, we search on the forum that is allowed, we get only one result
        # as forum2 is ignored
        response = self.client.get(f"/forum/search/?q=world&search_forums={forum.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Your search has returned <b>1</b> result", html=True
        )
