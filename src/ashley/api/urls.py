"""Ashley API URLs"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserApiView

router = DefaultRouter()
router.register(
    "users",
    UserApiView,
    basename="users",
)

urlpatterns = [
    path("", include(router.urls)),
]
