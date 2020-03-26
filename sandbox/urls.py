"""
ashley URLs
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from machina import urls as machina_urls

from ashley.views import ForumLTIView

from dev_tools import urls as dev_urls
from dev_tools.apps import DevToolsAppConfig

urlpatterns = [
    path("lti/forum/<uuid:uuid>", ForumLTIView.as_view(), name="forum.lti.view"),
    path("admin/", admin.site.urls),
    path("forum/", include(machina_urls)),
]
if DevToolsAppConfig.name in settings.INSTALLED_APPS:
    urlpatterns += [path("dev/", include(dev_urls))]
