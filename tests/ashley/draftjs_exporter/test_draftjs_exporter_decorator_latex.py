from django.test import TestCase
from draftjs_exporter.dom import DOM

from ashley.editor.decorators import inlinetex, render_children


class TestInlinetexDecorator(TestCase):
    """Test custom inlinetex decorator for draftjs_exporter"""

    def test_custom_decorator_inlinetex_ok(self):
        """
        check custom decorator ‘inlinetex‘ returns expected html
        """

        tex = "\left.\frac{x^3}{3}\right|_0^1"  # noqa: W605
        self.assertEqual(
            DOM.render(DOM.create_element(inlinetex, {"tex": tex})),
            f'<span class="ashley-latex-inline">{tex}</span>',
        )

    def test_custom_decorator_inlinetex_empty(self):
        """
        check custom decorator ‘inlinetex‘ returns expected html even when
        the content is empty
        """
        self.assertEqual(
            DOM.render(DOM.create_element(inlinetex, {"tex": ""})),
            '<span class="ashley-latex-inline"></span>',
        )

    def test_custom_decorator_inlinetex_no_maths(self):
        """
        check custom decorator ‘inlinetex‘ returns expected html even when
        the content is not a formula but a regular string
        """
        self.assertEqual(
            DOM.render(DOM.create_element(inlinetex, {"tex": "a common string"})),
            '<span class="ashley-latex-inline">a common string</span>',
        )

    def test_custom_decorator_displaytex_ok(self):
        """
        check custom decorator for `render_children` of tex returns expected html
        """

        tex = "\left.\frac{x^3}{3}\right|_0^1"  # noqa: W605

        self.assertEqual(
            DOM.render(
                DOM.create_element(
                    render_children,
                    {
                        "block": {
                            "key": "a215p",
                            "text": "",
                            "type": "atomic",
                            "data": {"tex": tex, "type": "TEXBLOCK"},
                        }
                    },
                )
            ),
            f'<span class="ashley-latex-display">{tex}</span>',
        )

    def test_custom_decorator_displaytex_empty(self):
        """
        check custom decorator `render_children` returns expected html even when
        the content is empty
        """
        self.assertEqual(
            DOM.render(
                DOM.create_element(
                    render_children,
                    {
                        "block": {
                            "key": "a215p",
                            "text": "",
                            "type": "atomic",
                            "data": {"tex": "", "type": "TEXBLOCK"},
                        }
                    },
                )
            ),
            '<span class="ashley-latex-display"></span>',
        )

    def test_custom_decorator_displaytex_no_maths(self):
        """
        check custom decorator `render_children` returns expected html even when
        the content is not a formula but a regular string
        """
        self.assertEqual(
            DOM.render(
                DOM.create_element(
                    render_children,
                    {
                        "block": {
                            "key": "a215p",
                            "text": "",
                            "type": "atomic",
                            "data": {"tex": "a common string", "type": "TEXBLOCK"},
                        }
                    },
                )
            ),
            '<span class="ashley-latex-display">a common string</span>',
        )

    def test_custom_decorator_displaytex_no_malformed(self):
        """
        check custom decorator `render_children` returns expected html even when
        the `tex` attribute is missing
        """
        self.assertEqual(
            DOM.render(
                DOM.create_element(
                    render_children,
                    {
                        "block": {
                            "key": "a215p",
                            "text": "",
                            "type": "atomic",
                            "data": {"type": "TEXBLOCK"},
                        }
                    },
                )
            ),
            '<span class="ashley-latex-display"></span>',
        )
