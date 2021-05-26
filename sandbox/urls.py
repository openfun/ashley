"""
ashley URLs
"""
from dev_tools import urls as dev_urls
from dev_tools.apps import DevToolsAppConfig
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from ashley import urls as ashley_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(ashley_urls)),
]
if DevToolsAppConfig.name in settings.INSTALLED_APPS:
    urlpatterns += [path("dev/", include(dev_urls))] + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
