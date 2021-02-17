from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model
from machina.core.loading import get_class

from ashley.factories import (
    ForumFactory,
    LTIConsumerFactory,
    LTIContextFactory,
    PostFactory,
    TopicFactory,
    UserFactory,
)
from ashley.machina_extensions.forum_conversation.forms import PostForm

get_forum_member_display_name = get_class(
    "forum_member.shortcuts", "get_forum_member_display_name"
)
Post = get_model("forum_conversation", "Post")
Forum = get_model("forum", "Forum")


class ForumConversationTestPostCreateView(TestCase):
    """Test post form of a forum overridden from django_machina"""

    def setUp(self):
        super().setUp()
        # Setup
        # Create consumer, context and user
        self.lti_consumer = LTIConsumerFactory()
        self.context = LTIContextFactory(lti_consumer=self.lti_consumer)

        # Create forum and add context
        self.forum = ForumFactory(name="Forum")
        self.forum.lti_contexts.add(self.context)

    def test_list_active_users_empty_topic_with_no_post(self):
        """
        The form loads the list of active users for the current topic. We control that the list
        is empty when topic has no post
        """
        # Setup
        user1 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Benoit",
        )
        self.context.sync_user_groups(user1, ["student"])

        # Set up topic and initial post
        topic = TopicFactory(forum=self.forum, poster=user1)
        # Load PostForm for user1
        form = PostForm(user=user1, forum=self.forum, topic=topic)
        # No post created yet, mention_users should be empty
        assert form.fields["content"].widget.attrs["mention_users"] == []

    def test_list_active_users_ignore_current_user(self):
        """
        The form loads the list of active users for the current topic. We control that the list
        ignores the current user
        """
        # Setup
        user1 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Benoit",
        )
        user2 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Alfred",
        )
        self.context.sync_user_groups(user1, ["student"])
        self.context.sync_user_groups(user2, ["student"])

        # Set up topic and initial post
        topic = TopicFactory(forum=self.forum, poster=user1)

        # Add a Post for user1
        PostFactory(topic=topic, poster=user1)

        # User2 loads the form
        form = PostForm(user=user2, forum=self.forum, topic=topic)
        # User1 must be listed in users
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Benoit",
                "user": user1.id,
            }
        ]
        # User1 loads the form
        form = PostForm(user=user1, forum=self.forum, topic=topic)
        # Check current user is ignored in the list
        assert form.fields["content"].widget.attrs["mention_users"] == []

    def test_list_active_users_ordered_by_alphabetical_order(self):
        """
        The form loads the list of active users for the current topic. We control that the list is
        rendered in alphabetical order
        """
        # Setup
        user1 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Benoit",
        )
        user2 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Alfred",
        )
        user3 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Aurélien",
        )
        user4 = UserFactory(lti_consumer=self.lti_consumer)
        self.context.sync_user_groups(user1, ["student"])
        self.context.sync_user_groups(user2, ["student"])
        self.context.sync_user_groups(user3, ["student"])

        # Set up topic and initial post
        topic = TopicFactory(forum=self.forum, poster=user1)

        # Add post with user1
        PostFactory(topic=topic, poster=user1)

        # user2 loads the form
        form = PostForm(
            user=user2,
            forum=self.forum,
            topic=topic,
        )
        # user2 sees user1
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Benoit",
                "user": user1.id,
            },
        ]
        # Add posts from user2
        PostFactory(topic=topic, poster=user2)

        # Load form from user 3
        form = PostForm(user=user3, forum=self.forum, topic=topic)
        # Alfred should be before Benoit
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Alfred",
                "user": user2.id,
            },
            {
                "name": "Benoit",
                "user": user1.id,
            },
        ]
        # Add posts from user3
        PostFactory(topic=topic, poster=user3)
        form = PostForm(user=user4, forum=self.forum, topic=topic)
        # Alfred should be before Aurélien and before Benoit
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Alfred",
                "user": user2.id,
            },
            {
                "name": "Aurélien",
                "user": user3.id,
            },
            {
                "name": "Benoit",
                "user": user1.id,
            },
        ]

    def test_list_active_users_has_distinct_users(self):
        """
        The form loads the list of active users for the current topic. We control that the list
        only contains distinct users
        """
        user1 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Benoit",
        )
        user2 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Alfred",
        )
        self.context.sync_user_groups(user1, ["student"])
        self.context.sync_user_groups(user2, ["student"])

        # Set up topic and initial post
        topic = TopicFactory(forum=self.forum, poster=user1)

        # Add three posts from user1 and two from user2
        initial_post_count = Post.objects.count()
        PostFactory(topic=topic, poster=user1)
        PostFactory(topic=topic, poster=user1)
        PostFactory(topic=topic, poster=user1)
        PostFactory(topic=topic, poster=user2)
        PostFactory(topic=topic, poster=user2)
        # Confirms Posts got created
        self.assertEqual(Post.objects.count(), initial_post_count + 5)

        # user2 loads the form
        form = PostForm(user=user2, forum=self.forum, topic=topic)
        # user2 only see one time user1
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Benoit",
                "user": user1.id,
            }
        ]

        # user1 loads the form
        form = PostForm(user=user1, forum=self.forum, topic=topic)
        # user1 only see one time user1
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Alfred",
                "user": user2.id,
            },
        ]

    def test_list_active_users_only_concerns_writer_of_current_topic(self):
        """
        The form loads the list of active users for the current topic. We control that the list
        only contains writers involved in the current topic and no other users
        """
        user1 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Benoit",
        )
        user2 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Alfred",
        )
        user3 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Aurélien",
        )
        user4 = UserFactory(
            lti_consumer=self.lti_consumer,
        )
        self.context.sync_user_groups(user1, ["student"])
        self.context.sync_user_groups(user2, ["student"])
        self.context.sync_user_groups(user3, ["student"])
        self.context.sync_user_groups(user4, ["student"])

        # Set up topic and initial post
        topic = TopicFactory(forum=self.forum, poster=user1)
        # Add two posts for topic
        PostFactory(topic=topic, poster=user1)
        PostFactory(topic=topic, poster=user2)
        # user4 loads the form
        form = PostForm(user=user4, forum=self.forum, topic=topic)
        # Two users should be listed
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Alfred",
                "user": user2.id,
            },
            {
                "name": "Benoit",
                "user": user1.id,
            },
        ]

        # Set up new topic and initial post with user3
        topic2 = TopicFactory(forum=self.forum, poster=user3)
        PostFactory(topic=topic2, poster=user3)

        # user4 loads the form for topic2
        form = PostForm(
            user=user4,
            forum=self.forum,
            topic=topic2,
        )
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Aurélien",
                "user": user3.id,
            }
        ]
        # user4 loads topic, nothing should have changed as user3 only posted in another topic
        form = PostForm(
            user=user4,
            forum=self.forum,
            topic=topic,
        )
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Alfred",
                "user": user2.id,
            },
            {
                "name": "Benoit",
                "user": user1.id,
            },
        ]

    def test_list_active_users_only_concerns_users_with_approved_posts(self):
        """
        The form loads the list of active users for the current topic. We control that the list
        only concerns users that have approved posts
        """
        user1 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Benoit",
        )
        user2 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Alfred",
        )

        self.context.sync_user_groups(user1, ["student"])
        self.context.sync_user_groups(user2, ["student"])

        topic = TopicFactory(forum=self.forum, poster=user1)
        post = PostFactory(topic=topic, poster=user1)

        form = PostForm(user=user2, forum=self.forum, topic=topic)
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Benoit",
                "user": user1.id,
            }
        ]
        # Post of user1 gets unapproved
        post.approved = False
        post.save()
        # Load form from user2
        form = PostForm(
            user=user2,
            forum=self.forum,
            topic=topic,
        )
        # List of active users should be empty
        assert form.fields["content"].widget.attrs["mention_users"] == []

    def test_list_active_users_only_concerns_active_users(self):
        """
        The form loads the list of active users for the current topic. We control that the list
        only concerns users that have the status active
        """
        user1 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Benoit",
        )
        user2 = UserFactory(
            lti_consumer=self.lti_consumer,
            public_username="Alfred",
        )
        self.context.sync_user_groups(user1, ["student"])
        self.context.sync_user_groups(user2, ["student"])

        topic = TopicFactory(forum=self.forum, poster=user1)
        PostFactory(topic=topic, poster=user1)

        form = PostForm(user=user2, forum=self.forum, topic=topic)
        assert form.fields["content"].widget.attrs["mention_users"] == [
            {
                "name": "Benoit",
                "user": user1.id,
            }
        ]
        # user1 becomes inactive
        user1.is_active = False
        user1.save()
        # user3 loads the form for topic
        form = PostForm(user=user2, forum=self.forum, topic=topic)
        # We should only see user1 in the list of active users for this topic
        assert form.fields["content"].widget.attrs["mention_users"] == []

    def test_access_topic_reply_form(self):
        """
        The post form in a created topic is overridden from django_machina,
        we control it still loads as expected
        """
        user = UserFactory(lti_consumer=self.lti_consumer)
        assign_perm("can_read_forum", user, self.forum)
        assign_perm("can_reply_to_topics", user, self.forum)

        # Set up topic and initial post
        topic = TopicFactory(forum=self.forum, poster=user)
        PostFactory(topic=topic)

        # authenticate the user related to consumer
        self.client.force_login(user)

        url_topic_reply = (
            f"/forum/forum/{self.forum.slug}-{self.forum.pk}"
            f"/topic/{topic.slug}-{topic.pk}/post/create/"
        )

        # Run
        response = self.client.get(url_topic_reply, follow=True)
        # Check
        assert response.status_code == 200
