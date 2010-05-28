"""HouseVote model"""
import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Date
from sqlalchemy.orm import relation, backref

from realt.model.meta import Base, Session
from realt.model.bill import Bill

from simplejson import loads, dumps


class RawHouseVote(Base):
    __tablename__ = "house_vote_raw"

    id = Column(Integer, primary_key=True)
    parliament = Column(Integer, nullable=False)
    session = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    raw_data = Column(Unicode)
    _raw_data = None

    def __init__(self, cvd):
        """Init method for RawHouseVote

        :param cvd: the ChamberHouseVote object to represent
        :type cvd: :class:`realt.lib.parliament_xml.ChamberVoteDetails` instance
        """
        attributes = [
            'context', 'date', 'decision', 'description', 'journal', 'number',
            'parliament', 'participants', 'related_bill', 'session', 'sitting',
            'sponsor',
        ]
        raw_data = dict()
        for attr in attributes:
            raw_data[attr] = getattr(cvd, attr)

        self.parliament = cvd.parliament
        self.session = cvd.session
        self.number = cvd.number

        # Encode the raw data for storage.
        rd = dict(raw_data)
        rd['date'] = self._encode_date(rd['date'])
        self.raw_data = dumps(rd)

        # Set up our cached access to the decoded data.
        self._raw_data = raw_data

    def __repr__(self):
        return "<RawHouseVote(%d, %d, %d)>" % (self.parliament, self.session, self.number)

    def _encode_date(self, date_obj):
        return date_obj.strftime("%Y-%m-%d")

    def _decode_date(self, date_str):
        y, m, d = [int(x) for x in date_str.split('-')]
        return datetime.date(y, m, d)

    def to_dict(self):
        if not self._raw_data:
            # Set up cached access to decoded data
            self._raw_data = loads(self.raw_data)
            self._raw_data['date'] = self._decode_date(self._raw_data['date'])
        return self._raw_data

    def to_housevote(self):
        try:
            from realt.model import HouseVote
            hv = Session.query(HouseVote)\
                    .filter(HouseVote.parliament==self.parliament)\
                    .filter(HouseVote.session==self.session)\
                    .filter(HouseVote.number==self.number)\
                    .one()
        except NoResultFound, e:
            d = self.to_dict()
            hv = HouseVote()
            used_attrs = [
                'context', 'decision', 'number', 'parliament', 'session',
                'session',
            ]
            # Ignore ['date', 'description', 'journal', 'sitting', 'sponsor']
            # for now. HouseVote doesn't use them yet.
            for attr in used_attrs:
                setattr(hv, attr, d[attr])
            hv.bill = get_bill(d['related_bill'])
            hv.member_votes = get_member_votes(d['participants'])
            Session.add(hv)
        finally:
            return hv

def get_bill(related):
    """Convert a 'related' dict, with keys 'number' and 'title_text' to a Bill.

    Either returns an existing bill, creates one, or None.
    """
    # TODO: Update bills IDs to include parliament and session number.
    #       Just using the number isn't actually unique.
    if not related:
        return None

    try:
        bill = Session.query(Bill).filter(Bill.name==related['number']).one()
    except NoResultFound, e:
        bill = Bill(related['number'], related['title_text'])
        Session.add(bill)
    finally:
        return bill

def get_member_votes(participants):
    """Return a list of MemberVote objects, creating necessary members, ridings, etc, as we go."""
    #TODO: implement me.
    pass

