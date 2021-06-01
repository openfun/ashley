"""
This module defines URL patterns associated with the django-machina``forum``
application.
"""

from django.urls import path
from machina.apps.forum.urls import (
    ForumURLPatternsFactory as BaseForumURLPatternsFactory,
)
from machina.core.loading import get_class


class ForumURLPatternsFactory(BaseForumURLPatternsFactory):
    """Allows to generate the URL patterns of the ``forum`` application."""

    rename_view = get_class("forum.views", "ForumRenameView")
    archive_view = get_class("forum.views", "ForumArchiveView")

    def get_urlpatterns(self):
        """Returns the URL patterns managed by the considered factory / application."""

        return super().get_urlpatterns() + [
            path("admin/rename/<int:pk>/", self.rename_view.as_view(), name="rename"),
            path(
                "admin/archive/<int:pk>/", self.archive_view.as_view(), name="archive"
            ),
        ]


urlpatterns_factory = ForumURLPatternsFactory()
