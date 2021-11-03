"""
    Forum search forms
    ==================
    This module defines forms provided by the ``forum_search`` application.
"""
from machina.apps.forum_search.forms import SearchForm as MachinaSearchForm
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model("forum", "Forum")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")


class SearchForm(MachinaSearchForm):
    """
    Override Django Machina's SearchForm to allow searching poster user names
    even with an empty search in the main field.
    """

    def __init__(self, *args, **kwargs):
        """
        Init form, code based on base class MachinaSearchForm. A filter on lti_context
        has been added.
        """
        # Loads current lti_context to filter forum search
        lti_contexts = kwargs.pop("lti_context", None)
        super().__init__(*args, **kwargs)
        user = kwargs.pop("user", None)
        self.allowed_forums = PermissionHandler().get_readable_forums(
            Forum.objects.filter(archived=False, lti_contexts=lti_contexts), user
        )
        # self.allowed_forums is used in search method of MachinaSearchForm
        if self.allowed_forums:
            self.fields["search_forums"].choices = [
                (f.id, "{} {}".format("-" * f.margin_level, f.name))
                for f in self.allowed_forums
            ]

    def clean(self):
        """
        Set main query to catch all "*" if it is empty and there is a search term for
        poster username.
        """
        cleaned_data = super().clean()

        if cleaned_data.get("search_poster_name") and not cleaned_data.get("q"):
            cleaned_data["q"] = "*"

        return cleaned_data
