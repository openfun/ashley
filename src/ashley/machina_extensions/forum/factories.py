"""Factories for the ``forum`` application."""
import factory
from factory.django import DjangoModelFactory
from lti_toolbox.factories import LTIConsumerFactory
from machina.core.db.models import get_model

Forum = get_model("forum", "Forum")  # pylint: disable=C0103


class CourseForumFactory(DjangoModelFactory):
    """Factory to create a Forum related to a course."""

    class Meta:
        model = Forum

    type = Forum.FORUM_POST
    name = factory.Sequence(lambda n: f"Forum {n}")
    lti_context = factory.Sequence(lambda n: f"course{n}")
    lti_consumer = factory.SubFactory(LTIConsumerFactory)
