import collections
import os.path
import unittest

import mock

from realt import votes

class TestURLs(unittest.TestCase):

    def test_get_bills_url(self):
        url = votes.get_bills_url(1234, 5678)
        # XXX: Should we actually be testing that the params are in a
        #      particular order?
        self.assertEqual(url,
            "http://www2.parl.gc.ca/HouseChamberBusiness/ChamberVoteList.aspx?"
            "xml=True&Language=E&Mode=1&AgreedTo=True&EndDate=2015-07-22&"
            "VoteType=0&Tie=True&StartDate=1700-01-01&Negatived=True&Ses=5678&"
            "Parl=1234&FltrSess=5678&FltrParl=1234"
        )

    def test_get_votes_url(self):
        url = votes.get_votes_url(1234, 5678, 91011)
        # XXX: Should we actually be testing that the params are in a
        #      particular order?
        self.assertEqual(url,
            "http://www2.parl.gc.ca/HouseChamberBusiness/ChamberVoteDetail.aspx?"
            "xml=True&Ses=5678&Mode=1&Language=E&vote=91011&Parl=1234&"
            "FltrSess=5678&FltrParl=1234"
        )

    def test_votes_in_session(self):
        test_xml_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'bills_xml_40_40.xml',
        ))
        with open(test_xml_path, 'rb') as f:
            content = f.read()
        MockedResponse = collections.namedtuple('MockedResponse', ['content'])
        mocked_response = MockedResponse(content=content)

        with mock.patch('requests.get', return_value=mocked_response):
            votes_in_session = votes.votes_in_session(40, 40)

        self.assertEqual(votes_in_session, range(467, 0, -1))
