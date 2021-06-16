"""
    Forum moderation forms
    ======================

    This module overrides forms provided by the ``forum_moderation`` application.

"""
from machina.apps.forum_moderation.forms import TopicMoveForm as MachinaTopicMoveForm
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model("forum", "Forum")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")


class TopicMoveForm(MachinaTopicMoveForm):
    """ Allows to move a topic. """

    def __init__(self, *args, **kwargs):
        """
        Overrides original __init__ method to filter forums in order to show only the ones from
        the same LTIContext
        """
        lti_context = kwargs.pop("lti_context", None)
        super().__init__(*args, **kwargs)
        # Overrides method and instanciates PermissionHandler with current lti_context.id
        self.perm_handler = PermissionHandler()
        self.perm_handler.current_lti_context_id = lti_context.id
        self.allowed_forums = self.perm_handler.get_target_forums_for_moved_topics(
            self.user
        )

        allowed_forums_ids = [f.id for f in self.allowed_forums]
        filtered_choices = filter(
            lambda c: c[0] in allowed_forums_ids, self.fields["forum"].choices
        )
        self.fields["forum"].choices = filtered_choices
