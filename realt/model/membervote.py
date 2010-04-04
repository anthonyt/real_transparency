"""MemberVote model"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Date
from sqlalchemy.orm import relation, backref

from realt.model.meta import Base


class MemberVote(Base):
    __tablename__ = "member_vote"

    id = Column(Integer, primary_key=True)
    value = Column(Unicode(10), nullable=False)

    house_vote_id = Column(Integer, ForeignKey('house_vote.id'), nullable=False)
    house_vote = relation('HouseVote', backref=backref('member_votes'))

    mp_id = Column(Integer, ForeignKey('mp.id'), nullable=False)
    mp = relation('MP', backref=backref('terms'))

    def __init__(self, value, mp, house_vote):
        self.mp = mp
        self.value = value
        self.house_vote = house_vote

    def __repr__(self):
        return "<MemberVote('%s', '%s')>" % (self.mp.full_name, self.house_vote.bill.name, self.value)



