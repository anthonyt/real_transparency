
__all__ = ['chamber_vote_details']

import urllib
import datetime
import lxml.etree as ET

def get_bills_url(parliament, session):
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    tomorrow = str(today + one_day)

    get_vars = {
        'Language': 'E',
        'Mode': 1,
        'Parl': parliament,
        'FltrParl': parliament,
        'Ses': session,
        'FltrSess': session,
        'VoteType': 0,
        'StartDate': '1700-01-01', # any date before the first sitting of the house
        'EndDate': tomorrow, # any date after the last sitting of the house
        'AgreedTo': 'True',
        'Negatived': 'True',
        'Tie': 'True',
        'xml': 'True'
    }
    base_url = "http://www2.parl.gc.ca/HouseChamberBusiness/Chambervotelist.aspx"
    return base_url + '?' + urllib.urlencode(get_vars)

def get_votes_url(parliament, session, vote_number):
    get_vars = {
        'Language': 'E',
        'Mode': 1,
        'Parl': parliament,
        'FltrParl': parliament,
        'Ses': session,
        'FltrSess': session,
        'vote': vote_number,
        'xml': 'True'
    }
    base_url = "http://www2.parl.gc.ca/HouseChamberBusiness/Chambervotedetail.aspx"
    return base_url + '?' + urllib.urlencode(get_vars)

def get_bills_xml(parliament, session):
    # TODO: catch file IO exceptions
    url = get_bills_url(parliament, session)
    filehandle = urllib.urlopen(url)

    xml = filehandle.read()
    filehandle.close()
    return xml

def get_votes_xml(parliament, session, vote_number):
    # TODO: catch file IO exceptions
    url = get_votes_url(parliament, session, vote_number)
    filehandle = urllib.urlopen(url)

    xml = filehandle.read()
    filehandle.close()
    return xml

class ChamberVoteDetails(object):
    def __init__(self, parliament, session, number):
        self.parliament = parliament
        self.session = session
        self.number = number

        self.context = None
        self.sponsor = None
        self.decision = None
        self.related_bills = []
        self.participants = []

    def get_xml(self):
        return get_votes_xml(self.parliament, self.session, self.number)

    def sync_from_xml(self):
        xml = self.get_xml()
        root = ET.XML(xml)
        context = root.xpath('Context')[0]
        sponsor = root.xpath('Sponsor')[0]
        decision = root.xpath('Decision')[0]
        related_bills = root.xpath('RelatedBill')
        participants = root.xpath('Participant')

        self.context = "\n".join(['<p>' + ' '.join(para.text.split()) + '</p>' for para in context.xpath('Para')])
        self.sponsor = sponsor.text
        self.decision = decision.text
        self.related_bills = [x.attrib['number'] for x in related_bills]

        self.participants = []
        for p in participants:
            name = p.xpath('Name')[0].text
            first_name = p.xpath('FirstName')[0].text
            last_name = p.xpath('LastName')[0].text
            constituency = p.xpath('Constituency')[0].text
            province = p.xpath('Province')[0].attrib['code']

            if p.xpath('RecordedVote/Yea')[0].text == '1':
                vote = 'yea'
            elif p.xpath('RecordedVote/Nay')[0].text == '1':
                vote = 'nay'
            elif p.xpath('RecordedVote/Paired')[0].text == '1':
                vote = 'paired'
            else:
                raise Exception('voting record error')
            participant = {
                'name':name,
                'first_name': first_name,
                'last_name': last_name,
                'constituency': constituency,
                'province': province,
                'vote': vote
            }
            self.participants.append(participant)

def chamber_vote_details(parliament, session, vote_number=None):
    """Return a list of ChamberVoteDetails representing the requested vote(s).

    Populates the fields of ChamberVoteDetails with information pulled down
    from the Government of Canada's XML feed.

    Leaving the vote_number field as None will return a list of all votes from
    the requested parliament/session.

    Setting the vote_number field to a valid number will return a list
    containing only the ChamberVoteDetails object that represents that vote.
    """
    cvdetails = []
    if vote_number is None:
        bills_xml  = get_bills_xml(parliament, session)
        bills_root = ET.XML(bills_xml)
        votes = [
            (vote_node.attrib['parliament'],
             vote_node.attrib['session'],
             vote_node.attrib['number'])
            for vote_node in bills_root
        ]
        # example vote_node attrs:
        # {'session': '2', 'date': '2009-04-01', 'parliament': '40', 'number': '47', 'sitting': '38'}
    else:
        votes = [(parliament, session, vote_number)]

    for (parliament, session, vote_number) in votes:
        cvd = ChamberVoteDetails(parliament, session, vote_number)
        cvd.sync_from_xml()
        cvdetails.append(cvd)
        ## print all participants and how they voted
        # for participant in cvd.participants:
        #     print participant
        ## print some details/summary info
        # print 'Parliament:', cvd.parliament.encode('utf-8')
        # print 'Session:', cvd.session.encode('utf-8')
        # print 'Vote Number:', cvd.number.encode('utf-8')
        # print 'Context:', cvd.context.encode('utf-8')
        # print 'Sponsor:', cvd.sponsor.encode('utf-8')
        # print 'Decision:', cvd.decision.encode('utf-8')
        # print 'Related Bills:', cvd.related_bills
        # print "Yeas:", len([p for p in cvd.participants if p['vote'] == 'yea'])
        # print "Nays:", len([p for p in cvd.participants if p['vote'] == 'nay'])
        # print "Paired:", len([p for p in cvd.participants if p['vote'] == 'paired'])

    return cvdetails

