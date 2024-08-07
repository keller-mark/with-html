# with-html

[![PyPI](https://img.shields.io/pypi/v/with_html)](https://pypi.org/project/with_html)

(Ab)use of context managers.

## Installation

```sh
pip install with_html
```

## Usage


```python
from with_html import create_root, RootWidget

h = create_root()

def my_button(h):
    h.button("submit")

with h.div():
    h.h1("Test")
    h.img(src="https://example.com/my_image.jpg", width=200, height=200)
    h.p("my paragraph")
    h(my_button)
    h.p("another paragraph")
    with h.table(style=dict(border="1px solid red")):
        with h.tr():
            h.th("Column 1")
            h.th("Column 2")
        with h.tr():
            h.td("Value 1")
            h.td("Value 2")

w = RootWidget(h.root)
w
```



## Development

```sh
conda create -n with-html python=3.12
conda activate with-html
pip install -e ".[dev]"
```

```sh
jupyter lab
```
