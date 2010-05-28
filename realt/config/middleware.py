"""Pylons middleware initialization"""
from beaker.middleware import SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from repoze.tm import make_tm
from routes.middleware import RoutesMiddleware

from realt.config.environment import load_environment
from realt.model.meta import Session

class DBSessionRemoverMiddleware(object):
    """Ensure the contextual session ends at the end of the request."""
    def __init__(self, app, session=None):
        self.app = app
        self.session = session

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        finally:
            self.session.remove()

def transaction_commit_veto(environ, status, headers):
    """Veto the commit if the response's status code is an error code.

    This hook is called by repoze.tm in case we want to veto a commit
    for some reason. Return True to force a rollback.
    """
    return not 200 <= int(status.split(None, 1)[0]) < 400

def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    config = load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp(config=config)

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'], singleton=False)
    app = SessionMiddleware(app, config)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    # Add transaction management
    app = make_tm(app, transaction_commit_veto)
    app = DBSessionRemoverMiddleware(app, Session)

    # END CUSTOM MIDDLEWARE

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'])
        app = Cascade([static_app, app])
    app.config = config
    return app
