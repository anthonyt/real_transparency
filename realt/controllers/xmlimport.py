import logging

from realt.lib.base import BaseController
from realt.lib.decorators import expose
from realt.lib.parliament_xml import chamber_vote_details
from realt.lib.parliament_xml import votes_in_session
from realt.model import RawHouseVote
from realt.model.meta import Session

log = logging.getLogger(__name__)

class XmlimportController(BaseController):

    @expose('json')
    def index(self, parliament, session, vote_number=None, limit=1):
        if vote_number is not None:
            vote_number = int(vote_number)
        parliament = int(parliament)
        session = int(session)
        limit = int(limit)

        data = self._pull_data(parliament, session, vote_number, limit)
        return data

    def _pull_data(self, parliament, session, vote_number, limit=1):
        if vote_number:
            vote_numbers = [vote_number]
        else:
            vote_numbers = votes_in_session(parliament, session)

        if limit > 0 and len(vote_numbers) > limit:
            vote_numbers = vote_numbers[:limit]

        rawvotes = Session.query(RawHouseVote)\
            .filter(RawHouseVote.parliament==parliament)\
            .filter(RawHouseVote.session==session)\
            .filter(RawHouseVote.number.in_(vote_numbers))\
            .all()

        found_numbers = [rv.number for rv in rawvotes]
        new_vote_numbers = [n for n in vote_numbers if n not in found_numbers]

        log.info('Found these RawHouseVotes in the database: %r', found_numbers)
        log.info('Looking up these new RawHouseVotes: %r', new_vote_numbers)

        cvds = chamber_vote_details(parliament, session, new_vote_numbers)
        for cvd in cvds:
            rv = RawHouseVote(cvd)
            Session.add(rv)
            rawvotes.append(rv)

        results = []
        for rv in rawvotes:
            d = rv.to_dict()
            d['date'] = d['date'].strftime('%y-%m-%d')
            results.append(d)

        return results
