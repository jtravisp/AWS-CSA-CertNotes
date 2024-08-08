class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
        # tag - A string representing the HTML tag name (e.g. "p", "a", "h1", etc.)
        # value - A string representing the value of the HTML tag (e.g. the text inside a paragraph)
        # children - A list of HTMLNode objects representing the children of this node
        # props - A dictionary of key-value pairs representing the attributes of the HTML tag. For example, a link (<a> tag) might have {"href": "https://www.google.com"}

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if not self.props:
            return ""
        return " " + " ".join(f'{key}="{value}"' for key, value in self.props.items())

    def __repr__(self):
        return (f"HTMLNode(tag={self.tag!r}, value={self.value!r}, "
                f"children={self.children!r}, props={self.props!r})")
        # Give yourself a way to print an HTMLNode object and see its tag, value, children, and props. This will be useful for your debugging.

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, children=None, props=props)
        if self.children is not None:
            raise ValueError("LeafNode cannot have children")

    def to_html(self):
        if self.tag is None:
            return self.value
        if self.value is None:
            raise ValueError("All LeafNodes must have a value")
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

# Example usage:
# leaf = LeafNode(tag="img", value="", props={"src": "image.png", "alt": "An image"})
# print(leaf)
# def main():
    # object = TextNode('This is a text node', 'bold', 'https://www.boot.dev')
    # print(object)
    # Create a main() function that creates a new TextNode object with some dummy values. Print the object, and make sure it looks like you'd expect. For example, my code printed:
    # TextNode(This is a text node, bold, https://www.boot.dev)

# if __name__ == '__main__':
    # main()
