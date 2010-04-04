import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from realt.lib.base import BaseController, expose
from realt.lib.parliament_xml import chamber_vote_details

log = logging.getLogger(__name__)

class XmlimportController(BaseController):

    @expose('json')
    def index(self, parliament, session, vote_number=None):
        if vote_number is not None:
            vote_number = int(vote_number)
        parliament = int(parliament)
        session = int(session)

        return dict(
            parliament = parliament,
            session = session,
            vote_number = vote_number,
        )
