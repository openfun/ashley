from django.test import TestCase
from draftjs_exporter.dom import DOM

from ashley.editor.decorators import mention


class TestMentionDecorator(TestCase):
    """Test custom ‘mention‘ decorator for draftjs_exporter"""

    def test_custom_decorator_mention(self):
        """
        check custom decorator ‘mention‘ returns expected html
        """
        self.assertEqual(
            DOM.render(
                DOM.create_element(mention, {"mention": {"name": "Jo", "user": "3"}})
            ),
            '<a class="mention" href="/forum/member/profile/3/">'
            + '<span class="mention">@Jo</span></a>',
        )
        # Check data not valid then nothing appears
        self.assertEqual(
            DOM.render(
                DOM.create_element(mention, {"mention": {"name": "", "user": ""}})
            ),
            "",
        )

        # Check data not valid then nothing appears
        self.assertEqual(DOM.render(DOM.create_element(mention, {"mention": {}})), "")
