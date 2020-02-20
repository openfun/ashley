"""URLs for the lti_provider django application."""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^launch$", views.launch, name="lti_provider.views.launch"),
]
