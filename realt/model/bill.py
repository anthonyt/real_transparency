"""Bill model"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref

from realt.model.meta import Base

class Bill(Base):
    __tablename__ = "bill"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    title = Column(Unicode)

    sponsor_id = Column(Integer, ForeignKey('mp.id'), nullable=False)
    sponsor = relation('MP', backref=backref('sponsored_bills'))

    def __init__(self, name, title=''):
        self.name = name
        self.title = title

    def __repr__(self):
        return "<Bill('%s')>" % self.name



