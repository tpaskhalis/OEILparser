#from bs4 import BeautifulSoup
import bs4
import csv
import re
import urllib2
import os.path
import time

def parse_links(inputxml_path, outputcsv_path):
    xmlfile = open(inputxml_path, "r")
    if os.path.isfile(outputcsv_path) and os.path.getsize(outputcsv_path) > 0:
        urllist = open(outputcsv_path, "a")
    else:
        urllist = open(outputcsv_path, "w")
    xmltext = xmlfile.read()
    soup = bs4.BeautifulSoup(xmltext, "xml")
    items = soup.find_all('item')
    csvwriter = csv.writer(urllist)
    for item in items:
        url = item.find('link').text
        csvwriter.writerow([url])
    xmlfile.close()
    urllist.close()

#The OEIL database is not perfect, thus there can be some duplicates after parsing 
#several xml files. This function removes duplicates by converting list of urls 
#into dictionary, using a procedure reference code as a key.
def remove_duplicates(inputcsv_path, outputcsv_path):
    with open(inputcsv_path, "r") as f:
        urllist = [url[0] for url in csv.reader(f)]
        pattern = re.compile(r"[0-9]{4}/[0-9]{4}\(INI\)")
        urldict = {re.search(pattern, url).group():url for url in urllist}
    with open(outputcsv_path, "w") as f:
        for value in urldict.values():
            csvwriter = csv.writer(f)
            csvwriter.writerow([value])
    
def parse_info(inputcsv_path, outputcsv_path):
    urllist = open(inputcsv_path, "r")
    infolist = open(outputcsv_path, "w")
    csvwriter = csv.writer(infolist)
    csvwriter.writerow(['Code','Title', 'Link', 'CommitteeAbr', 
                        'CommitteeFull', 'Rapporteur PartyAbr', 'Rapporteur PartyFull',
                        'Rapporteur', 'Commission DG', 'Commissioner',
                        'Date Committee Draft Report', 'Date Committee Draft Report2', 'Date Committee report tabled for plenary',
                        'Date Text adopted by Parliament', 'Code Text adopted by Parliament',
                        'Link Text adopted by Parliament', 'Link Summary', 'Date Commission response',
                        'Date Commission response2','Code Commission response', 'Code Commission response2',
                        'Link Commission response', 'Link Commission response2', 'Techref', 'Techtype',
                        'Techsubtype', 'Techbasis', 'Techstage', 'Techdossier'])    
    
    url = urllist.readline()[:-2]
    while url:
        reference = title = acronym = committee = group = \
        grouptitle = rapporteur = commission = commissioner = \
        reportdate = adoptedcode = adopteddate = \
        adoptedlink = summaryurl = [u'NA']
        
        page = urllib2.urlopen(url)
        soup = bs4.BeautifulSoup(page.read())
        table = soup.find('table', id='basic_information')
        reference = table.find('span', 'basic_reference').contents    
        title = table.find('p', 'basic_title').contents
        
        table = soup.find('table', id='key_players')
        acronym = table.find('acronym', 'acronym_nohelp').contents
        committee = table.find('span', 'players_committee_text')
        if table.find('span', 'tiptip'):
            group = table.find('span', 'tiptip')
            grouptitle = [unicode(group['title'])]
            if not group.string:
                group = [u'NA']
            else:
                group = group.contents
        else:
            group, grouptitle = [u'NA'], [u'NA']
        if table.find('span', 'players_rapporter_text'):
            rapporteur = [table.find('span', 'players_rapporter_text').string]
        else:
            rapporteur = [u'NA']
        
        if table.find(title='European Commission'):
            commissioncell = table.find(title='European Commission')
            commissionrow = commissioncell.parent.parent
            commission = commissionrow.find('td','players_committee').find('p','players_content')
            commission = [next(commission.stripped_strings)]
            if commissionrow.find('td','players_rapporter_com').find('p','players_content'):
                commissioner = commissionrow.find('td','players_rapporter_com').find('p','players_content')
                commissioner = commissioner.contents
            else:
                commissioner = [u'NA']
        else:
            commission, commissioner = [u'NA'], [u'NA']
        
        for table in soup.findAll('table', id='doc_gateway'):
            for sibling in table.findPreviousSiblings():
                if sibling.text == u'All':
                    draftdate = [u'NA', u'NA']
                    commissiondate = [u'NA', u'NA']
                    commissioncode = [u'NA', u'NA']
                    commissionurl = [u'NA', u'NA']
                    for descendant in table.tbody.descendants:
                        if isinstance(descendant, bs4.element.Tag) and descendant.td:
                            if descendant.td.string == u'Committee draft report' and draftdate[0] == u'NA':
                                draftdate[0] = descendant.find('td', 'event_column_r column_top').contents[0]
                            elif descendant.td.string == u'Committee draft report' and draftdate[0] != u'NA':
                                draftdate[1] = descendant.find('td', 'event_column_r column_top').contents[0]
                            elif descendant.td.string == u'Committee report tabled for plenary, single reading':
                                reportdate = descendant.find('td', 'event_column_r column_top').contents
                            elif descendant.td.string == u'Text adopted by Parliament, single reading' or \
                            descendant.td.string =='Text adopted by Parliament, 1st reading/single reading':
                                adoptedcode = descendant.find('td', 'event_column_document column_top')
                                adopteddate = descendant.find('td', 'event_column_r column_top')
                                adoptedlink = [unicode(adoptedcode.a['href'])]
                                summaryurl = descendant.find('a', 'sumbutton')
                            elif descendant.td.string == u'Commission response to text adopted in plenary' and commissiondate[0] == u'NA':
                                commissiondate[0] = descendant.find('td', 'event_column_r column_top').contents[0]
                                commissioncode[0] = descendant.find('td', 'event_column_document column_top')
                                if commissioncode[0].a:
                                    commissionurl[0] = unicode('http://www.europarl.europa.eu/' + commissioncode[0].a['href'])
                                commissioncode[0] = next(commissioncode[0].stripped_strings)
                            elif descendant.td.string == u'Commission response to text adopted in plenary' and commissiondate[0] != u'NA':
                                commissiondate[1] = descendant.find('td', 'event_column_r column_top').contents[0]
                                commissioncode[1] = descendant.find('td', 'event_column_document column_top')
                                if commissioncode[1].a:
                                    commissionurl[1] = unicode('http://www.europarl.europa.eu/' + commissioncode[1].a['href'])
                                commissioncode[1] = next(commissioncode[1].stripped_strings)
                        else:
                            continue
                    break
                elif sibling.text == u'European Parliament':
                    draftdate = [u'NA', u'NA']
                    commissiondate = [u'NA', u'NA']
                    commissioncode = [u'NA', u'NA']
                    commissionurl = [u'NA', u'NA']
                    for descendant in table.tbody.descendants:
                        if isinstance(descendant, bs4.element.Tag) and descendant.td:
                            if descendant.td.string == u'Committee draft report' and draftdate[0] == u'NA':
                                draftdate[0] = descendant.find('td', 'event_column_r column_top').contents[0]
                            elif descendant.td.string == u'Committee draft report' and draftdate[0] != u'NA':
                                draftdate[1] = descendant.find('td', 'event_column_r column_top').contents[0]
                            elif descendant.td.string == u'Committee report tabled for plenary, single reading':
                                reportdate = descendant.find('td', 'event_column_r column_top').contents
                            elif descendant.td.string == u'Text adopted by Parliament, single reading' or \
                            descendant.td.string =='Text adopted by Parliament, 1st reading/single reading':
                                adoptedcode = descendant.find('td', 'event_column_document column_top')
                                adopteddate = descendant.find('td', 'event_column_r column_top')
                                adoptedlink = [unicode(adoptedcode.a['href'])]
                                summaryurl = descendant.find('a', 'sumbutton')
                            elif descendant.td.string == u'Commission response to text adopted in plenary' and commissiondate[0] == u'NA':
                                commissiondate[0] = descendant.find('td', 'event_column_r column_top').contents[0]
                                commissioncode[0] = descendant.find('td', 'event_column_document column_top')
                                if commissioncode[0].a:
                                    commissionurl[0] = unicode('http://www.europarl.europa.eu/' + commissioncode[0].a['href'])
                                commissioncode[0] = next(commissioncode[0].stripped_strings)
                            elif descendant.td.string == u'Commission response to text adopted in plenary' and commissiondate[0] != u'NA':
                                commissiondate[1] = descendant.find('td', 'event_column_r column_top').contents[0]
                                commissioncode[1] = descendant.find('td', 'event_column_document column_top')
                                if commissioncode[1].a:
                                    commissionurl[1] = unicode('http://www.europarl.europa.eu/' + commissioncode[1].a['href'])
                                commissioncode[1] = next(commissioncode[1].stripped_strings)
                        else:
                            continue
                        
        table = soup.find('table', id='technicalInformations')
        techreference = table.find('td', 'column_center')
        tech = table.findAll('td', 'column_center column_top')
        tech = [t.contents[0] for t in tech]
        
        csvwriter.writerow(reference + title + [url] + acronym 
                            + [next(committee.stripped_strings)] + group + grouptitle
                            + rapporteur + commission + commissioner
                            + draftdate + reportdate
                            + adopteddate.contents + [next(adoptedcode.stripped_strings)] 
                            + adoptedlink + [(unicode('http://www.europarl.europa.eu/') + summaryurl['href'])]
                            + commissiondate + commissioncode + commissionurl + techreference.contents + tech)
        url = urllist.readline()[:-2]
        time.sleep(1)
    urllist.close()
    infolist.close()

def parse_text(inputcsv_path, outputfolder):
    with open(inputcsv_path, 'r') as f:
        urllist = [url[15] for url in csv.reader(f, delimiter=',')]
        urllist = urllist[1:]
    for url in urllist:
        time.sleep(1)
        page = urllib2.urlopen(url)
        soup = bs4.BeautifulSoup(page.read())
        procedure = soup.find('a', 'ring_ref_link')
        procedure = re.split('[/()]', procedure.contents[0])
        procedurefile = procedure[2] + u'_' + procedure[0] + u'-' + procedure[1]
        with open(os.path.join(outputfolder, procedurefile + u'.tsv'), 'w') as f:
            content = soup.find('tr', 'contents')
            paragraphs = content.findAll('p')
            
            pattern = re.compile(r'^[A-Z0-9]{1,3}\.\s{1,2}', re.UNICODE)
            paragraphs = [p.contents[0] for p in paragraphs if p.contents and isinstance(p.contents[0], bs4.element.NavigableString) and re.match(pattern, p.contents[0])]
            splitpattern = re.compile(r'\.\s{1,2}', re.UNICODE)
            paragraphs = [re.split(splitpattern, p) for p in paragraphs]
            clearpattern = re.compile(r'^[\s\n\t\"]*|[\s\n\t\"]*$', re.UNICODE)
            for p in paragraphs:
                p[1] = re.sub(clearpattern, u'', p[1])
            csvwriter = csv.writer(f, dialect='excel-tab')
            for p in paragraphs:
                csvwriter.writerow(p)

#for num in range(2004,2008):
#    parse_links('./data/' + str(num) + '.xml', './data/urls.csv')
#parse_links('./data/2008.rss', './data/urls.csv')
#parse_links('./data/2009.xml', './data/urls.csv')
#parse_links('./data/20042009.rss', './data/urls.csv')
#parse_links('./data/20092014.xml', './data/urls.csv')
#remove_duplicates('./data/urls.csv', './data/urls.csv')
#parse_info("./data/short_urls.csv", "./data/short_info.csv")
#parse_info("./data/urls.csv", "./data/info.csv")
#parse_text('./data/short_info.csv', './data/short_text')
parse_text('./data/info.csv', './data/text')