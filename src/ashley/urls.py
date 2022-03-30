"""
Ashley URLs (that includes django machina urls)
"""

from django.urls import include, path
from machina import urls as machina_urls

from ashley.api import urls as api_urls
from ashley.views import ChangeUsernameView, ForumLTIView, ManageModeratorsView

API_PREFIX = "v1.0"

urlpatterns = [
    path("lti/forum/<uuid:uuid>", ForumLTIView.as_view(), name="forum.lti.view"),
    path(
        "profile/username",
        ChangeUsernameView.as_view(),
        name="forum.username.change",
    ),
    path("moderators/", ManageModeratorsView.as_view(), name="moderators"),
    path(f"api/{API_PREFIX:s}/", include(api_urls)),
    path("forum/", include(machina_urls)),
]
