"""
    Forum conversation forms
    ========================

    This module defines forms provided by the ``forum_conversation`` application.

"""
from machina.apps.forum_conversation.forms import PostForm as MachinaPostForm
from machina.apps.forum_conversation.forms import TopicForm as MachinaTopicForm


class PostForm(MachinaPostForm):
    """Overload Machina PostForm to send extra variables to the widget editor"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # collect extra informations used by the editor
        self.fields["content"].widget.attrs.update(
            {
                "mentions": self.topic.get_active_users(self.user),
                "forum": self.forum.id,
            }
        )

        # remove unused machina placeholder, placeholder is created in our component AshleyEditor
        self.fields["content"].widget.attrs.pop("placeholder")


class TopicForm(MachinaTopicForm):
    """Overload Machina TopicForm to send extra variables to the widget editor for the
    Topic creation. TopicForm is loaded only for the initial post of the topic."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.topic is not None and self.topic.posts_count > 1:
            # will be useful only if this first post is edited after answers
            self.fields["content"].widget.attrs[
                "mentions"
            ] = self.topic.get_active_users(self.user)

        # send extra informations used by the editor
        self.fields["content"].widget.attrs.update({"forum": self.forum.id})

        # remove unused machina placeholder, placeholder is created in our component AshleyEditor
        self.fields["content"].widget.attrs.pop("placeholder")
