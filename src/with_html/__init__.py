class Node:
    def __init__(self, value, parent):
        self.value = value
        self.parent = parent
        self.children = []

    def indented(self, n=0):
        return ("\n" if n > 0 else "") + ("    " * n) + str(self.value) + "".join([
            child.indented(n+1) for child in self.children
        ])

    def __str__(self):
        return self.indented()

    def __repr__(self):
        return self.indented()

class ReactComponent:

    def __init__(self, value, *args, **kwargs):
        self.value = value
        self.text_content = args
        self.props = kwargs

    def is_leaf(self):
        # Is this a function component? Otherwise, it is an html tag.
        return isinstance(self.value, str)

    def render(self):
        if not isinstance(self.value, str) and not isinstance(self.value, list) and self.value is not None:
            self.value()

    def __repr__(self):
        return f"<{self.value} {self.props}>{self.text_content}"

def create_root():
    class NodeContext:
        root = Node("root", None)
        curr_node = root

        def __init__(self, value, *args, **kwargs):
            rc = ReactComponent(value, *args, **kwargs)
            # If this is function component, start building up list of children to pass in.
            rc.render()
            self.node = Node(rc, NodeContext.curr_node)

        def __enter__(self):
            NodeContext.curr_node = self.node
            return self

        def __exit__(self, *exc):
            # If this is a function component, do we need to append the node? Or just render it differently?
            # If this is a function component, render and pass in children nodes?

            self.node.parent.children.append(self.node)
            NodeContext.curr_node = self.node.parent

            return False

        def __call__(self):
            self.__enter__()
            self.__exit__()
            return self

    return NodeContext