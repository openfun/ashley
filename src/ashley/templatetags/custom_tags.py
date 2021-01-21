"""Ashley template tags to display forum content"""
from django import template
from machina.core.db.models import get_model

from ashley.defaults import _FORUM_ROLE_INSTRUCTOR

LTIContext = get_model("ashley", "LTIContext")
Topic = get_model("forum_conversation", "Topic")

register = template.Library()


@register.filter()
def is_user_instructor(topic, user):
    """
    This will return a boolean indicating if the passed user is instructor
    for the given topic.
    Usage::
        {% if topic|is_user_instructor:user %}...{% endif %}
    """
    # get the list of lti concerns by this forum, one forum can have multiple LTI Context
    # if the user is instructor in one of them then he is considered
    # as instructor for this forum
    return any(
        _FORUM_ROLE_INSTRUCTOR in lti.get_user_roles(user)
        for lti in LTIContext.objects.filter(forum=topic.forum)
    )
