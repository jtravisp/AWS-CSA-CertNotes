import unittest

from htmlnode import HTMLNode

# Create a few nodes and make sure the props_to_html method works as expected.

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(tag="a", props={"href": "https://www.google.com"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com"')
        
    def test_props_to_html_no_props(self):
        node = HTMLNode(tag="a")
        self.assertEqual(node.props_to_html(), "")
        
    def test_props_to_html_multiple_props(self):
        node = HTMLNode(tag="a", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')
        
    def test_repr(self):
        node = HTMLNode(tag="a", value="Click here", children=[], props={"href": "https://www.google.com"})
        expected_repr = ("HTMLNode(tag='a', value='Click here', "
                         "children=[], props={'href': 'https://www.google.com'})")
        self.assertEqual(repr(node), expected_repr)

if __name__ == "__main__":
    unittest.main()
    