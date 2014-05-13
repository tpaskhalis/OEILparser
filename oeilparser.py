#This script requires Python2.7+ and library bs4(which is not part of standard installation).
import bs4
import csv
import re
import urllib2
import os
import time

#This function takes search query results in xml or rss(if xml is unavailable) as an input
#and writes url list in csv format to path specified as a second argument.
def parse_urls(inputxml_path, outputcsv_path):
    with open(inputxml_path, "r") as f:
        xmltext = f.read()
        soup = bs4.BeautifulSoup(xmltext, "xml")
        items = soup.findall('item')
        if os.path.isfile(outputcsv_path) and os.path.getsize(outputcsv_path) > 0:
            urllist = open(outputcsv_path, "a")
        else:
            urllist = open(outputcsv_path, "w")
        csvwriter = csv.writer(urllist)
        for item in items:
            url = item.find('link').text
            csvwriter.writerow([url])
        urllist.close()

#The oeil database is not perfect, thus there can be some duplicates after parsing 
#several xml files. This function removes duplicates by converting list of urls 
#into dictionary, using a procedure reference code as a key.
def remove_duplicates(inputcsv_path, outputcsv_path):
    with open(inputcsv_path, "r") as f:
        urllist = [url[0] for url in csv.reader(f)]
        pattern = re.compile(r"[0-9]{4}/[A-Z0-9]{4,5}\([A-Z]{3}\)")
        urldict = {re.search(pattern, url).group():url for url in urllist}
    with open(outputcsv_path, "w") as f:
        for value in urldict.values():
            csvwriter = csv.writer(f)
            csvwriter.writerow([value])

#This function parses documentation gateway at the bottom of a page and is called 
#from parse_info. First for 'all' documents and in case this tab is missing from 
#'European Parliament' tab. 
def parse_doc_gateway(table_doc_gateway):
    adopteddate = [u'NA']
    adoptedcode = [u'NA']
    adoptedlink = [u'NA']
    reportdate = [u'NA']
    summaryurl = [u'NA']
    draftdate = [u'NA', u'NA']
    commissiondate = [u'NA', u'NA']
    commissioncode = [u'NA', u'NA']
    commissionurl = [u'NA', u'NA']
    for descendant in table_doc_gateway.tbody.descendants:
        if isinstance(descendant, bs4.element.Tag) and descendant.td:
            if descendant.td.string == u'Committee draft report' and draftdate[0] == u'NA':
                if descendant.find('td', 'event_column_r column_top'):
                    draftdate[0] = descendant.find('td', 'event_column_r column_top').contents[0]
            elif descendant.td.string == u'Committee draft report' and draftdate[0] != u'NA':
                if descendant.find('td', 'event_column_r column_top'):
                    draftdate[1] = descendant.find('td', 'event_column_r column_top').contents[0]
            elif descendant.td.string == u'Committee report tabled for plenary, single reading':
                if descendant.find('td', 'event_column_r column_top'):
                    reportdate = descendant.find('td', 'event_column_r column_top').contents
            elif descendant.td.string == u'Text adopted by Parliament, single reading' or \
            descendant.td.string =='Text adopted by Parliament, 1st reading/single reading':
                if descendant.find('td', 'event_column_document column_top'):
                    adoptedcode = descendant.find('td', 'event_column_document column_top')
                    adoptedlink = [unicode(adoptedcode.a['href'])]
                    adoptedcode = [next(adoptedcode.stripped_strings)]
                if descendant.find('td', 'event_column_r column_top'):
                    adopteddate = descendant.find('td', 'event_column_r column_top').contents
                if descendant.find('a', 'sumbutton'):
                    summaryurl = descendant.find('a', 'sumbutton')
                    summaryurl = [(unicode('http://www.europarl.europa.eu/') + summaryurl['href'])]
            elif descendant.td.string == u'Commission response to text adopted in plenary' and commissiondate[0] == u'NA':
                if descendant.find('td', 'event_column_r column_top'):
                    commissiondate[0] = descendant.find('td', 'event_column_r column_top').contents[0]
                if descendant.find('td', 'event_column_document column_top'):
                    commissioncode[0] = descendant.find('td', 'event_column_document column_top')
                    if commissioncode[0].a:
                        commissionurl[0] = unicode('http://www.europarl.europa.eu/' + commissioncode[0].a['href'])
                    commissioncode[0] = next(commissioncode[0].stripped_strings)
            elif descendant.td.string == u'Commission response to text adopted in plenary' and commissiondate[0] != u'NA':
                if descendant.find('td', 'event_column_r column_top'):
                    commissiondate[1] = descendant.find('td', 'event_column_r column_top').contents[0]
                if descendant.find('td', 'event_column_document column_top'):
                    commissioncode[1] = descendant.find('td', 'event_column_document column_top')
                    if commissioncode[1].a:
                        commissionurl[1] = unicode('http://www.europarl.europa.eu/' + commissioncode[1].a['href'])
                    commissioncode[1] = next(commissioncode[1].stripped_strings)
            else:
                continue
    return draftdate + reportdate + adopteddate + adoptedcode + adoptedlink + summaryurl + commissiondate + commissioncode + commissionurl

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
        reference = [u'NA']
        title = [u'NA']
        acronym = [u'NA']
        committee = [u'NA']
        group = [u'NA']
        grouptitle = [u'NA']
        rapporteur = [u'NA']
        commission = [u'NA']
        commissioner = [u'NA']
        doc = 13 * [u'NA']
        
        page = urllib2.urlopen(url)
        soup = bs4.BeautifulSoup(page.read())
        table = soup.find('table', id='basic_information')
        reference = table.find('span', 'basic_reference').contents    
        title = table.find('p', 'basic_title').contents
        
        table = soup.find('table', id='key_players')
        if table.find('acronym', 'acronym_nohelp'):
            acronym = table.find('acronym', 'acronym_nohelp').contents
        if table.find('span', 'players_committee_text'):
            committee = table.find('span', 'players_committee_text')
            committee = [next(committee.stripped_strings)]
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

        if table.find(title='European Commission'):
            commissioncell = table.find(title='European Commission')
            commissionrow = commissioncell.parent.parent
            commission = commissionrow.find('td','players_committee').find('p','players_content')
            commission = [next(commission.stripped_strings)]
            if commissionrow.find('td','players_rapporter_com').find('p','players_content'):
                commissioner = commissionrow.find('td','players_rapporter_com').find('p','players_content')
                commissioner = commissioner.contents
        
        for table in soup.findall('table', id='doc_gateway'):
            for sibling in table.findPreviousSiblings():
                if sibling.text == u'all':
                    doc = parse_doc_gateway(table)
                    break
                elif sibling.text == u'European Parliament':
                    doc = parse_doc_gateway(table)
                        
        table = soup.find('table', id='technicalInformations')
        techreference = table.find('td', 'column_center')
        tech = table.findall('td', 'column_center column_top')
        tech = [t.contents[0] for t in tech]
        
        csvwriter.writerow(reference + title + [url] + acronym 
                            + committee + group + grouptitle
                            + rapporteur + commission + commissioner
                            + doc + techreference.contents + tech)
        url = urllist.readline()[:-2]
        time.sleep(1)
    urllist.close()
    infolist.close()

def parse_text(inputcsv_path, outputfolder):
    with open(inputcsv_path, 'r') as f:
        urllist = [url[15] for url in csv.reader(f, delimiter=',')]
        urllist = urllist[1:]
        urllist = filter(None, urllist)
    for url in urllist:
        page = urllib2.urlopen(url)
        soup = bs4.BeautifulSoup(page.read())
        procedure = soup.find('a', 'ring_ref_link')
        procedure = re.split('[/()]', procedure.contents[0])
        procedurefile = procedure[2] + u'_' + procedure[0] + u'-' + procedure[1]
        
        content = soup.find('tr', 'contents')
        paragraphs = content.findall('p')
        pattern = re.compile(r'^[A-Z0-9]{1,3}\.\s{1,2}', re.UNICODE)
        paragraphs = [p.text for p in paragraphs if p.text and re.match(pattern, p.text)]
        splitpattern = re.compile(r'\.\s{1,2}', re.UNICODE)
        paragraphs = [re.split(splitpattern, p) for p in paragraphs]
        clearpattern = re.compile(r'^[\s\n\t\"]*|[\s\n\t\"]*$|[\n\t]', re.UNICODE)
        for p in paragraphs:
            p[1] = re.sub(clearpattern, u'', p[1])
        with open(os.path.join(outputfolder, procedurefile + u'.tsv'), 'w') as f:
            csvwriter = csv.writer(f, dialect='excel-tab')
            for p in paragraphs:
                csvwriter.writerow(p)
        time.sleep(1)

for f in os.listdir('./oeil/search_query_results/ini/6th_term/'):
    parse_urls('./oeil/search_query_results/ini/6th_term/' + f, './oeil/urlsini6.csv')
for f in os.listdir('./oeil/search_query_results/ini/7th_term/'):
    parse_urls('./oeil/search_query_results/ini/7th_term/' + f, './oeil/urlsini7.csv')
remove_duplicates('./oeil/urlsini6.csv', './oeil/urlsini6.csv')
remove_duplicates('./oeil/urlsini7.csv', './oeil/urlsini7.csv')
parse_info('./oeil/urlsini6.csv', './oeil/metadataini6.csv')
parse_info('./oeil/urlsini7.csv', './oeil/metadataini7.csv')

#for f in os.listdir('./oeil/search_query_results/ini/'):
#    parse_urls('./oeil/search_query_results/ini/' + f, './oeil/urlsini.csv')
#remove_duplicates('./oeil/urlsini.csv', './oeil/urlsini.csv')
#parse_info("./oeil/urlsini.csv", "./oeil/metadataini.csv")
#parse_text('./oeil/metadataini.csv', './oeil/text')

#for f in os.listdir('./oeil/search_query_results/all/6th_term/'):
#    parse_urls('./oeil/search_query_results/all/6th_term/' + f, './oeil/urls6.csv')
#for f in os.listdir('./oeil/search_query_results/all/7th_term/'):
#    parse_urls('./oeil/search_query_results/all/7th_term/' + f, './oeil/urls7.csv')
#remove_duplicates('./oeil/urls6.csv', './oeil/urls6.csv')
#remove_duplicates('./oeil/urls7.csv', './oeil/urls7.csv')
#parse_info('./oeil/urls6.csv', './oeil/metadata6.csv')
#parse_info('./oeil/urls7.csv', './oeil/metadata7.csv')

#for f in os.listdir('./oeil/search_query_results/all/6th_term/'):
#    parse_urls('./oeil/search_query_results/all/6th_term/' + f, './oeil/urls67.csv')
#for f in os.listdir('./oeil/search_query_results/all/7th_term/'):
#    parse_urls('./oeil/search_query_results/all/7th_term/' + f, './oeil/urls67.csv')
#remove_duplicates('./oeil/urls67.csv', './oeil/urls67.csv')
#parse_info('./oeil/urls67.csv', './oeil/metadata67.csv')