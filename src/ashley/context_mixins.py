"""Mixins based on current LTIContext Session"""
from machina.core.db.models import get_model

from . import SESSION_LTI_CONTEXT_ID

LTIContext = get_model("ashley", "LTIContext")
Forum = get_model("forum", "Forum")


def get_current_lti_session(request):
    """
    Gets from current session the corresponding LTIContext object.
    """
    if request.user.is_authenticated and request.session.get(SESSION_LTI_CONTEXT_ID):
        return LTIContext.objects.get(id=request.session[SESSION_LTI_CONTEXT_ID])

    return None


def get_current_lti_session_first_forum(request):
    """
    Gets an eligible forum from current LTIContext object.
    A LTIContext can have multiple forums.
    """
    if request.user.is_authenticated and request.session.get(SESSION_LTI_CONTEXT_ID):
        context = get_current_lti_session(request)
        return Forum.objects.filter(lti_contexts=context).first()

    return None
