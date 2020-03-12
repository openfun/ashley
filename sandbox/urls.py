"""
ashley URLs
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from machina import urls as machina_urls

from lti_provider import urls as lti_urls

from dev_tools import urls as dev_urls
from dev_tools.apps import DevToolsAppConfig

urlpatterns = [
    path("admin/", admin.site.urls),
    path("forum/", include(machina_urls)),
    path("lti/", include(lti_urls)),
]

if DevToolsAppConfig.name in settings.INSTALLED_APPS:
    urlpatterns += [path("dev/", include(dev_urls))]
