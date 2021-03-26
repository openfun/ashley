"""Serializer for ashley api."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from ashley.context_mixins import get_current_lti_session
from ashley.defaults import (
    _FORUM_ROLE_INSTRUCTOR,
    _FORUM_ROLE_MODERATOR,
    _FORUM_ROLE_STUDENT,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "public_username", "role"]
        read_only_fields = ["public_username", "role"]

    def get_role(self, obj):
        """Describes the role of the user"""
        lti_session = get_current_lti_session(self.context.get("request"))
        student_group = lti_session.get_group_role_name(_FORUM_ROLE_STUDENT)
        moderator_group = lti_session.get_group_role_name(_FORUM_ROLE_MODERATOR)
        user_groups = list(obj.groups.values_list("name", flat=True))

        if obj.is_active:

            if student_group in user_groups and moderator_group not in user_groups:
                return _FORUM_ROLE_STUDENT

            if student_group in user_groups and moderator_group in user_groups:
                return _FORUM_ROLE_MODERATOR

            if obj.groups.filter(
                name=lti_session.get_group_role_name(_FORUM_ROLE_INSTRUCTOR)
            ):
                return _FORUM_ROLE_INSTRUCTOR

        return None
