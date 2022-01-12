"""Ashley template tags to display forum content"""
from django import template
from machina.core.db.models import get_model
from machina.templatetags.forum_tags import forum_list

from ashley.defaults import _FORUM_ROLE_ADMINISTRATOR, _FORUM_ROLE_INSTRUCTOR

LTIContext = get_model("ashley", "LTIContext")

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


@register.filter()
def is_user_administrator(topic, user):
    """
    This will return a boolean indicating if the passed user is admin
    for the given topic.
    Usage::
        {% if topic|is_user_administrator:user %}...{% endif %}
    """
    # get the list of lti concerns by this forum, one forum can have multiple LTI Context
    # if the user is admin in one of them then he is considered
    # as admin for this forum
    return any(
        _FORUM_ROLE_ADMINISTRATOR in lti.get_user_roles(user)
        for lti in LTIContext.objects.filter(forum=topic.forum)
    )


@register.inclusion_tag("forum/forum_list.html", takes_context=True)
def forum_list_order(context, forum_visibility_contents):
    """Renders the considered forum list with the column order added.

    Usage::

        {% forum_list_order my_forums %}

    """
    data_dict = forum_list(context, forum_visibility_contents)
    data_dict["header"] = context.get("header")
    return data_dict
