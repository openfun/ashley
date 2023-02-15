import json

from django.test import TestCase

from ashley.editor import draftjs_renderer


class TestDraftJsRenderer(TestCase):
    """Test draftjs_renderer method used to render draftjs content"""

    def test_draftjs_renderer_valid_json(self):
        """draftjs_renderer should return valid html"""
        content = {
            "entityMap": {},
            "blocks": [
                {
                    "key": "d1d87",
                    "text": "Hello, world!",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {},
                }
            ],
        }
        result = draftjs_renderer(json.dumps(content))
        self.assertEqual("<p>Hello, world!</p>", result)

    def test_draftjs_renderer_invalid_json(self):
        """draftjs_renderer should return an error message if
        the input is not valid JSON"""

        # Test invalid input
        content = "not valid JSON"

        with self.assertLogs() as log:
            self.assertEqual(draftjs_renderer(content), "")

        self.assertIn("Unable to render content", log.output[0])

    def test_draftjs_renderer_inline_tex(self):
        """draftjs_renderer should render inline tex"""

        tex = r"\frac{1}{2}"
        inline_latex = {
            "blocks": [
                {
                    "key": "92d7d",
                    "text": "   ",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [{"offset": 1, "length": 1, "key": 0}],
                    "data": {},
                }
            ],
            "entityMap": {
                "0": {
                    "type": "INLINETEX",
                    "mutability": "IMMUTABLE",
                    "data": {"tex": tex, "type": "INLINETEX"},
                }
            },
        }
        expected_html = f'<p> <span class="ashley-latex-inline">{tex}</span> </p>'

        self.assertEqual(
            draftjs_renderer(json.dumps(inline_latex)),
            expected_html,
        )

    def test_draftjs_renderer_block_tex(self):
        """draftjs_renderer should render block TEXBLOCK"""
        tex = r"\frac{1}{2}"
        block_latex = {
            "blocks": [
                {
                    "key": "3f2dm",
                    "text": "",
                    "type": "atomic",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {"tex": tex, "type": "TEXBLOCK"},
                },
            ]
        }

        expected_html = f'<span class="ashley-latex-display">{tex}</span>'
        self.assertEqual(
            draftjs_renderer(json.dumps(block_latex)),
            expected_html,
        )

    def test_draftjs_renderer_atomic_mixing_render_children(self):
        """
        Check draftjs_renderer is able to render different type of atomic blocks image and tex,
        as well as inline tex and simple text
        """
        tex = r"\frac{1}{2}"
        image = "http://localhost:8090/media/image_uploads/1/1/b993e1c036f4.png"
        draftjs_json = {
            "blocks": [
                {
                    "key": "4771m",
                    "text": "Hello  ",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [{"offset": 0, "length": 5, "style": "BOLD"}],
                    "entityRanges": [{"offset": 6, "length": 1, "key": 0}],
                    "data": {},
                },
                {
                    "key": "597gj",
                    "text": "",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {},
                },
                {
                    "key": "bk58g",
                    "text": "",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {},
                },
                {
                    "key": "d55a2",
                    "text": " ",
                    "type": "atomic",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [{"offset": 0, "length": 1, "key": 1}],
                    "data": {},
                },
                {
                    "key": "erbih",
                    "text": "",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {},
                },
                {
                    "key": "2g4cm",
                    "text": "",
                    "type": "atomic",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {"tex": tex, "type": "TEXBLOCK"},
                },
                {
                    "key": "egqml",
                    "text": " ",
                    "type": "unstyled",
                    "depth": 0,
                    "inlineStyleRanges": [],
                    "entityRanges": [],
                    "data": {},
                },
            ],
            "entityMap": {
                "0": {
                    "type": "INLINETEX",
                    "mutability": "IMMUTABLE",
                    "data": {"tex": tex, "type": "INLINETEX"},
                },
                "1": {
                    "type": "IMAGE",
                    "mutability": "IMMUTABLE",
                    "data": {
                        "src": image,
                        "width": 4,
                        "height": 100,
                        "alignment": "center",
                    },
                },
            },
        }

        expected_output = (
            f'<p><strong>Hello</strong> <span class="ashley-latex-inline">{tex}</span></p><p></p>'
            f'<p></p><img class="image-center" src="{image}" width="4%" height="100%"/>'
            f'<p></p><span class="ashley-latex-display">{tex}</span><p> </p>'
        )
        self.assertEqual(
            draftjs_renderer(json.dumps(draftjs_json)),
            expected_output,
        )
