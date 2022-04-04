"""
    Forum search forms
    ==================
    This module defines forms provided by the ``forum_search`` application.
"""
from django.utils.translation import gettext_lazy as _
from machina.apps.forum_search.forms import SearchForm as MachinaSearchForm
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model("forum", "Forum")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")


class SearchForm(MachinaSearchForm):
    """
    Allows to search forum topics and posts and allows searching poster user names
    even with an empty search in the main field.
    """

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        lti_contexts = kwargs.pop("lti_context", None)

        # pylint: disable=bad-super-call
        super(MachinaSearchForm, self).__init__(*args, **kwargs)

        # Update some fields
        self.fields["q"].label = _("Search for keywords")
        self.fields["q"].widget.attrs["placeholder"] = _("Keywords or phrase")
        self.fields["search_poster_name"].widget.attrs["placeholder"] = _("Poster name")

        self.perm_handler = PermissionHandler()

        # add context
        if lti_contexts:
            self.perm_handler.current_lti_context_id = lti_contexts.id

        # forums gets filtered by lti_context and exclude archives directly
        # in get_readable_forums
        self.allowed_forums = self.perm_handler.get_readable_forums(
            Forum.objects.all(), user
        )
        # pylint: disable=consider-using-f-string
        if self.allowed_forums:
            self.fields["search_forums"].choices = [
                (f.id, "{} {}".format("-" * f.margin_level, f.name))
                for f in self.allowed_forums
            ]
        else:
            # The user cannot view any single forum, the 'search_forums' field can be deleted
            del self.fields["search_forums"]

    def clean(self):
        """
        Set main query to catch all "*" if it is empty and there is a search term for
        poster username.
        """
        cleaned_data = super().clean()

        if cleaned_data.get("search_poster_name") and not cleaned_data.get("q"):
            cleaned_data["q"] = "*"

        return cleaned_data
