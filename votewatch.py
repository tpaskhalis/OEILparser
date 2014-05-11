import bs4
import csv
import re
import urllib2
import time

#7th parliamentary term, 2009-2014, VoteWatch
page = urllib2.urlopen('http://www.votewatch.eu//en/european-parliament-members.html?limit=1000')
soup = bs4.BeautifulSoup(page.read())
table = soup.find('table', 'standard_table narrow_table')
rows = table.tbody.findAll('tr')

meps = [[i.a.div.text, i.a['href']] for i in rows[:-1]]

with open('./votewatch/meps7.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    for mep in meps:    
        perspage = urllib2.urlopen(mep[1])
        perssoup = bs4.BeautifulSoup(perspage.read())
        dd = perssoup.find('dd', text = re.compile('Start of'))
        dt = dd.findNextSibling()
        mandate = re.findall(re.compile('[0-9]{2}.[0-9]{2}.[0-9]{4}'), dt.text)
        csvwriter.writerow(mep + mandate)
        time.sleep(1)
        
#6th parliamentary term, 2004-2009, Old VoteWatch
page = urllib2.urlopen('http://old.votewatch.eu/cx_meps_statistics.php')
soup = bs4.BeautifulSoup(page.read())
div = soup.find('div', style = 'width:734px;height:500px;overflow:auto;overflow-x:hidden;overflow-y:scroll;')
table = div.table
urls = table.findAll('a')

meps = [[i.text, 'http://old.votewatch.eu/' + i['href']] for i in urls if urls.index(i) % 2 == 1]

with open('./votewatch/meps6.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    for mep in meps:
        perspage = urllib2.urlopen(mep[1])
        perssoup = bs4.BeautifulSoup(perspage.read())
        td = perssoup.find('td', text = re.compile('Start of'))
        mandate = re.findall(re.compile('[0-9]{2}.[0-9]{2}.[0-9]{4}'), td.text)
        csvwriter.writerow(mep + mandate)
        time.sleep(1)