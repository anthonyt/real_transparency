import os
from genshi import XML
from pylons import config, request, tmpl_context
from pylons.templating import render_genshi as render
from pylons.decorators import jsonify

__all__ = ['expose', 'expose_xhr']

_func_attrs = [
    # Attributes that define useful information or context for functions
    '__dict__', '__doc__', '__name__', 'im_class', 'im_func', 'im_self',
    'template', 'exposed' # custom attribute to allow web access
]

def _copy_func_attrs(f1, f2):
    """Copy relevant attributes from f1 to f2

    TODO: maybe replace this with the use of functools.wraps
    http://docs.python.org/library/functools.html#functools.wraps
    """

    for x in _func_attrs:
        if hasattr(f1, x):
            setattr(f2, x, getattr(f1, x))

def _get_func_attrs(f):
    """Return a dict of attributes. Used for debugging."""
    result = {}
    for x in _func_attrs:
        result[x] = getattr(f, x, (None,))
    return result

def _expose_wrapper(f, template):
    """Returns a function that will render the passed in function according
    to the passed in template"""
    f.exposed = True
    f.template = template

    if template == "json":
        return jsonify(f)
    elif template == "string":
        return f
    def wrapped_f(*args, **kwargs):
        result = f(*args, **kwargs)
        extra_vars = {
            # Steal a page from TurboGears' book:
            # include the genshi XML helper for convenience in templates.
            'XML': XML
        }
        # If the provided template path isn't absolute (ie, doesn't start with
        # a '/'), then prepend the default search path. By providing the
        # template path to genshi as an absolute path, we invoke different
        # rules for the resolution of 'xi:include' paths in the template.
        # See http://genshi.edgewall.org/browser/trunk/genshi/template/loader.py#L178
        if not template.startswith('/'):
            tmpl = os.path.join(config['genshi_search_path'], template)
        else:
            tmpl = template
        extra_vars.update(result)
        return render(tmpl, extra_vars=extra_vars)
    return wrapped_f

def expose(template='string'):
    """Simple expose decorator for controller actions.

    Transparently wraps a method in a function that will render the method's
    return value with the given template.

    Sets the 'exposed' and 'template' attributes of the wrapped method,
    marking it as safe to be accessed via HTTP request.

    :Usage:

    Example, using a genshi template::

        class MyController(BaseController):

            @expose('path/to/template.html')
            def sample_action(self, *args):
                # do something
                return dict(message='Hello World!')

    :param template:
        One of:
            * The path to a genshi template, relative to the project's
              template directory
            * 'string'
            * 'json'
    :type template: string or unicode

    """
    def wrap(f):
        wrapped_f = _expose_wrapper(f, template)
        _copy_func_attrs(f, wrapped_f)
        return wrapped_f
    return wrap

def expose_xhr(template_norm='', template_xhr='json'):
    """
    Expose different templates for normal vs XMLHttpRequest requests.

    :Usage:

    Example, using two genshi templates:

        class MyController(BaseController):

            @expose_xhr('items/main_list.html', 'items/ajax_list.html')
            def sample_action(self, *args):
                # do something
                return dict(items=get_items_list())
    """
    def wrap(f):
        norm = _expose_wrapper(f, template_norm)
        xhr = _expose_wrapper(f, template_xhr)

        def choose(*args, **kwargs):
            if request.is_xhr:
                return xhr(*args, **kwargs)
            else:
                return norm(*args, **kwargs)
        _copy_func_attrs(f, choose)
        return choose
    return wrap

