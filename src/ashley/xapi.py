"""XAPI module."""
import logging
import uuid
from typing import Optional

from django.utils import timezone
from tincan import Activity, Agent, AgentAccount, Context, Statement, Verb

from ashley.models import AbstractUser

logger = logging.getLogger(__name__)


def build_statement(
    user: AbstractUser,
    verb: Verb,
    obj: Activity,
    context: Context,
    statement_id: Optional[uuid.UUID] = None,
) -> Optional[Statement]:
    """Build a XAPI Statement based on the current context"""
    timestamp = timezone.now().isoformat()
    actor = _get_actor_from_user(user)
    if statement_id is None:
        statement_id = uuid.uuid4()
    if actor is None:
        logger.warning("Unable to get an XAPI actor definition for user %s", user.id)
        return None
    return Statement(
        actor=actor,
        context=context,
        id=statement_id,
        object=obj,
        timestamp=timestamp,
        verb=verb,
    )


def _get_actor_from_user(user: AbstractUser) -> Optional[Agent]:
    """Generate a XAPI Agent object from a Ashley User object"""
    if user.lti_remote_user_id and user.lti_consumer.url:
        return Agent(
            account=AgentAccount(
                name=user.lti_remote_user_id, home_page=user.lti_consumer.url
            )
        )
    return None
