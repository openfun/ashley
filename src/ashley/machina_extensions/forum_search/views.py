"""
    Forum search views
    ==================

    This module defines views provided by the ``forum_search`` application.

"""
from haystack import views

from ashley.context_mixins import get_current_lti_session


class FacetedSearchView(views.FacetedSearchView):
    """View to show search results"""

    template = "forum_search/search.html"

    def build_form(self, form_kwargs=None):
        form = super().build_form(
            form_kwargs={
                "user": self.request.user,
                "lti_context": get_current_lti_session(self.request),
            }
        )
        return form
