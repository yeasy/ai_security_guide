import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("reader", ROOT / "tools/build_html_reader.py")
READER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(READER)


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class DiagramZoomTests(unittest.TestCase):
    def figure(self, svg, index):
        # The old renderer has no zoom entry; keep the red phase semantic.
        render = getattr(READER, "diagram_figure", lambda s, i: f'<figure class="diagram">{s}</figure>')
        return render(svg, index)

    def test_each_diagram_has_keyboard_operable_control_and_one_svg(self):
        markup = "".join(self.figure('<svg viewBox="0 0 1216 1540"><text>步骤</text></svg>', i) for i in (0, 1))
        tags = Elements(markup).tags
        inputs = [a for t, a in tags if t == "input"]
        self.assertEqual(len(inputs), 2)
        self.assertEqual(len({a["id"] for a in inputs}), 2)
        labels = [a for t, a in tags if t == "label"]
        regions = {a.get("id") for t, a in tags if t == "div"}
        for control in inputs:
            self.assertEqual(control["type"], "checkbox")
            self.assertIn(control["aria-controls"], regions)
            self.assertIn(control["id"], [a.get("for") for a in labels])
        self.assertEqual(sum(t == "svg" for t, _ in tags), 2)
        self.assertIn("1216px", markup)
        self.assertNotIn("onclick", markup)

    def test_intrinsic_width_is_numeric_and_untrusted_attribute_cannot_be_css(self):
        markup = self.figure('<svg viewBox="0 0 expression(alert(1)) 500"></svg>', 3)
        self.assertIn("--diagram-width:960px", markup)
        self.assertNotIn("--diagram-width:expression", markup)

    def test_static_images_have_a_zoom_entry_without_duplicate_image(self):
        source = '<p><img src="data:image/svg+xml;base64,fixture" alt="架构"></p>'
        wrap = getattr(READER, "zoom_images", lambda value: value)
        markup = wrap(source)
        tags = Elements(markup).tags
        self.assertEqual(sum(t == "img" for t, _ in tags), 1)
        self.assertEqual(sum(t == "input" for t, _ in tags), 1)
        self.assertIn("放大查看", markup)


class LinkedImageTests(unittest.TestCase):
    def test_images_inside_links_are_left_alone(self):
        html = '<p><a href="https://example.test"><img src="badge.svg" alt="b"></a> <img src="fig.png" alt="f"></p>'
        out = READER.zoom_images(html)
        self.assertIn('<a href="https://example.test"><img src="badge.svg" alt="b"></a>', out)
        self.assertEqual(out.count('<img'), 2)
        self.assertIn('image-0', out)
        self.assertNotIn('image-1', out)  # only the unlinked image got a zoom control


if __name__ == "__main__":
    unittest.main()
