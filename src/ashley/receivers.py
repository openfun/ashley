"""This module defines signal receivers for the Ashley application"""

import logging

from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import to_locale
from machina.apps.forum_conversation.signals import topic_viewed
from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from tincan import (
    Activity,
    ActivityDefinition,
    Context,
    ContextActivities,
    LanguageMap,
    Verb,
)

from .xapi import build_statement

LTIContext = get_model("ashley", "LTIContext")

logger = logging.getLogger(__name__)


@receiver(topic_viewed)
# pylint: disable=unused-argument
def track_topic_view(sender, topic, user, request, response, **kwargs):
    """ Log a XAPI statement when a user views a topic. """

    consumer = getattr(user, "lti_consumer", None)
    if consumer is None:
        logger.warning("Unable to get LTI consumer of user %s", user)
        return
    xapi_logger = logging.getLogger(f"xapi.{user.lti_consumer.slug}")

    verb = Verb(
        id="http://id.tincanapi.com/verb/viewed",
        display=LanguageMap({"en-US": "viewed"}),
    )

    obj = Activity(
        id=f"id://ashley/topic/{topic.pk}",
        definition=ActivityDefinition(
            name=LanguageMap(
                {to_locale(settings.LANGUAGE_CODE).replace("_", "-"): topic.subject}
            ),
            type="http://id.tincanapi.com/activitytype/discussion",
            extensions={
                "https://w3id.org/xapi/acrossx/extensions/total-items": topic.posts_count,
                "https://w3id.org/xapi/acrossx/extensions/total-pages": (
                    (topic.posts_count - 1)
                    // machina_settings.TOPIC_POSTS_NUMBER_PER_PAGE
                )
                + 1,
            },
        ),
    )

    parent_activities = [
        Activity(
            id=f"uuid://{topic.forum.lti_id}",
            definition=ActivityDefinition(
                name=LanguageMap(
                    {
                        to_locale(settings.LANGUAGE_CODE).replace(
                            "_", "-"
                        ): topic.forum.name
                    }
                ),
                type="http://id.tincanapi.com/activitytype/community-site",
            ),
        )
    ]

    if request.forum_permission_handler.current_lti_context_id is not None:
        try:
            lti_context = LTIContext.objects.get(
                pk=request.forum_permission_handler.current_lti_context_id
            )
            parent_activities.append(
                Activity(
                    id=lti_context.lti_id,
                    definition=ActivityDefinition(
                        type="http://adlnet.gov/expapi/activities/course"
                    ),
                )
            )

        except LTIContext.DoesNotExist:
            pass

    context = Context(
        context_activities=ContextActivities(parent=parent_activities),
        extensions={
            "http://www.risc-inc.com/annotator/extensions/page": int(
                request.GET.get("page", default=1)
            )
        },
    )

    statement = build_statement(user, verb, obj, context)
    if statement:
        xapi_logger.info(statement.to_json())
