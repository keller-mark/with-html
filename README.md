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

with h("div", style=dict(margin_top=10)):
    h("p", "this is a string in a paragraph")()
    h("span", "contents of the span")
with h("div"):
    h("img", src="http://example.com/image.png")()
print(h.root)

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
