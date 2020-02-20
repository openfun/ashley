"""URLs for the fun_lti_provider django application"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^launch$", views.launch, name="fun_lti_provider.views.launch"),
]
