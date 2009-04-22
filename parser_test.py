#!/usr/bin/env python

import sys, urllib
import lxml.etree as ET

def get_bills_url(parliament, session):
    get_vars = {
        'Language': 'E',
        'Mode': 1,
        'Parl': parliament,
        'FltrParl': parliament,
        'Ses': session,
        'FltrSess': session,
        'VoteType': 0,
        'StartDate': '1700-01-01', # any date before the first sitting of the house
        'EndDate': '3000-01-01', # any date after the last sitting of the house
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
    print "Fetching BillsXML from URL:", url
    filehandle = urllib.urlopen(url)

    xml = filehandle.read()
    filehandle.close()
    return xml

def get_votes_xml(parliament, session, vote_number):
    # TODO: catch file IO exceptions
    url = get_votes_url(parliament, session, vote_number)
    print "Fetching VotesXML from URL:", url
    filehandle = urllib.urlopen(url)

    xml = filehandle.read()
    filehandle.close()
    return xml

class HouseVote(object):
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

if __name__ == "__main__":
    bills_xml  = get_bills_xml(40, 2)
    bills_root = ET.XML(bills_xml)

    # to avoid over-taxing the webserver
    # only use the first two bills, for now.
    bills_root = bills_root[:2]

    for vote_node in bills_root:
        attrs = vote_node.attrib
        # example vote_node attrs:
        # {'session': '2', 'date': '2009-04-01', 'parliament': '40', 'number': '47', 'sitting': '38'}

        hv = HouseVote(attrs['parliament'], attrs['session'], attrs['number'])
        hv.sync_from_xml()

        # print all participants and how they voted
        for participant in hv.participants:
            print participant

        # print some details/summary info
        print 'Parliament:', hv.parliament.encode('utf-8')
        print 'Session:', hv.session.encode('utf-8')
        print 'Vote Number:', hv.number.encode('utf-8')
        print 'Context:', hv.context.encode('utf-8')
        print 'Sponsor:', hv.sponsor.encode('utf-8')
        print 'Decision:', hv.decision.encode('utf-8')
        print 'Related Bills:', hv.related_bills
        print "Yeas:", len([p for p in hv.participants if p['vote'] == 'yea'])
        print "Nays:", len([p for p in hv.participants if p['vote'] == 'nay'])
        print "Paired:", len([p for p in hv.participants if p['vote'] == 'paired'])

        print "------------------------------------------------------------------"
        print ""

