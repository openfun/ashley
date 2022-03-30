"""
    Forum conversation views
    ========================
    This module defines views provided by the ``forum_conversation`` application.
"""

from machina.apps.forum_conversation.views import PostCreateView as BasePostCreateView
from machina.apps.forum_conversation.views import PostUpdateView as BasePostUpdateView
from machina.apps.forum_conversation.views import TopicCreateView as BaseTopicCreateView
from machina.apps.forum_conversation.views import TopicUpdateView as BaseTopicUpdateView
from machina.apps.forum_conversation.views import TopicView as BaseTopicView
from machina.core.db.models import get_model

from .signals import post_created, post_updated, topic_created, topic_updated

LTIContext = get_model("ashley", "LTIContext")
Topic = get_model("forum_conversation", "Topic")


class SendSignalMixin:
    """Implements the signal sending at the view level."""

    view_signal = None

    def send_signal(self, request, response, **kwargs):
        """Sends the signal associated with the view."""

        self.view_signal.send(
            sender=self,
            user=request.user,
            request=request,
            response=response,
            **kwargs,
        )


class TopicCreateView(SendSignalMixin, BaseTopicCreateView):
    """Creates a topic within a forum."""

    view_signal = topic_created

    def form_valid(self, post_form, attachment_formset, poll_option_formset, **kwargs):
        """Raises topic created signal on successful topic creation"""

        response = super().form_valid(
            post_form, attachment_formset, poll_option_formset, **kwargs
        )
        self.send_signal(self.request, response, topic=self.forum_post.topic)

        return response


class TopicUpdateView(SendSignalMixin, BaseTopicUpdateView):
    """Updates an existing topic."""

    view_signal = topic_updated

    def form_valid(self, post_form, attachment_formset, poll_option_formset, **kwargs):
        """Raises topic updated signal on successful topic update"""

        response = super().form_valid(
            post_form, attachment_formset, poll_option_formset, **kwargs
        )
        self.send_signal(self.request, response, topic=self.forum_post.topic)

        return response


class PostCreateView(SendSignalMixin, BasePostCreateView):
    """Creates a post within a topic."""

    view_signal = post_created

    def form_valid(self, post_form, attachment_formset, **kwargs):
        """Raises post created signal on successful post creation"""

        response = super().form_valid(post_form, attachment_formset, **kwargs)

        self.send_signal(self.request, response, post=self.forum_post)

        return response


class PostUpdateView(SendSignalMixin, BasePostUpdateView):
    """Creates a post within a topic."""

    view_signal = post_updated

    def form_valid(self, post_form, attachment_formset, **kwargs):
        """Raises post created signal on successful post creation"""

        response = super().form_valid(post_form, attachment_formset, **kwargs)

        self.send_signal(self.request, response, post=self.forum_post)

        return response


# pylint: disable=too-many-ancestors
class TopicView(BaseTopicView):
    """Displays a forum topic."""

    def get_context_data(self, **kwargs):
        """Returns the context data to provide to the template."""
        context = super().get_context_data(**kwargs)
        # Add information about the current lti_context
        try:
            context["course_locked"] = LTIContext.objects.get(
                id=self.request.forum_permission_handler.current_lti_context_id
            ).is_marked_locked
        except LTIContext.DoesNotExist:
            context["course_locked"] = False

        return context
