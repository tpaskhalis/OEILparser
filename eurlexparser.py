#This script requires Python2.7+ and library bs4(which is not part of standard installation).
import bs4
import csv
import re
import os
import urllib2
import time

errors = 'Errors: '
def parse_eurlex_text(inputcsv_path, outputfolder):
    global errors
    with open(inputcsv_path, 'r') as f:
        namepattern = re.compile(r'^Proposal for a Regulation of the European Parliament', re.UNICODE)
        celexlist = [row[0] for row in csv.reader(f, delimiter=',') if re.match(namepattern, row[1])]
        urldict = {celex:'http://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:' + celex + '&rid=1' for celex in celexlist}
    for celex, url in urldict.iteritems():
        page = urllib2.urlopen(url)
        soup = bs4.BeautifulSoup(page.read())
        content = soup.find('div', id='TexteOnly')
        try:
            paragraphs = content.findAll('p')
        except AttributeError:
            errors += celex + ', '
            continue
        paragraphs = [p.contents[0] for p in paragraphs if p.contents]
        whereas = re.compile(r'Whereas:|Whereas', re.UNICODE)
        index = [i for i, paragraph in enumerate(paragraphs) if re.match(whereas, paragraph)]
        if index:
            paragraphs = paragraphs[index[0]:]
            clearpattern = re.compile(r'^[\s\n\t\"]*|[\s\n\t\"]*$', re.UNICODE)
            paragraphs = [re.sub(clearpattern, u'', p) for p in paragraphs]
            with open(os.path.join(outputfolder, celex + u'.tsv'), 'w') as f:
                csvwriter = csv.writer(f, dialect='excel-tab')
                for p in paragraphs:
                    csvwriter.writerow([p])
            time.sleep(1)
        else:
            errors += celex + ', '
    print errors
    
for f in os.listdir('./EUR-Lex/search_query_results/'):
    parse_eurlex_text('./EUR-Lex/search_query_results/' + f, './EUR-Lex/text')