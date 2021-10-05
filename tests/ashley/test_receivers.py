"""Test suite for ashley receivers"""
import json

from django.test import TestCase
from django.urls import reverse
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

Post = get_model("forum_conversation", "Post")
Topic = get_model("forum_conversation", "Topic")


class TestTrackForumView(TestCase):
    """Test the track_forum_view receiver"""

    def test_xapi_logger(self):
        """
        When a forum is viewed, the test_track_forum receiver should emit an
        XAPI event on the logger configured for the corresponding LTIConsumer.
        """

        # Create a new forum
        forum = ForumFactory()

        # Create a user with access to this forum
        user = UserFactory()
        lti_context = LTIContextFactory(
            lti_consumer=user.lti_consumer,
            lti_id="course-v1:myschool+mathematics101+session01",
        )
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        forum_url = reverse(
            "forum:forum",
            kwargs={
                "slug": forum.slug,
                "pk": forum.pk,
            },
        )

        logger_name = f"xapi.{user.lti_consumer.slug}"
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        with self.assertLogs(logger=logger_name, level="INFO") as cm:
            response = self.client.get(forum_url)

        self.assertEqual(response.status_code, 200)

        # One line of debug should have been written
        self.assertEqual(len(cm.output), 1)

        # Extract XAPI statement from log output
        log_prefix_len = len(f"{logger_name}:INFO:")
        raw_xapi_event = cm.output[0][log_prefix_len:]
        xapi_event = json.loads(raw_xapi_event)

        # The XAPI event should have an ID
        self.assertIn("id", xapi_event)

        # Validate the actor part of the XAPI event
        self.assertEqual("Agent", xapi_event["actor"]["objectType"])
        self.assertEqual(
            user.lti_consumer.url, xapi_event["actor"]["account"]["homePage"]
        )
        self.assertEqual(user.public_username, xapi_event["actor"]["account"]["name"])

        # Validate the verb
        self.assertEqual(
            "http://id.tincanapi.com/verb/viewed", xapi_event["verb"]["id"]
        )

        # Validate the activity
        self.assertEqual(f"id://ashley/forum/{forum.pk}", xapi_event["object"]["id"])
        self.assertEqual("Activity", xapi_event["object"]["objectType"])
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/community-site",
            xapi_event["object"]["definition"]["type"],
        )

        # Validate the context
        self.assertEqual(
            "course-v1:myschool+mathematics101+session01",
            xapi_event["context"]["contextActivities"]["parent"][0]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][0]["objectType"],
        )
        self.assertEqual(
            "http://adlnet.gov/expapi/activities/course",
            xapi_event["context"]["contextActivities"]["parent"][0]["definition"][
                "type"
            ],
        )


class TestTrackTopicView(TestCase):
    """Test the track_topic_view receiver"""

    def test_xapi_logger(self):
        """
        When a topic is viewed, the test_track_topic receiver should emit an
        XAPI event on the logger configured for the corresponding LTIConsumer.
        """

        # Create a topic in a new forum
        topic = TopicFactory()
        for _ in range(42):
            PostFactory(topic=topic)

        # Create a user with access to this forum
        user = UserFactory()
        lti_context = LTIContextFactory(
            lti_consumer=user.lti_consumer,
            lti_id="course-v1:myschool+mathematics101+session01",
        )
        forum = topic.forum
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        topic_url = reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_slug": topic.forum.slug,
                "forum_pk": topic.forum.pk,
                "slug": topic.slug,
                "pk": topic.pk,
            },
        )

        logger_name = f"xapi.{user.lti_consumer.slug}"
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        with self.assertLogs(logger=logger_name, level="INFO") as cm:
            response = self.client.get(topic_url, data={"page": 2})

        self.assertEqual(response.status_code, 200)

        # One line of debug should have been written
        self.assertEqual(len(cm.output), 1)

        # Extract XAPI statement from log output
        log_prefix_len = len(f"{logger_name}:INFO:")
        raw_xapi_event = cm.output[0][log_prefix_len:]
        xapi_event = json.loads(raw_xapi_event)

        # The XAPI event should have an ID
        self.assertIn("id", xapi_event)

        # Validate the actor part of the XAPI event
        self.assertEqual("Agent", xapi_event["actor"]["objectType"])
        self.assertEqual(
            user.lti_consumer.url, xapi_event["actor"]["account"]["homePage"]
        )
        self.assertEqual(user.public_username, xapi_event["actor"]["account"]["name"])

        # Validate the verb
        self.assertEqual(
            "http://id.tincanapi.com/verb/viewed", xapi_event["verb"]["id"]
        )

        # Validate the activity
        self.assertEqual(f"id://ashley/topic/{topic.pk}", xapi_event["object"]["id"])
        self.assertEqual("Activity", xapi_event["object"]["objectType"])
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/discussion",
            xapi_event["object"]["definition"]["type"],
        )

        # validate the activity definition extensions
        expected_extensions = {
            "https://w3id.org/xapi/acrossx/extensions/total-items": 42,
            "https://w3id.org/xapi/acrossx/extensions/total-pages": 3,
        }

        self.assertEqual(
            xapi_event["object"]["definition"]["extensions"], expected_extensions
        )

        # Validate the context
        self.assertEqual(
            f"uuid://{topic.forum.lti_id}",
            xapi_event["context"]["contextActivities"]["parent"][0]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][0]["objectType"],
        )
        self.assertEqual(
            xapi_event["context"]["extensions"],
            {"http://www.risc-inc.com/annotator/extensions/page": 2},
        )
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/community-site",
            xapi_event["context"]["contextActivities"]["parent"][0]["definition"][
                "type"
            ],
        )

        self.assertEqual(
            "course-v1:myschool+mathematics101+session01",
            xapi_event["context"]["contextActivities"]["parent"][1]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][1]["objectType"],
        )
        self.assertEqual(
            "http://adlnet.gov/expapi/activities/course",
            xapi_event["context"]["contextActivities"]["parent"][1]["definition"][
                "type"
            ],
        )


class TestTrackTopicCreation(TestCase):
    """Test the track_create_topic receiver"""

    def test_xapi_logger(self):
        """
        When a topic is created, the test_track_topic receiver should emit an
        XAPI event on the logger configured for the corresponding LTIConsumer.
        """

        # Create a new forum
        forum = ForumFactory()

        # Create a user with access to this forum
        user = UserFactory()
        lti_context = LTIContextFactory(
            lti_consumer=user.lti_consumer,
            lti_id="course-v1:myschool+mathematics101+session01",
        )
        forum.lti_contexts.add(lti_context)

        assign_perm("can_read_forum", user, forum, True)
        assign_perm("can_start_new_topics", user, forum, True)
        assign_perm("can_post_without_approval", user, forum, True)

        # Create a topic
        topic_creation_url = reverse(
            "forum_conversation:topic_create",
            kwargs={
                "forum_slug": forum.slug,
                "forum_pk": forum.pk,
            },
        )

        logger_name = f"xapi.{user.lti_consumer.slug}"
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        with self.assertLogs(logger=logger_name, level="INFO") as cm:
            response = self.client.post(
                topic_creation_url,
                data={
                    "subject": "foo",
                    "content": "foo text",
                    "topic_type": Topic.TOPIC_POST,
                },
                follow=True,
            )

        self.assertEqual(response.status_code, 200)

        # Identifier of created topic
        topic_pk = response.context_data["topic"].pk

        # Two lines of debug should have been written
        self.assertEqual(len(cm.output), 2)

        # Extract XAPI statement from log output
        log_prefix_len = len(f"{logger_name}:INFO:")
        raw_xapi_event = cm.output[0][log_prefix_len:]
        xapi_event = json.loads(raw_xapi_event)

        # The XAPI event should have an ID
        self.assertIn("id", xapi_event)

        # Validate the actor part of the XAPI event
        self.assertEqual("Agent", xapi_event["actor"]["objectType"])
        self.assertEqual(
            user.lti_consumer.url, xapi_event["actor"]["account"]["homePage"]
        )
        self.assertEqual(user.public_username, xapi_event["actor"]["account"]["name"])

        # Validate the verb
        self.assertEqual(
            "https://w3id.org/xapi/dod-isd/verbs/created", xapi_event["verb"]["id"]
        )

        # Validate the activity
        self.assertEqual(f"id://ashley/topic/{topic_pk}", xapi_event["object"]["id"])
        self.assertEqual("Activity", xapi_event["object"]["objectType"])
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/discussion",
            xapi_event["object"]["definition"]["type"],
        )

        # Validate the context
        self.assertEqual(
            f"uuid://{forum.lti_id}",
            xapi_event["context"]["contextActivities"]["parent"][0]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][0]["objectType"],
        )
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/community-site",
            xapi_event["context"]["contextActivities"]["parent"][0]["definition"][
                "type"
            ],
        )

        self.assertEqual(
            "course-v1:myschool+mathematics101+session01",
            xapi_event["context"]["contextActivities"]["parent"][1]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][1]["objectType"],
        )
        self.assertEqual(
            "http://adlnet.gov/expapi/activities/course",
            xapi_event["context"]["contextActivities"]["parent"][1]["definition"][
                "type"
            ],
        )


class TestTrackTopicUpdate(TestCase):
    """Test the track_update_topic receiver"""

    def test_xapi_logger(self):
        """
        When a topic is updated, the test_track_topic receiver should emit an
        XAPI event on the logger configured for the corresponding LTIConsumer.
        """

        # Create a user with access to this forum
        user = UserFactory()
        lti_context = LTIContextFactory(
            lti_consumer=user.lti_consumer,
            lti_id="course-v1:myschool+mathematics101+session01",
        )

        topic = TopicFactory(poster=user)
        first_post = PostFactory(topic=topic, poster=user)

        forum = topic.forum
        forum.lti_contexts.add(lti_context)

        assign_perm("can_read_forum", user, forum, True)
        assign_perm("can_start_new_topics", user, forum, True)
        assign_perm("can_edit_own_posts", user, forum, True)
        assign_perm("can_post_without_approval", user, forum, True)

        # Updates a topic
        topic_update_url = reverse(
            "forum_conversation:topic_update",
            kwargs={
                "forum_slug": forum.slug,
                "forum_pk": forum.pk,
                "slug": topic.slug,
                "pk": topic.pk,
            },
        )

        logger_name = f"xapi.{user.lti_consumer.slug}"
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        with self.assertLogs(logger=logger_name, level="INFO") as cm:
            response = self.client.post(
                topic_update_url,
                data={"subject": "Updated subject", "content": first_post.content},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)

        # Identifier of updated topic
        topic_pk = response.context_data["topic"].pk

        # Two lines of debug should have been written
        self.assertEqual(len(cm.output), 2)

        # Extract XAPI statement from log output
        log_prefix_len = len(f"{logger_name}:INFO:")
        raw_xapi_event = cm.output[0][log_prefix_len:]
        xapi_event = json.loads(raw_xapi_event)

        # The XAPI event should have an ID
        self.assertIn("id", xapi_event)

        # Validate the actor part of the XAPI event
        self.assertEqual("Agent", xapi_event["actor"]["objectType"])
        self.assertEqual(
            user.lti_consumer.url, xapi_event["actor"]["account"]["homePage"]
        )
        self.assertEqual(user.public_username, xapi_event["actor"]["account"]["name"])

        # Validate the verb
        self.assertEqual(
            "https://w3id.org/xapi/dod-isd/verbs/updated", xapi_event["verb"]["id"]
        )

        # Validate the activity
        self.assertEqual(f"id://ashley/topic/{topic_pk}", xapi_event["object"]["id"])
        self.assertEqual("Activity", xapi_event["object"]["objectType"])
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/discussion",
            xapi_event["object"]["definition"]["type"],
        )

        # Validate the context
        self.assertEqual(
            f"uuid://{forum.lti_id}",
            xapi_event["context"]["contextActivities"]["parent"][0]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][0]["objectType"],
        )
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/community-site",
            xapi_event["context"]["contextActivities"]["parent"][0]["definition"][
                "type"
            ],
        )

        self.assertEqual(
            "course-v1:myschool+mathematics101+session01",
            xapi_event["context"]["contextActivities"]["parent"][1]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][1]["objectType"],
        )
        self.assertEqual(
            "http://adlnet.gov/expapi/activities/course",
            xapi_event["context"]["contextActivities"]["parent"][1]["definition"][
                "type"
            ],
        )


class TestTrackPostCreation(TestCase):
    """Test the track_create_post receiver"""

    def test_xapi_logger(self):
        """
        When a post is created, the test_track_post receiver should emit an
        XAPI event on the logger configured for the corresponding LTIConsumer.
        """

        # Create a new topic
        topic = TopicFactory()
        # first_post = PostFactory(topic=topic)

        # Create a user with access to this forum
        user = UserFactory()
        lti_context = LTIContextFactory(
            lti_consumer=user.lti_consumer,
            lti_id="course-v1:myschool+mathematics101+session01",
        )
        forum = topic.forum
        forum.lti_contexts.add(lti_context)

        assign_perm("can_read_forum", user, forum, True)
        assign_perm("can_reply_to_topics", user, forum, True)
        assign_perm("can_edit_own_posts", user, forum, True)

        post_creation_url = reverse(
            "forum_conversation:post_create",
            kwargs={
                "forum_slug": forum.slug,
                "forum_pk": forum.pk,
                "topic_slug": topic.slug,
                "topic_pk": topic.pk,
            },
        )

        logger_name = f"xapi.{user.lti_consumer.slug}"
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        self.assertEqual(len(Post.objects.filter(topic=topic)), 0)

        with self.assertLogs(logger=logger_name, level="INFO") as cm:
            response = self.client.post(
                post_creation_url,
                data={
                    "subject": topic.subject,
                    "content": "foo text",
                },
                follow=True,
            )

        posts = Post.objects.filter(topic=topic)
        self.assertEqual(len(posts), 1)

        post = posts.first()

        self.assertEqual(response.status_code, 200)

        # Two lines of debug should have been written
        self.assertEqual(len(cm.output), 2)

        # Extract XAPI statement from log output
        log_prefix_len = len(f"{logger_name}:INFO:")
        raw_xapi_event = cm.output[0][log_prefix_len:]
        xapi_event = json.loads(raw_xapi_event)

        # The XAPI event should have an ID
        self.assertIn("id", xapi_event)

        # Validate the actor part of the XAPI event
        self.assertEqual("Agent", xapi_event["actor"]["objectType"])
        self.assertEqual(
            user.lti_consumer.url, xapi_event["actor"]["account"]["homePage"]
        )
        self.assertEqual(user.public_username, xapi_event["actor"]["account"]["name"])

        # Validate the verb
        self.assertEqual(
            "https://w3id.org/xapi/dod-isd/verbs/created", xapi_event["verb"]["id"]
        )

        # Validate the activity
        self.assertEqual(f"id://ashley/post/{post.pk}", xapi_event["object"]["id"])
        self.assertEqual("Activity", xapi_event["object"]["objectType"])
        self.assertEqual(
            "https://w3id.org/xapi/acrossx/activities/message",
            xapi_event["object"]["definition"]["type"],
        )

        # Validate the context
        self.assertEqual(
            f"uuid://{forum.lti_id}",
            xapi_event["context"]["contextActivities"]["parent"][0]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][0]["objectType"],
        )
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/discussion",
            xapi_event["context"]["contextActivities"]["parent"][0]["definition"][
                "type"
            ],
        )

        self.assertEqual(
            "course-v1:myschool+mathematics101+session01",
            xapi_event["context"]["contextActivities"]["parent"][1]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][1]["objectType"],
        )
        self.assertEqual(
            "http://adlnet.gov/expapi/activities/course",
            xapi_event["context"]["contextActivities"]["parent"][1]["definition"][
                "type"
            ],
        )


class TestTrackPostUpdate(TestCase):
    """Test the track_update_post receiver"""

    def test_xapi_logger(self):
        """
        When a post is updated, the test_track_post receiver should emit an
        XAPI event on the logger configured for the corresponding LTIConsumer.
        """

        # Create a user with access to this forum
        user = UserFactory()
        lti_context = LTIContextFactory(
            lti_consumer=user.lti_consumer,
            lti_id="course-v1:myschool+mathematics101+session01",
        )

        topic = TopicFactory(poster=user)
        post = PostFactory(poster=user, topic=topic)

        forum = topic.forum
        forum.lti_contexts.add(lti_context)

        assign_perm("can_read_forum", user, forum, True)
        assign_perm("can_reply_to_topics", user, forum, True)
        assign_perm("can_edit_own_posts", user, forum, True)

        post_update_url = reverse(
            "forum_conversation:post_update",
            kwargs={
                "forum_slug": forum.slug,
                "forum_pk": forum.pk,
                "topic_slug": topic.slug,
                "topic_pk": topic.pk,
                "pk": post.pk,
            },
        )

        logger_name = f"xapi.{user.lti_consumer.slug}"
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        with self.assertLogs(logger=logger_name, level="INFO") as cm:
            response = self.client.post(
                post_update_url,
                data={
                    "subject": topic.subject,
                    "content": "foo text",
                },
                follow=True,
            )

        self.assertEqual(response.status_code, 200)

        # One line of debug should have been written
        self.assertEqual(len(cm.output), 2)

        # Extract XAPI statement from log output
        log_prefix_len = len(f"{logger_name}:INFO:")
        raw_xapi_event = cm.output[0][log_prefix_len:]
        xapi_event = json.loads(raw_xapi_event)

        # The XAPI event should have an ID
        self.assertIn("id", xapi_event)

        # Validate the actor part of the XAPI event
        self.assertEqual("Agent", xapi_event["actor"]["objectType"])
        self.assertEqual(
            user.lti_consumer.url, xapi_event["actor"]["account"]["homePage"]
        )
        self.assertEqual(user.public_username, xapi_event["actor"]["account"]["name"])

        # Validate the verb
        self.assertEqual(
            "https://w3id.org/xapi/dod-isd/verbs/updated", xapi_event["verb"]["id"]
        )

        # Validate the activity
        self.assertEqual(f"id://ashley/post/{post.pk}", xapi_event["object"]["id"])
        self.assertEqual("Activity", xapi_event["object"]["objectType"])
        self.assertEqual(
            "https://w3id.org/xapi/acrossx/activities/message",
            xapi_event["object"]["definition"]["type"],
        )

        # Validate the context
        self.assertEqual(
            f"uuid://{forum.lti_id}",
            xapi_event["context"]["contextActivities"]["parent"][0]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][0]["objectType"],
        )
        self.assertEqual(
            "http://id.tincanapi.com/activitytype/discussion",
            xapi_event["context"]["contextActivities"]["parent"][0]["definition"][
                "type"
            ],
        )

        self.assertEqual(
            "course-v1:myschool+mathematics101+session01",
            xapi_event["context"]["contextActivities"]["parent"][1]["id"],
        )
        self.assertEqual(
            "Activity",
            xapi_event["context"]["contextActivities"]["parent"][1]["objectType"],
        )
        self.assertEqual(
            "http://adlnet.gov/expapi/activities/course",
            xapi_event["context"]["contextActivities"]["parent"][1]["definition"][
                "type"
            ],
        )
