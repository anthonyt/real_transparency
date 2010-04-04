"""District model"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Date
from sqlalchemy.orm import relation, backref

from realt.model.meta import Base


class District(Base):
    __tablename__ = "district"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    province_id = Column(Integer, ForeignKey('province.id'), nullable=False)
    province = relation('Province', backref=backref('districts', order_by=id))

    created = Column('created_on', Date, nullable=False)
    removed = Column('removed_on', Date, nullable=False)

    def __init__(self, name, province, created, removed):
        self.name = name
        self.province = province
        self.created = created
        self.removed = removed

    def __repr__(self):
        return "<District('%s', '%s')>" % (self.name, self.province.name)

