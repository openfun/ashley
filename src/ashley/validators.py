"""Validators for the ashley application."""
from html.parser import HTMLParser

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from machina.models.fields import render_func


class MarkupNullableMaxLengthValidator(validators.MaxLengthValidator):
    """
    Ensure that the length of the plain text contained in a markup is lower than
    or equal the specified max length. Also, it provides a way to not validate
    an input if the max length is None.
    """

    def __call__(self, value):
        if self.limit_value is None:
            # If the limit value is None, this means that there is no
            # limit value at all. The default validation process is not
            # performed.
            return
        # Render the value to HTML using MACHINA_MARKUP_LANGUAGE
        html_value = render_func(value)
        # Extract plain text from html
        html_parser = HTMLFilter()
        html_parser.feed(html_value)
        # Validate the extracted text length
        super().__call__(html_parser.text)


class HTMLFilter(HTMLParser):
    """HTML parser to extract plain text from a HTML fragment."""

    text = ""

    def error(self, message):
        """Ignore errors"""

    def handle_data(self, data):
        """Concatenate the plain text found in each element."""
        self.text += data


def validate_upload_image_file_size(file):
    """Controls the size of the uploaded file is not over the limit authorized"""
    if file.size > settings.MAX_UPLOAD_FILE_MB * 1024 * 1024:
        raise ValidationError(
            _(
                f"The maximum file size that can be uploaded is {settings.MAX_UPLOAD_FILE_MB} MB"
            )
        )
    return file
