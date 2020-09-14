"""Forms definition for the dev_tools application."""

from django import forms
from django.utils.translation import gettext_lazy as _

from lti_provider.models import LTIPassport


class PassportChoiceField(forms.ModelChoiceField):
    """Select a LTI password"""

    def label_from_instance(self, obj):
        return f"{obj.consumer.slug} - {obj.title}"


class LTIConsumerForm(forms.Form):
    """Form to configure the standalone LTI consumer."""

    passport = PassportChoiceField(
        queryset=LTIPassport.objects.all(), empty_label=None, label="Consumer"
    )

    user_id = forms.CharField(
        label="User ID",
        max_length=100,
        initial="jojo",
    )

    course_id = forms.CharField(
        label="Course ID",
        max_length=100,
        initial="course-v1:openfun+mathematics101+session01",
    )
    course_title = forms.CharField(
        label="Course Title", max_length=100, initial="Mathematics 101"
    )

    role = forms.ChoiceField(
        choices=(
            ("Student", _("Student")),
            ("Instructor", _("Instructor")),
        )
    )

    presentation_locale = forms.ChoiceField(
        choices=(("fr", "fr"), ("en", "en"), ("", "--none--")),
        initial="fr",
        required=False,
    )
