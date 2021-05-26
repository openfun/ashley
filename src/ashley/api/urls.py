"""Ashley API URLs"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ImageUploadApiView, UserApiView

router = DefaultRouter()
router.register(
    "users",
    UserApiView,
    basename="users",
)
router.register(
    "images",
    ImageUploadApiView,
    basename="images",
)

urlpatterns = [
    path("", include(router.urls)),
]
