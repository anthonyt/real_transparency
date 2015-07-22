from unittest import TestCase
from realt.votes import get_bills_url
from realt.votes import get_votes_url

class TestURLs(TestCase):

    def test_get_bills_url(self):
        url = get_bills_url(1234, 5678)
        # XXX: Should we actually be testing that the params are in a
        #      particular order?
        self.assertEqual(url,
            "http://www2.parl.gc.ca/HouseChamberBusiness/ChamberVoteList.aspx?"
            "xml=True&Language=E&Mode=1&AgreedTo=True&EndDate=2015-07-22&"
            "VoteType=0&Tie=True&StartDate=1700-01-01&Negatived=True&Ses=5678&"
            "Parl=1234&FltrSess=5678&FltrParl=1234"
        )

    def test_get_votes_url(self):
        url = get_votes_url(1234, 5678, 91011)
        # XXX: Should we actually be testing that the params are in a
        #      particular order?
        self.assertEqual(url,
            "http://www2.parl.gc.ca/HouseChamberBusiness/ChamberVoteDetail.aspx?"
            "xml=True&Ses=5678&Mode=1&Language=E&vote=91011&Parl=1234&"
            "FltrSess=5678&FltrParl=1234"
        )

