
__all__ = ['chamber_vote_details', 'votes_in_session']

import urllib
import datetime
import lxml.etree as ET

cached_xml = dict()

parliament_url = "http://www2.parl.gc.ca"

import logging
log = logging.getLogger(__name__)

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
    base_url = parliament_url + "/HouseChamberBusiness/ChamberVoteList.aspx"
    url = base_url + '?' + urllib.urlencode(get_vars)
    log.info("Bills URL for (%d, %d): %s", parliament, session, url)
    return url

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
    base_url = parliament_url + "/HouseChamberBusiness/ChamberVoteDetail.aspx"
    url = base_url + '?' + urllib.urlencode(get_vars)
    log.info("Votes URL for (%d, %d, %d): %s", parliament, session, vote_number, url)
    return url

def get_bills_xml(parliament, session):
    """Returns the xml string listing all votes, based on id numbers.

    :param parliament: the parliament number
    :type parliament: int

    :param session: the session number within the parliament
    :type session: int
    """
    # TODO: catch file IO exceptions
    hash = 'bills_%d-%d' % ( parliament, session )
    if hash in cached_xml:
        log.info('Returning cached bills XML for (%d, %d)', parliament, session)
        return cached_xml[hash]
    url = get_bills_url(parliament, session)
    filehandle = urllib.urlopen(url)

    xml = filehandle.read()
    cached_xml[hash] = xml
    filehandle.close()
    log.info('Got bills XML for (%d, %d)', parliament, session)
    return xml

def get_votes_xml(parliament, session, vote_number):
    """Returns the XML string for a vote, based on id numbers.

    :param parliament: the parliament number
    :type parliament: int

    :param session: the session number within the parliament
    :type session: int

    :param vote_number: the vote number within the session
    :type vote_number: int
    """
    # TODO: catch file IO exceptions
    hash = 'votes_%d-%d-%d' % ( parliament, session, vote_number )
    if hash in cached_xml:
        log.info('Returning cached votes XML for (%d, %d, %d)', parliament, session, vote_number)
        return cached_xml[hash]

    url = get_votes_url(parliament, session, vote_number)
    filehandle = urllib.urlopen(url)

    xml = filehandle.read()
    cached_xml[hash] = xml
    filehandle.close()
    log.info('Got votes XML for (%d, %d, %d)', parliament, session, vote_number)
    return xml

class ChamberVoteDetails(object):
    def __init__(self, parliament, session, number, sitting, date, description):
        """Initialize a ChamberVoteDetails object.

        :param parliament: the parliament number
        :type parliament: int

        :param session: the session number within the parliament
        :type session: int

        :param number: the vote number within the session
        :type number: int

        :param sitting: the sitting number within the session
        :type sitting: int

        :param date: the date of the vote
        :type date: :class:`datetime.date` instance

        :param description: the text description of the vote
        :type description: basestring
        """
        self.parliament = parliament
        self.session = session
        self.number = number

        self.sitting = sitting
        self.date = date
        self.description = description

        self.context = None
        self.sponsor = None
        self.decision = None
        self.related_bill = None
        self.participants = []

    def get_xml(self):
        """Returns the XML string representing this vote's details.
        """
        return get_votes_xml(self.parliament, self.session, self.number)

    def sync_journal(self):
        """Sets self.journal.

        self.journal is a tuple of unicode objects representing the title and
        URL this vote's published entry in the house journals.
        """
        # TODO: catch file IO exceptions
        url = get_votes_url(self.parliament, self.session, self.number).replace('xml=True', 'xml=False')
        filehandle = urllib.urlopen(url)
        html = filehandle.read()
        filehandle.close()

        title = ''
        link = ''

        try:
            label_index = html.index('voteJournalsLabel')

            link_start = html.index('href', label_index) + len('href="')
            link_end = html.index('">', link_start)
            link = parliament_url + html[link_start:link_end]

            title_start = link_end + len('">')
            title_end = html.index("</a>", title_start)
            title = html[title_start:title_end]

        except Exception, e:
            pass

        self.journal = (title, link)

    def sync_from_xml(self):
        """Updates the properties of this vote from the online XML document.

        Properties set: context, sponsor, decision, related_bill, participants.
        """
        xml = self.get_xml()
        root = ET.XML(xml)
        context = root.xpath('Context')[0]
        sponsor = root.xpath('Sponsor')[0]
        decision = root.xpath('Decision')[0]
        related_bill = root.xpath('RelatedBill')[0]
        participants = root.xpath('Participant')

        # Get the context in a more text friendly format:
        self.context = "".join([' '.join(ET.tostring(para).strip().split()) for para in context.xpath('Para')])
        # Replace known styling tags.
        self.context = self.context.replace('<Para>', '').replace('</Para>', '\n').strip()
        self.context = self.context.replace('<Emphasis>', '<em>').replace('</Emphasis>', '</em>')

        self.sponsor = sponsor.text
        self.decision = decision.text
        self.related_bill = dict(related_bill.attrib)
        self.related_bill['title_text'] = related_bill.text.strip()

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

def votes_in_session(parliament, session):
    """Return a list of vote numbers occurring during a given parliament and session.
    """
    bills_xml  = get_bills_xml(parliament, session)
    bills_root = ET.XML(bills_xml)
    numbers = [int(node.attrib['number']) for node in bills_root]
    return numbers

def chamber_vote_details(parliament, session, vote_numbers=None):
    """Return a list of ChamberVoteDetails representing the requested vote(s).

    Populates the fields of ChamberVoteDetails with information pulled down
    from the Government of Canada's XML feed.

    Leaving the vote_number field as None will return a list of all votes from
    the requested parliament/session.

    Setting the vote_number field to a valid number will return a list
    containing only the ChamberVoteDetails object that represents that vote.
    """
    cvdetails = []
    bills_xml  = get_bills_xml(parliament, session)
    bills_root = ET.XML(bills_xml)

    if vote_numbers:
        vote_nodes = [node for node in bills_root[:1] if int(node.attrib['number']) in vote_numbers]

    for vote_node in vote_nodes:
        # example vote_node attrs:
        # {'session': '2', 'date': '2009-04-01', 'parliament': '40', 'number': '47', 'sitting': '38'}
        y, m, d = [int(x) for x in vote_node.attrib['date'].split('-')]
        vote_date = datetime.date(y, m, d)
        args = (
            int(vote_node.attrib['parliament']),
            int(vote_node.attrib['session']),
            int(vote_node.attrib['number']),
            int(vote_node.attrib['sitting']),
            vote_date,
            ET.tostring(vote_node.xpath('Description')[0]).strip()[13:-14]
        )
        cvd = ChamberVoteDetails(*args)
        cvd.sync_from_xml()
        cvd.sync_journal()
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
        # print 'Related Bill:', cvd.related_bill
        # print 'Published vote and details:', cvd.journal
        # print "Yeas:", len([p for p in cvd.participants if p['vote'] == 'yea'])
        # print "Nays:", len([p for p in cvd.participants if p['vote'] == 'nay'])
        # print "Paired:", len([p for p in cvd.participants if p['vote'] == 'paired'])

    return cvdetails

