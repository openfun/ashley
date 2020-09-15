"""Test suite for ashley validators"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from ashley.validators import MarkupNullableMaxLengthValidator


class TestMarkupNullableMaxLengthValidator(TestCase):
    """Test the MarkupNullableMaxLengthValidator validator class"""

    # pylint: disable=no-self-use
    def test_none_limit(self):
        """The validator should not raise any exception if the defined limit is None."""
        validator = MarkupNullableMaxLengthValidator(None)
        validator("")

    def test_limit_ok(self):
        """The validator should not raise any exception if the text contained in the
        Draft.js markup is lower than or equal to the defined limit."""

        # This the representation of "**Test** :boom:" (test in bold and boom emoji)
        # in DraftJS markup.
        draftjs_markup = (
            '{"blocks":[{"key":"4h6tb","text":"Test 💥","type":"unstyled","depth":0,'
            '"inlineStyleRanges":[{"offset":0,"length":5,"style":"BOLD"}],"entityRanges":'
            '[{"offset":5,"length":1,"key":0}],"data":{}}],"entityMap":{"0":{"type":"emoji",'
            '"mutability":"IMMUTABLE","data":{"emojiUnicode":"💥"}}}}'
        )
        MarkupNullableMaxLengthValidator(255)(draftjs_markup)
        MarkupNullableMaxLengthValidator(6)(draftjs_markup)
        with self.assertRaises(ValidationError):
            MarkupNullableMaxLengthValidator(5)(draftjs_markup)
