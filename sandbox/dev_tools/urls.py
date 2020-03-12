"""URLs for the dev_tools django application."""
from django.conf.urls import url
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(
        r"^$",
        RedirectView.as_view(
            url=reverse_lazy("dev_tools.views.consumer"), permanent=False
        ),
    ),
    url(r"^consumer$", views.dev_consumer, name="dev_tools.views.consumer"),
]

#
#
