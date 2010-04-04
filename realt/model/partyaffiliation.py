"""Affiliation model"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Date
from sqlalchemy.orm import relation, backref

from realt.model.meta import Base


class Affiliation(Base):
    __tablename__ = "affiliation"

    id = Column(Integer, primary_key=True)
    began = Column('began_on', Date, nullable=False)
    ended = Column('ended_on', Date, nullable=False)

    party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    party = relation('Party', backref=backref('affiliations'))

    mp_id = Column(Integer, ForeignKey('mp.id'), nullable=False)
    mp = relation('MP', backref=backref('affiliations'))

    def __init__(self, mp, party, began, ended):
        self.mp = mp
        self.party = party
        self.began = began
        self.ended = ended

    def __repr__(self):
        return "<Affiliation('%s', '%s')>" % (self.mp.full_name, self.party.name)



