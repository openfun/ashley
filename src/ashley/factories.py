"""Factories for the ``ashley`` application."""
import factory
from factory.django import DjangoModelFactory
from lti_toolbox.factories import LTIConsumerFactory
from machina.core.db.models import get_model

Forum = get_model("forum", "Forum")  # pylint: disable=C0103
LTIContext = get_model("ashley", "LTIContext")  # pylint: disable=C0103
User = get_model("ashley", "User")  # pylint: disable=C0103


class UserFactory(DjangoModelFactory):
    """Factory to create a User."""

    class Meta:
        model = User

    lti_consumer = factory.SubFactory(LTIConsumerFactory)

    public_username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda u: f"{u.public_username}@example.com")
    lti_remote_user_id = factory.SelfAttribute("public_username")
    username = factory.LazyAttribute(
        lambda u: f"{u.public_username}@{u.lti_consumer.slug}"
    )


class LTIContextFactory(DjangoModelFactory):
    """Factory to create a LTIContext."""

    class Meta:
        model = LTIContext

    lti_consumer = factory.SubFactory(LTIConsumerFactory)
    lti_id = factory.Sequence(lambda n: f"context{n}")


class ForumFactory(DjangoModelFactory):
    """Factory to create a Forum"""

    class Meta:
        model = Forum

    type = Forum.FORUM_POST
    name = factory.Sequence(lambda n: f"forum{n}")
