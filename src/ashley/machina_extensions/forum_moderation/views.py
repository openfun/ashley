"""
    Forum moderation views
    ======================

    This module overrides views provided by the ``forum_moderation`` application.

"""

from machina.apps.forum_moderation.views import TopicMoveView as MachinaTopicMoveView

from ashley.context_mixins import get_current_lti_session


class TopicMoveView(MachinaTopicMoveView):
    """Overrides MachinaTopicMoveView to filter on forums part of the LTIContext"""

    def get_form_kwargs(self):
        """Returns the keyword arguments used to initialize the associated form."""
        return {
            **super().get_form_kwargs(),
            "lti_context": get_current_lti_session(self.request),
        }
