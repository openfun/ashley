"""
ashley URLs
"""
from django.contrib import admin
from django.urls import include, path
from machina import urls as machina_urls

from lti_provider import urls as lti_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("forum/", include(machina_urls)),
    path("lti/", include(lti_urls)),
]
