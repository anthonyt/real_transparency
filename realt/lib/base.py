"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons import request
from pylons.controllers import WSGIController
from realt.model.meta import Session

__all__ = ['BaseController']

class BaseController(WSGIController):

    def _perform_call(self, func, args):
        """
        _perform_call is called by _inspect_call in Pylons' WSGIController.
        """
        # Steal a page from TurboGears' book, and Add the GET/POST
        # request params to our params dict, overriding any defaults passed in.
        # XXX: This may cause a security hazard if you are relying on routes
        #      rules to validate input. Always validate args at the controller
        #      level before using!
        args.update(request.params.mixed())
        return WSGIController._perform_call(self, func, args)

    def __before__(self, *args, **kwargs):
        """This method is called before your action is.
        It should be used for setting up variables/objects, restricting access
        to other actions, or other tasks which should be executed before the
        action is called.
        """
        action = getattr(self, kwargs['action'])
        # The expose decorator sets the exposed attribute on controller
        # actions. If a method is not exposed, do not allow access to it.
        if not hasattr(action, 'exposed'):
            abort(status_code=404)
