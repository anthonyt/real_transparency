"""Party model"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode, Date

from realt.model.meta import Base

class Party(Base):
    __tablename__ = "party"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    created = Column('created_on', Date, nullable=False)
    removed = Column('removed_on', Date, nullable=False)

    def __init__(self, name, created, removed):
        self.name = name
        self.created = created
        self.removed = removed

    def __repr__(self):
        return "<Party('%s')>" % self.name


