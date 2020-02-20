"""
ashley URLs
"""
from django.contrib import admin
from django.urls import include, path
from machina import urls as machina_urls

from fun_lti_provider import urls as lti_urls

urlpatterns = [
    path("forum/", include(machina_urls)),
    path("admin/", admin.site.urls),
    path("lti/", include(lti_urls)),
]
