"""Serializer for ashley api."""
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from rest_framework import serializers

User = get_user_model()
UploadImage = get_model("ashley", "UploadImage")


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ["id", "public_username"]
        read_only_fields = ["id", "public_username"]


class UploadImageSerializer(serializers.ModelSerializer):
    """Serializer for Image Upload model."""

    class Meta:
        model = UploadImage
        fields = (
            "id",
            "file",
            "forum",
            "poster",
        )
        extra_kwargs = {"poster": {"required": False}}
