from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley.factories import ForumFactory, PostFactory, TopicFactory, UserFactory


class TestForumView(TestCase):
    """Displays a forum and its topics overridden from django machina."""

    def setUp(self):
        super().setUp()

        self.forum = ForumFactory()
        # create 3 topics with distinct subject, views_count and date
        PostFactory(
            topic=TopicFactory(forum=self.forum, views_count=9),
            subject="TOPIC B the eldest with 9 views_count",
        )
        PostFactory(
            topic=TopicFactory(forum=self.forum, views_count=6),
            subject="TOPIC A created second with 6 views_count",
        )

        PostFactory(
            topic=TopicFactory(forum=self.forum, views_count=12),
            subject="TOPIC C the newest one with 12 views_count",
        )
        user = UserFactory()
        assign_perm("can_read_forum", user, self.forum)
        self.client.force_login(user)

        # Setup
        self.url_list_topic = f"/forum/forum/{self.forum.slug}-{self.forum.pk}/"

    def build_column_order(self, orders):
        """
        Create sort orders for topic list view with default value.
        Build blocks by replacing attributes declared in orders from default_block
        """
        default_block = {
            "sorted": False,
            "ascending": False,
            "sort_priority": 0,
            "url_primary": "?o=",
            "url_remove": "?o=",
            "url_toggle": "?o=",
            "class_attrib": "",
        }

        return [{**default_block, **i} for i in orders]

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
        # Run
        response = self.client.get(self.url_list_topic)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_default_sorting(self):
        """By default view is sorted by last_post_on."""
        # Run
        response = self.client.get(self.url_list_topic)
        # Should have 4 columns sortable
        self.assertContains(response, "sortable ", count=4)
        # Should have no sorted column, it's the default view
        self.assertContains(response, "sorted ", count=0)
        # Should be orderedy by date by default, the latest post first
        self.assertContentBefore(
            response, "TOPIC C the newest", "TOPIC A created second"
        )
        self.assertContentBefore(
            response, "TOPIC A created second", "TOPIC B the eldest"
        )

        # Check we have expected default header links for CTAs
        self.assertEqual(
            response.context["header"],
            self.build_column_order(
                [
                    {
                        "url_primary": "?o=0",
                    },
                    {
                        "url_primary": "?o=1",
                    },
                    {
                        "url_primary": "?o=2",
                    },
                    {
                        "url_primary": "?o=3",
                    },
                ],
            ),
        )

    def test_sorting_by_subject(self):
        """Test sorting by subject."""
        # Setup add param sorting on subject
        # subject is index 0 for column 1
        url = f"{self.url_list_topic}?o=0"
        # Run
        response = self.client.get(url)

        # it should be in alphabetic order
        self.assertContentBefore(response, "TOPIC A", "TOPIC B")
        self.assertContentBefore(response, "TOPIC B", "TOPIC C")

        # Should have 1 sorted column
        self.assertContains(response, "sorted ", count=1)

        # Check we have expected default header links for each possible CTAs
        self.assertEqual(
            response.context["header"],
            self.build_column_order(
                [
                    {
                        "sorted": True,
                        "ascending": True,
                        "sort_priority": 1,
                        "url_primary": "?o=-0",
                        "url_toggle": "?o=-0",
                        "class_attrib": "sorted ascending",
                    },
                    {
                        "url_primary": "?o=1.0",
                        "url_remove": "?o=0",
                        "url_toggle": "?o=0",
                    },
                    {
                        "url_primary": "?o=2.0",
                        "url_remove": "?o=0",
                        "url_toggle": "?o=0",
                    },
                    {
                        "url_primary": "?o=3.0",
                        "url_remove": "?o=0",
                        "url_toggle": "?o=0",
                    },
                ],
            ),
        )

    def test_sorting_by_views_count_desc(self):
        """Test sorting by view count desc."""
        # Setup add param sorting on subject
        url = f"{self.url_list_topic}?o=-2"
        # Run
        response = self.client.get(url)
        # it should be in numeric order
        self.assertContentBefore(response, "12 views_count", "9 views_count")
        self.assertContentBefore(response, "9 views_count", "6 views_count")

        # Should have 1 sorted column
        self.assertContains(response, "sorted ", count=1)

        # Check we have expected default header links for each possible CTAs
        self.assertEqual(
            response.context["header"],
            self.build_column_order(
                [
                    {
                        "url_primary": "?o=0.-2",
                        "url_remove": "?o=-2",
                        "url_toggle": "?o=-2",
                    },
                    {
                        "url_primary": "?o=1.-2",
                        "url_remove": "?o=-2",
                        "url_toggle": "?o=-2",
                    },
                    {
                        "sorted": True,
                        "ascending": False,
                        "sort_priority": 1,
                        "url_primary": "?o=2",
                        "url_toggle": "?o=2",
                        "class_attrib": "sorted descending",
                    },
                    {
                        "url_primary": "?o=3.-2",
                        "url_remove": "?o=-2",
                        "url_toggle": "?o=-2",
                    },
                ],
            ),
        )

    def test_sorting_by_combined_fields(self):
        """Test sorting by combined fields number of views, subject and date."""
        # For the test we introduce 3 new topics
        # All 3 have same view_counts and 2 have same title
        PostFactory(
            topic=TopicFactory(forum=self.forum, views_count=9),
            subject=(
                "TOPIC D newer that the newest one with 9 views_count "
                "first in alphabetic order",
            ),
        )
        post_initial = PostFactory(
            topic=TopicFactory(forum=self.forum, views_count=9),
            subject=(
                "TOPIC D newer that the newest one with 9 views_count "
                "title cloned with different date",
            ),
        )
        # The next topic has 9 views as well but it's created after
        post_newest = PostFactory(
            topic=TopicFactory(forum=self.forum, views_count=9),
            subject=(
                "TOPIC D newer that the newest one with 9 views_count "
                "title cloned with different date",
            ),
        )

        # Setup add param sorting on priority 1 views, 2 post created_on and 3 subject
        url = f"{self.url_list_topic}?o=-2.0.-3"
        # Run
        response = self.client.get(url)

        # Should have 3 sorted column  views, subject and date
        self.assertContains(response, "sorted ", count=3)

        # should be order in priority 1 with views_count,
        self.assertContentBefore(response, "12 views_count", "9 views_count")
        self.assertContentBefore(response, "9 views_count", "6 views_count")
        # we have three posts that have 9 views, priority 2 subject order should be respected
        self.assertContentBefore(
            response,
            "9 views_count first in alphabetic order",
            "9 views_count title cloned with different date",
        )
        # and two that have exactly the same number of views, the same subject but different dates
        # check with the post id link that the newest is shown first as expected
        self.assertContentBefore(
            response,
            f"post={post_newest.id}#{post_newest.id}",
            f"post={post_initial.id}#{post_initial.id}",
        )

        # Check we have expected default header links for each possible actions
        self.assertEqual(
            response.context["header"],
            self.build_column_order(
                [
                    {
                        "sorted": True,
                        "ascending": True,
                        "sort_priority": 2,
                        "url_primary": "?o=-0.-2.-3",
                        "url_remove": "?o=-2.-3",
                        "url_toggle": "?o=-2.-0.-3",
                        "class_attrib": "sorted ascending",
                    },
                    {
                        "url_primary": "?o=1.-2.0.-3",
                        "url_remove": "?o=-2.0.-3",
                        "url_toggle": "?o=-2.0.-3",
                    },
                    {
                        "sorted": True,
                        "ascending": False,
                        "sort_priority": 1,
                        "url_primary": "?o=2.0.-3",
                        "url_remove": "?o=0.-3",
                        "url_toggle": "?o=2.0.-3",
                        "class_attrib": "sorted descending",
                    },
                    {
                        "sorted": True,
                        "ascending": False,
                        "sort_priority": 3,
                        "url_primary": "?o=3.-2.0",
                        "url_remove": "?o=-2.0",
                        "url_toggle": "?o=-2.0.3",
                        "class_attrib": "sorted descending",
                    },
                ],
            ),
        )

    def test_sorting_unknown_index_column(self):
        """Try to request an order on a column that doesn't exist."""
        # there's only 4 columns, o=3 is the maximum
        url = f"{self.url_list_topic}?o=5"
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

        # Should have 0 sorted column as the one asked is unknown
        self.assertContains(response, "sorted ", count=0)

    def test_sorting_on_label_column(self):
        """Try to request an order on a column with a label instead of a number."""
        # there's only 4 columns, o=3 is the maximum and a number is expected
        # point is used to separate fields
        url = f"{self.url_list_topic}?o=DATE,POST,TOPIC"
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

        # Should have 0 sorted column as the one asked is unknown
        self.assertContains(response, "sorted ", count=0)

    def test_sorting_on_mixing_type_column(self):
        """Try to request mixin good and invalid params."""
        # there's only 4 columns, o=3 is the maximum and a number is expected
        url = f"{self.url_list_topic}?o=DATE.0.7"
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

        # Should have 1 sorted column as the other two are unknown format
        self.assertContains(response, "sorted ", count=1)

        # it should be in alphabetic order
        self.assertContentBefore(response, "TOPIC A", "TOPIC B")
        self.assertContentBefore(response, "TOPIC B", "TOPIC C")

    def test_sorting_header_template_render(self):
        """Test the relation between our context header and links created in the view
        to ensure it's used
        """
        # sort on three fields
        url = f"{self.url_list_topic}?o=-2.0.3"
        # Run
        response = self.client.get(url)

        self.assertEqual(
            response.context["header"],
            self.build_column_order(
                [
                    {
                        "sorted": True,
                        "ascending": True,
                        "sort_priority": 2,
                        "url_primary": "?o=-0.-2.3",
                        "url_remove": "?o=-2.3",
                        "url_toggle": "?o=-2.-0.3",
                        "class_attrib": "sorted ascending",
                    },
                    {
                        "url_primary": "?o=1.-2.0.3",
                        "url_remove": "?o=-2.0.3",
                        "url_toggle": "?o=-2.0.3",
                    },
                    {
                        "sorted": True,
                        "ascending": False,
                        "sort_priority": 1,
                        "url_primary": "?o=2.0.3",
                        "url_remove": "?o=0.3",
                        "url_toggle": "?o=2.0.3",
                        "class_attrib": "sorted descending",
                    },
                    {
                        "sorted": True,
                        "ascending": True,
                        "sort_priority": 3,
                        "url_primary": "?o=-3.-2.0",
                        "url_remove": "?o=-2.0",
                        "url_toggle": "?o=-2.0.-3",
                        "class_attrib": "sorted ascending",
                    },
                ],
            ),
        )

        # Check topics links contains generated links
        self.assertContains(
            response,
            (
                '<a href="?o=-0.-2.3">Topics </a>'
                '<span class="sortoptions">'
                '<a class="sortremove" href="?o=-2.3" title="Remove from sorting"></a>'
                '<span class="sortpriority" title="Sorting priority: 2">2</span>'
                '<a href="?o=-2.-0.3" class="toggle ascending" title="Toggle sorting"></a>'
                "</span>"
            ),
            html=True,
        )

        # Check views links are descending and have the expected links
        self.assertContains(
            response,
            (
                '<div class="col-md-2 d-none d-md-block text-center text-nowrap '
                'topic-count-col sortable sorted descending">'
                '<a href="?o=2.0.3">Views</a>'
                '<span class="sortoptions">'
                '<a class="sortremove" href="?o=0.3" title="Remove from sorting"></a>'
                '<span class="sortpriority" title="Sorting priority: 1">1</span>'
                '<a href="?o=2.0.3" class="toggle descending" title="Toggle sorting"></a>'
                "</span>"
                "</div>"
            ),
            html=True,
        )

        # Check date link has url_primary link
        self.assertContains(response, '<a href="?o=-3.-2.0">Last post</a>')
        # Check replies link has url_primary
        self.assertContains(response, '<a href="?o=1.-2.0.3">Replies</a>')
