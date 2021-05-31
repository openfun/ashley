from django.test import TestCase
from draftjs_exporter.dom import DOM

from ashley.editor.decorators import image


class TestImageDecorator(TestCase):
    """Test custom ‘image‘ decorator for draftjs_exporter"""

    def test_custom_decorator_image_default_param(self):
        """
        check custom decorator ‘image‘ returns expected html
        """
        self.assertEqual(
            DOM.render(DOM.create_element(image, {})),
            "",
        )

    def test_custom_decorator_image_with_params(self):
        """
        check custom decorator ‘image‘ returns expected html with
        parameters
        """
        self.assertEqual(
            DOM.render(
                DOM.create_element(
                    image,
                    {
                        "src": "test.png",
                        "alignment": "center",
                        "width": 80,
                        "height": 70,
                    },
                )
            ),
            '<img class="image-center" src="test.png" width="80%" height="70%"/>',
        )

    def test_custom_decorator_image_alignment_left(self):
        """
        check custom decorator ‘image‘ returns expected html with
        different alignment value to left
        """
        self.assertEqual(
            DOM.render(
                DOM.create_element(image, {"src": "test.png", "alignment": "left"})
            ),
            '<img class="float-left" src="test.png" width="40%" height="auto"/>',
        )

    def test_custom_decorator_image_alignment_right(self):
        """
        check custom decorator ‘image‘ returns expected html with
        different alignment value to right
        """
        self.assertEqual(
            DOM.render(
                DOM.create_element(image, {"src": "test.png", "alignment": "right"})
            ),
            '<img class="float-right" src="test.png" width="40%" height="auto"/>',
        )
