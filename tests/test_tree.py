import pytest

from with_html import create_root

def test_tree_creation():

    h = create_root()

    with h("child1"):
        h("child1.1")()
        h("child1.2")()
    with h("child2"):
        h("child2.1")()
        with h("child2.2"):
            h("child2.2.1")()
            h("child2.2.2")()

    tree_str = str(h.root)
    
    assert tree_str == """
todo
"""
    