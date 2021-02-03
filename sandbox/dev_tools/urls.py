"""URLs for the dev_tools django application."""
from django.urls import re_path, reverse_lazy
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    re_path(
        r"^$",
        RedirectView.as_view(
            url=reverse_lazy("dev_tools.views.consumer"), permanent=False
        ),
    ),
    re_path(r"^consumer$", views.dev_consumer, name="dev_tools.views.consumer"),
]

#
#
