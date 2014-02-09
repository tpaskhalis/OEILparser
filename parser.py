#from bs4 import BeautifulSoup
import bs4
import csv
import urllib2
import os.path

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
    
def parse_info(inputcsv_path, outputcsv_path):
    urllist = open(inputcsv_path, "r")
    infolist = open(outputcsv_path, "w")
    csvwriter = csv.writer(infolist)
    csvwriter.writerow(['Code','Title', 'Link', 'CommitteeAbr', 
                        'CommitteeFull', 'Rapporteur Party', 'Rapporteur',
                        'Date Committee Draft Report', 'Date Committee report tabled for plenary'
                        'Date Text adopted by Parliament', 'Code Text adopted by Parliament',
                        'Link Text adopted by Parliament', 'Link Summary'])    
    
    url = urllist.readline()[:-2]
    while url:    
        page = urllib2.urlopen(url)
        soup = bs4.BeautifulSoup(page.read())
        table = soup.find('table', id='basic_information')
        reference = table.find('span', 'basic_reference')    
        title = table.find('p', 'basic_title')
        
        table = soup.find('table', id='key_players')
        acronym = table.find('acronym', 'acronym_nohelp')
        committee = table.find('span', 'players_committee_text')
        group = table.find('span', 'tiptip')
        rapporteur = table.find('span', 'players_rapporter_text')
        
        table = soup.find('table', id='doc_gateway')
        for descendant in table.tbody.descendants:
#            This workaround works for now but I don't like isinstance test
            if isinstance(descendant, bs4.element.Tag) and descendant.td:
                if descendant.td.string == u'Committee draft report':
                    draftdate = descendant.find('td', 'event_column_r column_top')
                elif descendant.td.string == u'Committee report tabled for plenary, single reading':
                    reportdate = descendant.find('td', 'event_column_r column_top')
                elif descendant.td.string == u'Text adopted by Parliament, single reading':
                    adoptednum = descendant.find('td', 'event_column_document column_top')
                    adopteddate = descendant.find('td', 'event_column_r column_top')
                    summaryurl = descendant.find('a', title='Summary for Text adopted by Parliament, single reading')
                else:
                    continue
        
        csvwriter.writerow(reference.contents + title.contents + [url] + acronym.contents 
                            + [next(committee.stripped_strings)] + group.contents 
                            + [rapporteur.string] + draftdate.contents + reportdate.contents
                            + adopteddate.contents + [next(adoptednum.stripped_strings)] 
                            + [unicode(adoptednum.a['href'])] + [(unicode('http://www.europarl.europa.eu/') + summaryurl['href'])])
        url = urllist.readline()[:-2]
    urllist.close()
    infolist.close()
    
#for num in range(2004,2008):
#    parse_links('./data/' + str(num) + '.xml', './data/urls.csv')
#parse_links('./data/2008.rss', './data/urls.csv')
#parse_links('./data/2009.xml', './data/urls.csv')
#parse_links('./data/20042009.rss', './data/urls.csv')
#parse_links('./data/20092014.xml', './data/urls.csv')

#parse_info("./data/short_urls.csv", "./data/short_info.csv")