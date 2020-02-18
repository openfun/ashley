"""
ashley URLs
"""
from django.contrib import admin
from django.urls import include, path
from machina import urls as machina_urls

urlpatterns = [
    path("forum/", include(machina_urls)),
    path("admin/", admin.site.urls),
]
