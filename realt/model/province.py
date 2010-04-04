"""Province model"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode

from realt.model.meta import Base

class Province(Base):
    __tablename__ = "province"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Province('%s')>" % self.name

