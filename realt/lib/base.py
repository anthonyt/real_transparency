"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_genshi as render

from realt.model.meta import Session

from pylons.decorators import jsonify

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            Session.remove()


def expose(template):
    """Simple expose decorator for controller actions.

    Takes a single template argument.
    'string' for returning a simple string
    'json' for returning the json encoding of a returned dict
    any template for returning the rendered template with the local variables
        set from a returned dict
    """
    def wrap(f):
        if template == "json":
            return jsonify(f)
        elif template == "string":
            return f
        def wrapped_f(*args, **kwargs):
            result = f(*args, **kwargs)
            return render(template, extra_vars=result)
        return wrapped_f
    return wrap

