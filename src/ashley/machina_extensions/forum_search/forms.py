"""
    Forum search forms
    ==================
    This module defines forms provided by the ``forum_search`` application.
"""

from machina.apps.forum_search.forms import SearchForm as MachinaSearchForm


class SearchForm(MachinaSearchForm):
    """
    Override Django Machina's SearchForm to allow searching poster user names
    even with an empty search in the main field.
    """

    def clean(self):
        """
        Set main query to catch all "*" if it is empty and there is a search term for
        poster username.
        """
        cleaned_data = super().clean()

        if cleaned_data.get("search_poster_name") and not cleaned_data.get("q"):
            cleaned_data["q"] = "*"

        return cleaned_data
