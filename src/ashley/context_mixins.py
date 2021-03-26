"""Mixins based on current LTIContext Session"""
from machina.core.db.models import get_model

from . import SESSION_LTI_CONTEXT_ID

LTIContext = get_model("ashley", "LTIContext")


def get_current_lti_session(request):
    """
    Gets from current session the corresponding LTIContext object.
    """
    if request.user.is_authenticated and request.session.get(SESSION_LTI_CONTEXT_ID):
        return LTIContext.objects.get(id=request.session[SESSION_LTI_CONTEXT_ID])

    return None
