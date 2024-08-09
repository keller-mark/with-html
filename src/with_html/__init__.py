import anywidget
import traitlets

class Node:
    # The node class is used to form the tree structure.
    # It has no knowledge of the internal node values.
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
    
    def to_dict(self):
        return {
            "value": self.value.to_dict() if isinstance(self.value, FunctionComponent) else self.value,
            "children": [child.to_dict() for child in self.children]
        }
    

class FunctionComponent:
    def __init__(self, value, *args, **kwargs):
        self.value = value
        self.text_content = args
        self.props = kwargs

    def is_leaf(self):
        # Is this a function component? Otherwise, it is an html tag.
        return isinstance(self.value, str)
    
    def value_is_func(self):
        if not isinstance(self.value, str) and not isinstance(self.value, list) and self.value is not None and not isinstance(self.value, anywidget.AnyWidget):
            return True
        return False

    def render(self, ctx):
        if self.value_is_func():
            self.value(ctx)

    def __repr__(self):
        value_str = str(self.value)
        if self.value_is_func():
            value_str = f"FunctionComponent.{self.value.__name__}"
        return f"<{value_str} {self.props}>{self.text_content}"
    
    def to_dict(self):
        return {
            "tag": self.value if not self.value_is_func() and not isinstance(self.value, anywidget.AnyWidget) else None,
            "text_content": self.text_content,
            "props": self.props,
            "model_id": self.value.model_id if isinstance(self.value, anywidget.AnyWidget) else None,

            # TODO: convert style keys to camelCase if present?
            # TODO: convert class_name to className?
            # TODO: convert callbacks to anywidget.experimental.invoke command references?
            # TODO: convert html_for to htmlFor?
            # TODO: convert aria_ to aria-?
        }

class NodeContextMeta(type):
    def __getattr__(cls, key):
        # __getattr__ only gets called for attributes that don't actually exist
        if key in {"div", "span", "h1", "h2", "h3", "h4", "h5", "h6", "p", "a", "img", "button", "input", "form", "label", "ul", "ol", "li", "nav", "header", "footer", "section", "article", "aside", "main", "figure", "figcaption", "blockquote", "pre", "code", "table", "tr", "th", "td", "thead", "tbody", "tfoot", "caption", "colgroup", "col", "style", "script", "noscript", "meta", "link", "title", "head", "body", "html"}:
            def node_context_wrapper(*args, **kwargs):
                return cls.html_tag(key, *args, **kwargs)
            return node_context_wrapper
        
        raise AttributeError(f"'NodeContext' object has no attribute '{key}'")


def create_root():
    class NodeContext(metaclass=NodeContextMeta):
        root = Node(None, None)
        curr_node = root

        potential_self_closing = []

        def __init__(self, value, *args, **kwargs):
            rc = FunctionComponent(value, *args, **kwargs)
            self.node = Node(rc, NodeContext.curr_node)

            NodeContext.potential_self_closing.append(self)

            self.was_entered = False
        
        @staticmethod
        def html_tag(tag, *args, **kwargs):
            return NodeContext(tag, *args, **kwargs)
        
        def pop_self_closing(self):
            for node_ctx in NodeContext.potential_self_closing[::-1]:
                if not node_ctx.was_entered:
                    node_ctx.enter_exit()
            NodeContext.potential_self_closing = []

        def __enter__(self):
            NodeContext.curr_node = self.node
            # TODO: If this is function component, start building up list of children to pass in?
            self.node.value.render(NodeContext)
            self.was_entered = True
            return self

        def __exit__(self, *args):
            self.pop_self_closing()
            # If this is a function component, do we need to append the node? Or just render it differently?
            # If this is a function component, render and pass in children nodes?
            self.node.parent.children.append(self.node)
            NodeContext.curr_node = self.node.parent

            return False

        def enter_exit(self):
            self.__enter__()
            self.__exit__()
            return self

    return NodeContext

class RootWidget(anywidget.AnyWidget):
    _esm = """
    import { importWithMap } from 'https://unpkg.com/dynamic-importmap@0.1.0';
    const importMap = {
    imports: {
        "react": "https://esm.sh/react@18.2.0?dev",
        "react-dom": "https://esm.sh/react-dom@18.2.0?dev",
        "react-dom/client": "https://esm.sh/react-dom@18.2.0/client?dev",
    },
    };

    const React = await importWithMap("react", importMap);
    const { createRoot } = await importWithMap("react-dom/client", importMap);

    const e = React.createElement;


    async function render(ctx) {
        const _html = ctx.model.get("_html");
        console.log(_html);

        function App(props) {
            const { node } = props;
            const { value, children } = node;
            const hasChildren = Array.isArray(children) && children.length > 0;
            const hasText = value?.text_content?.length === 1;

            const elRef = React.useRef();

            React.useEffect(() => {
                if(node && value?.model_id) {
                    async function renderWidget() {
                        // Create a dom node to provide as the el.
                        // Get the widget's model
                        const model = await ctx.model.widget_manager.get_model(value.model_id);
                        console.log(model);
                        const _esm = model.get("_esm");
                        const _css = model.get("_css");

                        const url = URL.createObjectURL(new Blob([_esm], { type: "text/javascript" }));
                        const mod = await import(url);
                        URL.revokeObjectURL(url);
                        const widget = typeof mod.default === "function" ? await mod.default() : mod.default;

                        const subInvoke = async () => { 
                            // TODO: call the global invoke method with an extra scoping key
                            // to enable de-multiplexing on the python side.
                        };
                        const subCtx = { model, el: elRef.current, experimental: { invoke: subInvoke } };

                        // TODO: use shadow DOM to insert CSS? or just use react to insert into a <style> tag?
                        // However React-inserted styles seem to not have an effect on the DOM nodes
                        // that get inserted into the provided `el` using vanilla JS in the render() function.
                        // Another option could be to require the widget to provide a react component (instead of a render function).
                        
                        const cleanup = await widget.render(subCtx);
                        // TODO: use the cleanup in the effect cleanup
                    }
                    renderWidget();
                }
                // TODO: return an effect cleanup function.
            }, [elRef]);

            if(node) {
                if(value?.model_id) {
                    return e(
                        "div",
                        { ref: elRef },
                        // TODO: is there a use case for children here?
                    );
                }

                return e(
                    value?.tag ?? React.Fragment,
                    value?.props ?? {},
                    (hasChildren ? children.map(child => e(App, { node: child })) : (
                        hasText ? value.text_content[0] : null
                    ))
                );
            }
            return null;
        }

        const root = createRoot(ctx.el);
        root.render(e(App, { node: _html }));

        return () => {
            // Clean up React and DOM state.
            root.unmount();
        };
    }
    export default { render };
    """

    def __init__(self, root):
        self.root = root

        html_trait = traitlets.Dict(self.root.to_dict()).tag(sync=True)

        self.add_traits(_html=html_trait)
        super().__init__()