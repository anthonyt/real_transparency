"""ElectedTerm model"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Date
from sqlalchemy.orm import relation, backref

from realt.model.meta import Base


class ElectedTerm(Base):
    __tablename__ = "elected_term"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    began = Column('began_on', Date, nullable=False)
    ended = Column('ended_on', Date, nullable=False)

    district_id = Column(Integer, ForeignKey('district.id'), nullable=False)
    district = relation('District', backref=backref('terms', order_by=began))

    mp_id = Column(Integer, ForeignKey('mp.id'), nullable=False)
    mp = relation('MP', backref=backref('terms', order_by=began))

    def __init__(self, mp, district, began, ended):
        self.mp = mp
        self.district = district
        self.began = began
        self.ended = ended

    def __repr__(self):
        return "<ElectedTerm('%s', '%s')>" % (self.mp.full_name, self.district.name)


