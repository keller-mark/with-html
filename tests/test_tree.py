import pytest

from with_html import create_root

def test_tree_creation():

    h = create_root()

    with h("child1"):
        h("child1.1")
        h("child1.2")
    with h("child2"):
        h("child2.1")
        with h("child2.2"):
            h("child2.2.1")
            h("child2.2.2")

    # TODO: dont test the string, test the tree structure
    tree_str = str(h.root)
    
    assert tree_str == """
root
    <child1 {}>()
        <child1.1 {}>()
        <child1.2 {}>()
    <child2 {}>()
        <child2.1 {}>()
        <child2.2 {}>()
            <child2.2.1 {}>()
            <child2.2.2 {}>()
""".strip()

def test_convenience_funcs():

    h = create_root()

    with h.div():
        h.img(src="test.jpg")
        h.p("my paragraph")
    with h("child2"):
        h("child2.1")
        with h("child2.2"):
            h("child2.2.1")
            h.pre("child2.2.2")

    # TODO: dont test the string, test the tree structure
    tree_str = str(h.root)

    print(tree_str)
    
    assert tree_str == """
root
    <div {}>()
        <img {'src': 'test.jpg'}>()
        <p {}>('my paragraph',)
    <child2 {}>()
        <child2.1 {}>()
        <child2.2 {}>()
            <child2.2.1 {}>()
            <pre {}>('child2.2.2',)
""".strip()

def test_components():
    
    h = create_root()

    def my_button(h):
        h.button("submit")

    with h.div():
        h.img(src="test.jpg")
        h.p("my paragraph")
        h(my_button)
        h.p("another paragraph")
    
    tree_str = str(h.root)

    print(tree_str)

    assert tree_str == """
root
    <div {}>()
        <img {'src': 'test.jpg'}>()
        <p {}>('my paragraph',)
        <FunctionComponent.my_button {}>()
            <button {}>('submit',)
        <p {}>('another paragraph',)
""".strip()