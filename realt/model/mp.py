"""MP model"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode

from realt.model.meta import Base

class MP(Base):
    __tablename__ = "mp"

    id = Column(Integer, primary_key=True)
    first_name = Column(Unicode(100), nullable=False)
    last_name = Column(Unicode(100), nullable=False)
    full_name = Column(Unicode(100), nullable=False)

    def __init__(self, first_name, last_name, full_name):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = full_name

    def __repr__(self):
        return "<MP('%s')>" % self.full_name


