"""
ashley URLs
"""
from django.contrib import admin
from django.urls import include, path

from lti_provider import urls as lti_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lti/", include(lti_urls)),
]
