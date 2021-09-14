"""Test suite for Ashley's xapi module"""
import uuid

from django.test import TestCase
from tincan import (
    Activity,
    ActivityDefinition,
    Context,
    ContextActivities,
    LanguageMap,
    Verb,
)

from ashley.factories import UserFactory
from ashley.xapi import build_statement


class TestXAPI(TestCase):
    """Test utility functions provided by the xapi module"""

    def test_build_statement(self):
        """
        The build_statement function should return a valid tincan
        Statement.
        """
        user = UserFactory()

        verb = Verb(
            id="https://activitystrea.ms/schema/1.0/create",
            display=LanguageMap({"en-US": "created"}),
        )
        activity = Activity(
            id=f"id://ashley/topic/{uuid.uuid4()}",
            definition=ActivityDefinition(
                name=LanguageMap({"en-US": "test topic"}),
                type="http://id.tincanapi.com/activitytype/discussion",
            ),
        )
        context = Context(
            context_activities=ContextActivities(
                parent=[
                    Activity(
                        id=f"uuid://{uuid.uuid4()}",
                        definition=ActivityDefinition(
                            name=LanguageMap({"en-US": "test forum"}),
                            type="http://id.tincanapi.com/activitytype/community-site",
                        ),
                    )
                ]
            )
        )

        statement1 = build_statement(user, verb, activity, context)
        statement2 = build_statement(user, verb, activity, context)

        # The function should generate a random, non empty uuid as a
        # statement ID
        self.assertIsInstance(statement1.id, uuid.UUID)
        self.assertIsInstance(statement2.id, uuid.UUID)
        self.assertNotEqual(statement1.id, statement2.id)

        # The statement id can also be specified
        statement3_id = uuid.uuid4()
        statement3 = build_statement(user, verb, activity, context, statement3_id)
        self.assertEqual(statement3_id, statement3.id)

        # The verb, object and context should correspond to the given arguments
        self.assertEqual(statement1.verb, verb)
        self.assertEqual(statement1.object, activity)
        self.assertEqual(statement1.context, context)

        # The Actor part of the statement should reflect the user passed as an
        # argument
        self.assertEqual(statement1.actor.account.name, user.lti_remote_user_id)
        self.assertEqual(statement1.actor.account.home_page, user.lti_consumer.url)
