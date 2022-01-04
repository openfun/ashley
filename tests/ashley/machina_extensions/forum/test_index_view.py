from django.http import HttpRequest
from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley.factories import (
    ForumFactory,
    LTIContextFactory,
    PostFactory,
    TopicFactory,
    UserFactory,
)
from ashley.machina_extensions.forum.views import OrderByColumnMixin

Topic = get_model("forum_conversation", "Topic")


class TestForumView(TestCase):
    """Displays the listing of forums overridden from django machina."""

    def _get_url_list_forum_with_forums(self):
        """Creates four forums and a user to access the forum that has
        the permission to access it. It's a shortcut used in all the tests below.
        """
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory(name="Z Letter")
        forum.lti_contexts.add(lti_context)
        # create 3 topics, and one topic with 10 posts
        topic = TopicFactory(forum=forum)
        for i in range(10):
            PostFactory(topic=topic)
        PostFactory(topic=TopicFactory(forum=forum))
        PostFactory(topic=TopicFactory(forum=forum))

        # create a forum with 2 topics
        forum2 = ForumFactory(name="A Letter")
        forum2.lti_contexts.add(lti_context)
        PostFactory(topic=TopicFactory(forum=forum2))
        PostFactory(topic=TopicFactory(forum=forum2))

        # create a forum with 1 topic and 5 messages
        forum3 = ForumFactory(name="Q Letter")
        forum3.lti_contexts.add(lti_context)
        topic3 = TopicFactory(forum=forum3)
        PostFactory(topic=topic3)
        PostFactory(topic=topic3)
        PostFactory(topic=topic3)
        PostFactory(topic=topic3)
        PostFactory(topic=topic3)
        PostFactory(topic=TopicFactory(forum=forum3))
        PostFactory(topic=TopicFactory(forum=forum3))
        PostFactory(topic=TopicFactory(forum=forum3))

        # create a forum with no topic
        forum4 = ForumFactory(name="M Letter")
        forum4.lti_contexts.add(lti_context)

        # Grant access
        assign_perm("can_see_forum", user, forum, True)
        assign_perm("can_read_forum", user, forum, True)
        assign_perm("can_see_forum", user, forum2, True)
        assign_perm("can_read_forum", user, forum2, True)
        assign_perm("can_see_forum", user, forum3, True)
        assign_perm("can_read_forum", user, forum3, True)
        assign_perm("can_see_forum", user, forum4, True)
        assign_perm("can_read_forum", user, forum4, True)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")

        return forum, forum2, forum3, forum4

    def assertContentBefore(self, response, text1, text2, failing_msg=None):
        """
        Testing utility asserting that text1 appears before text2 in response
        content.
        """
        self.assertLess(
            response.content.index(text1.encode()),
            response.content.index(text2.encode()),
            (failing_msg or "")
            + "\nResponse:\n"
            + response.content.decode(response.charset),
        )

    def test_browsing_works(self):
        """Default url should return a 200."""
        self._get_url_list_forum_with_forums()
        # Run
        response = self.client.get("/forum/")
        # Check
        self.assertEqual(response.status_code, 200)

    def test_default_sorting(self):
        """By default view is sorted by last_post_on desc. Forums with no message are ignored
        in the list and are listed at the bottom.
        """
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Run
        response = self.client.get("/forum/")

        # Should have 4 sortable columns
        self.assertContains(response, "sortable ", count=4)

        # Controls last_post_on is in this order
        self.assertLess(forum.last_post_on, forum2.last_post_on, forum3.last_post_on)
        # forum4 has no message posted and is not concerned by the order
        self.assertIsNone(forum4.last_post_on)

        # Controls alphabetical order is not the same order as last_post_on order
        self.assertLess(forum2.name, forum4.name, forum3.name)

        # Should be orderedy by date by default, the oldest forum first
        self.assertContentBefore(response, forum3.name, forum2.name)
        self.assertContentBefore(response, forum2.name, forum.name)
        # forums with no last_post_on date are at the end
        self.assertContentBefore(response, forum.name, forum4.name)

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected result in html
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(response, '<a href="?o=3">Last post</a>')
        # Column is sorted by last post
        self.assertContains(
            response,
            '<a href="?o=3" class="toggle descending" title="Toggle sorting"></a>',
        )

    def test_sorting_by_subject_asc(self):
        """Test sorting by name."""
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Setup add param sorting on name, name is index 0 for column 1
        response = self.client.get("/forum/?o=0")

        # Alphabetical order is defined this way
        self.assertLess(forum2.name, forum4.name, forum3.name)
        self.assertLess(forum3.name, forum.name)

        # It should be in alphabetic order
        self.assertContentBefore(response, forum2.name, forum4.name)
        self.assertContentBefore(response, forum4.name, forum3.name)
        self.assertContentBefore(response, forum3.name, forum.name)

        # Should have 1 sorted column and it should be ascending
        self.assertContains(response, "sortable sorted descending", count=0)
        self.assertContains(response, "sortable sorted ascending", count=1)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(
            response,
            '<a href="?o=-0" class="toggle ascending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_subject_desc(self):
        """Test sorting by subject desc."""
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Setup add param sorting on name, name is index 0 for column 1
        response = self.client.get("/forum/?o=-0")

        # Alphabetical order is defined this way
        self.assertGreater(forum.name, forum3.name, forum4.name)
        self.assertGreater(forum4.name, forum2.name)

        # It should be in alphabetic order
        self.assertContentBefore(response, forum.name, forum3.name)
        self.assertContentBefore(response, forum3.name, forum4.name)
        self.assertContentBefore(response, forum4.name, forum2.name)

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=0">Forums</a>')
        self.assertContains(
            response,
            '<a href="?o=0" class="toggle descending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_topics_count_asc(self):
        """Test sorting by topic count desc."""
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Setup add param sorting on topics count index 1 for column 2
        response = self.client.get("/forum/?o=1")

        # topics_count order is defined this way
        self.assertLess(
            forum2.direct_topics_count,
            forum.direct_topics_count,
            forum3.direct_topics_count,
        )
        self.assertEqual(0, forum4.direct_topics_count)

        # It should be in direct_topics_count order
        self.assertContentBefore(response, forum4.name, forum2.name)
        self.assertContentBefore(response, forum2.name, forum.name)
        self.assertContentBefore(response, forum.name, forum3.name)

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=0)
        self.assertContains(response, "sortable sorted ascending", count=1)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(
            response,
            '<a href="?o=-1" class="toggle ascending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_topics_count_desc(self):
        """Test sorting by topic count desc."""
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Setup add param sorting on topics count index 1 for column 2
        response = self.client.get("/forum/?o=-1")

        # topics_count order is defined this way
        self.assertGreater(
            forum3.direct_topics_count,
            forum.direct_topics_count,
            forum2.direct_topics_count,
        )
        self.assertEqual(0, forum4.direct_topics_count)

        # It should be in direct_topics_count order
        self.assertContentBefore(response, forum3.name, forum.name)
        self.assertContentBefore(response, forum.name, forum2.name)
        self.assertContentBefore(response, forum2.name, forum4.name)

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(response, '<a href="?o=1">Topics</a>')
        self.assertContains(
            response,
            '<a href="?o=1" class="toggle descending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_posts_count_desc(self):
        """Test sorting by post count desc."""
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Setup add param sorting on posts count index 2 for column 3
        response = self.client.get("/forum/?o=-2")

        # topics_count order is defined this way
        self.assertGreater(
            forum.direct_posts_count,
            forum3.direct_posts_count,
            forum2.direct_posts_count,
        )
        self.assertEqual(0, forum4.direct_posts_count)

        # It should be in direct_posts_count order
        self.assertContentBefore(response, forum.name, forum3.name)
        self.assertContentBefore(response, forum3.name, forum2.name)
        self.assertContentBefore(response, forum2.name, forum4.name)

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(response, '<a href="?o=2">Posts</a>')
        self.assertContains(
            response,
            '<a href="?o=2" class="toggle descending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_posts_count_asc(self):
        """Test sorting by post count asc."""
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Setup add param sorting on posts count index 2 for column 3
        response = self.client.get("/forum/?o=2")

        # topics_count order is defined this way
        self.assertLess(
            forum2.direct_posts_count,
            forum3.direct_posts_count,
            forum.direct_posts_count,
        )
        self.assertEqual(0, forum4.direct_posts_count)

        # It should be in direct_posts_count order
        self.assertContentBefore(response, forum4.name, forum2.name)
        self.assertContentBefore(response, forum2.name, forum3.name)
        self.assertContentBefore(response, forum3.name, forum.name)

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=0)
        self.assertContains(response, "sortable sorted ascending", count=1)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(
            response,
            '<a href="?o=-2" class="toggle ascending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_unknown_index_column(self):
        """Try to request an order on a column that doesn't exist."""
        self._get_url_list_forum_with_forums()

        # there's only 4 columns, o=3 is the maximum
        response = self.client.get("/forum/?o=4")

        # Check
        self.assertEqual(response.status_code, 200)

        # Should be sorted with default order
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(response, '<a href="?o=3">Last post</a>')
        self.assertContains(
            response,
            '<a href="?o=3" class="toggle descending" title="Toggle sorting"></a>',
        )

    def test_sorting_on_label_column(self):
        """Try to request an order on a column with a label instead of a number."""
        self._get_url_list_forum_with_forums()
        # there's only 4 columns, o=3 is the maximum and a number is expected
        response = self.client.get("/forum/?o=DATE,POST,TOPIC")
        # Check
        self.assertEqual(response.status_code, 200)

        # Should be sorted with default order
        self.assertContains(response, '<a href="?o=-0">Forums</a>')
        self.assertContains(response, '<a href="?o=-1">Topics</a>')
        self.assertContains(response, '<a href="?o=-2">Posts</a>')
        self.assertContains(response, '<a href="?o=3">Last post</a>')
        self.assertContains(
            response,
            '<a href="?o=3" class="toggle descending" title="Toggle sorting"></a>',
        )

    def test_testing_query_param(self):
        """Try to request page with param and make sure param is still in the request"""
        self._get_url_list_forum_with_forums()
        # Run
        response = self.client.get("/forum/?whatever=2")
        self.assertEqual(response.status_code, 200)

        # Should be sorted with default order
        self.assertContains(
            response, '<a href="?o=-0&whatever=2">Forums</a>', html=True
        )
        self.assertContains(
            response, '<a href="?o=-1&whatever=2">Topics</a>', html=True
        )
        self.assertContains(response, '<a href="?o=-2&whatever=2">Posts</a>', html=True)
        self.assertContains(
            response, '<a href="?o=3&whatever=2">Last post</a>', html=True
        )
        self.assertContains(
            response,
            '<a href="?o=3&whatever=2" class="toggle descending" title="Toggle sorting"></a>',
            html=True,
        )

    def test_index_view_with_archive_forum(self):
        """We archive a forum, we make sure is not displayed in the listing"""
        forum, forum2, forum3, forum4 = self._get_url_list_forum_with_forums()
        # Run
        response = self.client.get("/forum/")
        self.assertContains(response, forum.name)
        self.assertContains(response, forum2.name)
        self.assertContains(response, forum3.name)
        self.assertContains(response, forum4.name)

        # Archive forum3 and call the url
        forum3.archived = True
        forum3.save()
        response = self.client.get("/forum/")

        # Only forum3 is not shown
        self.assertContains(response, forum.name)
        self.assertContains(response, forum2.name)
        self.assertContains(response, forum4.name)

        self.assertTrue(forum3.archived)
        self.assertNotContains(response, forum3.name)

    def test_mixin_runtime_error_get_context_data(self):
        """
        Make sure the method get_context_data of OrderByColumnMixin generates a
        RuntimeError if used with no multiple inheritance.
        """
        columnMixin = OrderByColumnMixin()
        with self.assertRaises(RuntimeError) as message:
            columnMixin.get_context_data()

        self.assertEqual(
            "OrderByColumnMixin must be used as part of a multiple inheritance chain",
            str(message.exception),
        )

    def test_mixin_runtime_error_get(self):
        """
        Make sure the method get of OrderByColumnMixin generates  a RuntimeError if
        used with no multiple inheritance."""
        columnMixin = OrderByColumnMixin()
        with self.assertRaises(RuntimeError) as message:
            columnMixin.get(HttpRequest())

        self.assertEqual(
            "OrderByColumnMixin must be used as part of a multiple inheritance chain",
            str(message.exception),
        )

    def test_mixin_runtime_error_multiple_get_context_data(self):
        """
        Make sure the method get_context_data of OrderByColumnMixin generates a
        RuntimeError if used with no multiple inheritance.
        """

        class C:
            def get_context_data(self, **kwargs):
                return "works"

        class B:
            pass

        class A(OrderByColumnMixin, B):
            pass

        obj_a = A()
        with self.assertRaises(RuntimeError) as message:
            obj_a.get_context_data()

        self.assertEqual(
            "OrderByColumnMixin must be used as part of a multiple inheritance chain",
            str(message.exception),
        )

        # obj_c doesn't throw an exception
        obj_c = C()
        context = obj_c.get_context_data()
        self.assertEqual(context, "works")

    def test_mixin_runtime_error_multiple_get(self):
        """
        Make sure the method get of OrderByColumnMixin generates a
        RuntimeError if used with no multiple inheritance.
        """

        class C:
            def get(self, request, *args, **kwargs):
                return "works"

        class B:
            pass

        class A(OrderByColumnMixin, B):
            pass

        obj_a = A()
        with self.assertRaises(RuntimeError) as message:
            obj_a.get(HttpRequest())

        self.assertEqual(
            "OrderByColumnMixin must be used as part of a multiple inheritance chain",
            str(message.exception),
        )

        # obj_c doesn't throw an exception
        obj_c = C()
        context = obj_c.get(HttpRequest())
        self.assertEqual(context, "works")
