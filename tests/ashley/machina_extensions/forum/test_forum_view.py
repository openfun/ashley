from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley.factories import ForumFactory, PostFactory, TopicFactory, UserFactory


class TestForumView(TestCase):
    """Displays a forum and its topics overridden from django machina."""

    def _get_url_list_topic_with_three_topics(self):
        """Creates a forum with three topics and a user to access the forum that has
        the permission to access it. It's a shortcut used in all the tests below."""
        forum = ForumFactory()
        # create 3 topics with distinct subject, views_count and date
        PostFactory(
            topic=TopicFactory(forum=forum, views_count=9),
            subject="TOPIC B the eldest with 9 views_count",
        )
        PostFactory(
            topic=TopicFactory(forum=forum, views_count=6),
            subject="TOPIC A created second with 6 views_count",
        )

        PostFactory(
            topic=TopicFactory(forum=forum, views_count=12),
            subject="TOPIC C the newest one with 12 views_count",
        )

        user = UserFactory()
        assign_perm("can_read_forum", user, forum)
        self.client.force_login(user)

        # Setup
        url_list_topic = f"/forum/forum/{forum.slug}-{forum.pk}/"

        return forum, url_list_topic

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
        _forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # Run
        response = self.client.get(url_list_topic)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_default_sorting(self):
        """By default view is sorted by last_post_on desc."""
        forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # Run
        response = self.client.get(url_list_topic)
        # Should have 4 columns sortable
        self.assertContains(response, "sortable ", count=4)

        topicC = forum.topics.get(subject__startswith="TOPIC C the newest")
        topicB = forum.topics.get(subject__startswith="TOPIC B the eldest")
        topicA = forum.topics.get(subject__startswith="TOPIC A created second")

        # Controls topic has been created in the order assumed in their titles
        self.assertTrue(topicC.last_post_on > topicA.last_post_on > topicB.last_post_on)

        # Should be orderedy by date by default, the newest post first
        self.assertContentBefore(
            response, "TOPIC C the newest", "TOPIC A created second"
        )
        self.assertContentBefore(
            response, "TOPIC A created second", "TOPIC B the eldest"
        )

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected result in html
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(response, '<a href="?o=3">Last post</a>')
        self.assertContains(
            response,
            '<a href="?o=3" class="toggle descending" title="Toggle sorting"></a>',
        )

    def test_sorting_by_subject_asc(self):
        """Test sorting by subject."""
        forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # Setup add param sorting on subject, subject is index 0 for column 1
        url = f"{url_list_topic}?o=0"
        response = self.client.get(url)

        topicC = forum.topics.get(subject__startswith="TOPIC C the newest")
        topicB = forum.topics.get(subject__startswith="TOPIC B the eldest")
        topicA = forum.topics.get(subject__startswith="TOPIC A created second")

        # Controls topic has been created in the order assumed in their titles
        self.assertTrue(topicC.last_post_on > topicA.last_post_on > topicB.last_post_on)

        # it should be in alphabetic order
        self.assertContentBefore(response, "TOPIC A", "TOPIC B")
        self.assertContentBefore(response, "TOPIC B", "TOPIC C")

        # Should have 1 sorted column and it should be ascending
        self.assertContains(response, "sortable sorted descending", count=0)
        self.assertContains(response, "sortable sorted ascending", count=1)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(
            response,
            '<a href="?o=-0" class="toggle ascending" title="Toggle sorting"></a>',
        )

        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_subject_desc(self):
        """Test sorting by subject desc."""
        forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # Setup add param sorting on subject, subject is index 0 for column 1
        url = f"{url_list_topic}?o=-0"
        response = self.client.get(url)

        topicC = forum.topics.get(subject__startswith="TOPIC C the newest")
        topicB = forum.topics.get(subject__startswith="TOPIC B the eldest")
        topicA = forum.topics.get(subject__startswith="TOPIC A created second")

        # Controls topic has been created in the order assumed in their titles
        self.assertTrue(topicC.last_post_on > topicA.last_post_on)
        self.assertTrue(topicA.last_post_on > topicB.last_post_on)

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=0">Topics</a>')
        self.assertContains(
            response,
            '<a href="?o=0" class="toggle descending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_posts_count_asc(self):
        """Test sorting by posts count desc."""
        forum, url_list_topic = self._get_url_list_topic_with_three_topics()

        topicA = forum.topics.get(subject__startswith="TOPIC A")
        topicB = forum.topics.get(subject__startswith="TOPIC B")
        topicC = forum.topics.get(subject__startswith="TOPIC C")

        # 2 extra posts in topic B
        PostFactory(topic=topicB)
        PostFactory(topic=topicB)
        # 1 extra posts in topic C
        PostFactory(topic=topicC)

        # Controls order of posts
        self.assertTrue(
            topicB.posts.count() > topicC.posts.count() > topicA.posts.count()
        )

        url = f"{url_list_topic}?o=1"
        response = self.client.get(url)

        # Topic with the lowest number of post should be first
        self.assertContentBefore(response, "TOPIC A", "TOPIC C")
        self.assertContentBefore(response, "TOPIC C", "TOPIC B")

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=0)
        self.assertContains(response, "sortable sorted ascending", count=1)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(
            response,
            '<a href="?o=-1" class="toggle ascending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_posts_count_desc(self):
        """Test sorting by posts count desc."""
        forum, url_list_topic = self._get_url_list_topic_with_three_topics()

        topicA = forum.topics.get(subject__startswith="TOPIC A")
        topicB = forum.topics.get(subject__startswith="TOPIC B")
        topicC = forum.topics.get(subject__startswith="TOPIC C")

        # 2 extra posts in topic B
        PostFactory(topic=topicB)
        PostFactory(topic=topicB)
        # 1 extra posts in topic C
        PostFactory(topic=topicC)

        # Controls order of posts
        self.assertTrue(
            topicB.posts.count() > topicC.posts.count() > topicA.posts.count()
        )

        url = f"{url_list_topic}?o=-1"
        response = self.client.get(url)

        # Topic with the highest number of post should be first
        self.assertContentBefore(response, "TOPIC B", "TOPIC C")
        self.assertContentBefore(response, "TOPIC C", "TOPIC A")

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(response, '<a href="?o=1">Replies</a>')
        self.assertContains(
            response,
            '<a href="?o=1" class="toggle descending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_views_count_desc(self):
        """Test sorting by view count desc."""
        forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # Setup add param sorting on subject
        url = f"{url_list_topic}?o=-2"
        response = self.client.get(url)

        # Controls topic have ordered view assumed in their titles
        topic12 = forum.topics.get(subject__contains="12 views_count")
        topic9 = forum.topics.get(subject__contains="9 views_count")
        topic6 = forum.topics.get(subject__contains="6 views_count")
        self.assertTrue(topic12.views_count > topic9.views_count > topic6.views_count)

        # it should be in numeric order
        self.assertContentBefore(response, "12 views_count", "9 views_count")
        self.assertContentBefore(response, "9 views_count", "6 views_count")

        # Should have 1 sorted column and it should be descending
        self.assertContains(response, "sortable sorted descending", count=1)
        self.assertContains(response, "sortable sorted ascending", count=0)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(response, '<a href="?o=2">Views</a>')
        self.assertContains(
            response,
            '<a href="?o=2" class="toggle descending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_by_views_count_asc(self):
        """Test sorting by view count asc."""
        forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # Setup add param sorting on subject
        url = f"{url_list_topic}?o=2"
        response = self.client.get(url)

        topic12 = forum.topics.get(subject__contains="12 views_count")
        topic9 = forum.topics.get(subject__contains="9 views_count")
        topic6 = forum.topics.get(subject__contains="6 views_count")

        # Topic have views_count assumed in their titles
        self.assertTrue(topic12.views_count > topic9.views_count > topic6.views_count)

        # it should be in numeric order with smallest first
        self.assertContentBefore(response, "6 views_count", "9 views_count")
        self.assertContentBefore(response, "9 views_count", "12 views_count")

        # Should have 1 sorted column and it should be ascending
        self.assertContains(response, "sortable sorted descending", count=0)
        self.assertContains(response, "sortable sorted ascending", count=1)

        # Check we have expected links to order columns in html
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(
            response,
            '<a href="?o=-2" class="toggle ascending" title="Toggle sorting"></a>',
        )
        self.assertContains(response, '<a href="?o=-3">Last post</a>')

    def test_sorting_unknown_index_column(self):
        """Try to request an order on a column that doesn't exist."""
        _forum, url_list_topic = self._get_url_list_topic_with_three_topics()

        # there's only 4 columns, o=3 is the maximum
        url = f"{url_list_topic}?o=4"
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)

        # Should be sorted with default order
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(response, '<a href="?o=3">Last post</a>')
        self.assertContains(
            response,
            '<a href="?o=3" class="toggle descending" title="Toggle sorting"></a>',
        )

    def test_sorting_on_label_column(self):
        """Try to request an order on a column with a label instead of a number."""
        _forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # there's only 4 columns, o=3 is the maximum and a number is expected
        url = f"{url_list_topic}?o=DATE,POST,TOPIC"
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

        # Should be sorted with default order
        self.assertContains(response, '<a href="?o=-0">Topics</a>')
        self.assertContains(response, '<a href="?o=-1">Replies</a>')
        self.assertContains(response, '<a href="?o=-2">Views</a>')
        self.assertContains(response, '<a href="?o=3">Last post</a>')
        self.assertContains(
            response,
            '<a href="?o=3" class="toggle descending" title="Toggle sorting"></a>',
        )

    def test_testing_query_param(self):
        """Try to request page with param and make sure param is still in the request"""
        _forum, url_list_topic = self._get_url_list_topic_with_three_topics()
        # there's only 4 columns, o=3 is the maximum and a number is expected
        url = f"{url_list_topic}?whatever=2"
        # Run
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Should be sorted with default order
        self.assertContains(
            response, '<a href="?o=-0&whatever=2">Topics</a>', html=True
        )
        self.assertContains(
            response, '<a href="?o=-1&whatever=2">Replies</a>', html=True
        )
        self.assertContains(response, '<a href="?o=-2&whatever=2">Views</a>', html=True)
        self.assertContains(
            response, '<a href="?o=3&whatever=2">Last post</a>', html=True
        )
        self.assertContains(
            response,
            '<a href="?o=3&whatever=2" class="toggle descending" title="Toggle sorting"></a>',
            html=True,
        )
