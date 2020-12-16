"""
Ashley URLs (that includes django machina urls)
"""

from django.urls import include, path
from machina import urls as machina_urls

from ashley.views import ChangeUsernameView, ForumLTIView

urlpatterns = [
    path("lti/forum/<uuid:uuid>", ForumLTIView.as_view(), name="forum.lti.view"),
    path(
        "profile/username",
        ChangeUsernameView.as_view(),
        name="forum.username.change",
    ),
    path("forum/", include(machina_urls)),
]
