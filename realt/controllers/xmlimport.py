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

        data = self._pull_data(parliament, session, vote_number)
        return data

    def _pull_data(self, parliament, session, vote_number):
        cvds = chamber_vote_details(parliament, session, vote_number)
        results = []
        for cvd in cvds:
            results.append(dict(
                parliament = cvd.parliament,
                session = cvd.session,
                vote_number = cvd.number,
                sitting = cvd.sitting,
                description = cvd.description,
                date = cvd.date.strftime('%y-%m-%d'),
                context = cvd.context,
                sponsor = cvd.sponsor,
                decision = cvd.decision,
                related = cvd.related_bill,
                journal = cvd.journal,
                participants = cvd.participants,
            ))

        return results
