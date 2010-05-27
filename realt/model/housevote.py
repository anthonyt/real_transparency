"""HouseVote model"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Date
from sqlalchemy.orm import relation, backref

from realt.model.meta import Base


class HouseVote(Base):
    __tablename__ = "house_vote"

    id = Column(Integer, primary_key=True)
    parliament = Column(Integer, nullable=False)
    session = Column(Integer, nullable=False)
    vote_number = Column(Integer, nullable=False)
    context = Column(Unicode)
    decision = Column(Unicode)

    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=False)
    bill = relation('Bill', backref=backref('votes'))

    def __init__(self, bill=None):
        self.bill = bill

    def __repr__(self):
        return "<HouseVote(%d, %d, %d, '%s', '%s')>" % (self.parliament, self.session, self.vote_number, self.bill.name, self.decision)

