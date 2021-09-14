"""Test suite for ashley receivers"""
import json

from django.test import TestCase
from django.urls import reverse
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import LTIContextFactory, PostFactory, TopicFactory, UserFactory


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
        with self.assertLogs(logger=logger_name, level="INFO") as cm:
            self.client.force_login(user, "ashley.auth.backend.LTIBackend")
            session = self.client.session
            session[SESSION_LTI_CONTEXT_ID] = lti_context.id
            session.save()
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
            self.assertEqual(
                user.public_username, xapi_event["actor"]["account"]["name"]
            )

            # Validate the verb
            self.assertEqual(
                "http://id.tincanapi.com/verb/viewed", xapi_event["verb"]["id"]
            )

            # Validate the activity
            self.assertEqual(
                f"id://ashley/topic/{topic.pk}", xapi_event["object"]["id"]
            )
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
