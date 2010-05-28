"""The application's model objects"""
from realt.model.meta import Session, Base

from realt.model.province import Province
from realt.model.district import District
from realt.model.electedterm import ElectedTerm
from realt.model.party import Party
from realt.model.mp import MP
from realt.model.partyaffiliation import Affiliation
from realt.model.bill import Bill
from realt.model.housevote import HouseVote
from realt.model.housevote_raw import RawHouseVote
from realt.model.membervote import MemberVote

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)

