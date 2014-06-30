import bs4
import csv
import os
import fnmatch
import regex as re
import pandas as pd
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

#7th parliamentary term, 2009-2014, surname and id
def parse_stats(url, policy, outputcsv_path):        
    page = urllib2.urlopen(url)
    soup = bs4.BeautifulSoup(page.read())
    table = soup.find('table', 'standard_table')
    meps = table.tbody.findAll('tr')
    with open(outputcsv_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['name', 'id', 'grouployalty.' + policy, 'partyloyalty.' + policy, 'rollcall.' + policy])
        for mep in meps:
            tds = mep.findAll('td')
            divs = tds[0].findAll('div')
            name = divs[1].contents[0]
            id = re.findall(re.compile('[0-9]{1,10}\.jpg'), divs[0].img.attrs['src'])
            id[0] = re.sub(re.compile('\.jpg'), '', id[0])
            loyaltygroup = tds[1].text
            loyaltyparty = tds[2].text
            rollcall = tds[3].text
            stats = [re.sub(re.compile('\s'), '', s) for s in [loyaltygroup, loyaltyparty, rollcall]]
            csvwriter.writerow([name] + id + stats)
            
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/0/2009-07-14/2014-07-14//', 'all', './votewatch/statistics/mepsall.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/2/2009-07-14/2014-07-14//', 'agri', './votewatch/statistics/mepsagri.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/3/2009-07-14/2014-07-14//', 'budg', './votewatch/statistics/mepbudg.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/4/2009-07-14/2014-07-14//', 'budgcont', './votewatch/statistics/mepsbudgcont.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/5/2009-07-14/2014-07-14//', 'civil', './votewatch/statistics/mepscivil.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/6/2009-07-14/2014-07-14//', 'const', './votewatch/statistics/mepsconst.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/7/2009-07-14/2014-07-14//', 'cult', './votewatch/statistics/mepscult.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/8/2009-07-14/2014-07-14//', 'develop', './votewatch/statistics/mepsdevelop.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/9/2009-07-14/2014-07-14//', 'econ', './votewatch/statistics/mepsecon.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/10/2009-07-14/2014-07-14//', 'employ', './votewatch/statistics/mepsemploy.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/11/2009-07-14/2014-07-14//', 'environ', './votewatch/statistics/mepsenviron.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/12/2009-07-14/2014-07-14//', 'fish', './votewatch/statistics/mepsfish.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/13/2009-07-14/2014-07-14//', 'foreign', './votewatch/statistics/mepsforeign.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/14/2009-07-14/2014-07-14//', 'gender', './votewatch/statistics/mepsgender.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/15/2009-07-14/2014-07-14//', 'indust', './votewatch/statistics/mepsindust.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/16/2009-07-14/2014-07-14//', 'intern', './votewatch/statistics/mepsintern.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/17/2009-07-14/2014-07-14//', 'internreg', './votewatch/statistics/mepsinternreg.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/18/2009-07-14/2014-07-14//', 'international', './votewatch/statistics/mepsinternational.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/19/2009-07-14/2014-07-14//', 'legal', './votewatch/statistics/mepslegal.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/20/2009-07-14/2014-07-14//', 'petition', './votewatch/statistics/mepspetition.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/21/2009-07-14/2014-07-14//', 'region', './votewatch/statistics/mepsregion.csv')
parse_stats('http://www.votewatch.eu/en/voting-statistics.html#/#0/22/2009-07-14/2014-07-14//', 'trans', './votewatch/statistics/mepstrans.csv')

df = pd.read_csv('./votewatch/statistics/mepsall.csv', encoding = 'utf-8')
for f in os.listdir('./votewatch/statistics/'):
    if fnmatch.fnmatch(f, '*all.csv'):
        continue
    else:
        temp = pd.read_csv(os.path.join('./votewatch/statistics/', f), encoding = 'utf-8')
        df = pd.merge(df, temp, on = ['name', 'id'], how = 'outer')
df.to_csv('./votewatch/mepscomplete.csv', index = False)