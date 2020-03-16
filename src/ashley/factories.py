"""Factories for the ``ashley`` application."""
import factory
from factory.django import DjangoModelFactory
from machina.core.db.models import get_model

from lti_provider.factories import LTIConsumerFactory

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