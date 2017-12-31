import requests
import urllib
import csv
import os.path
import re
from bs4 import BeautifulSoup
from pg import DB

db = DB(dbname="interactive_brokers", host="localhost", port=5432, user="neurotrader", passwd="profit")

def getExchange(page):
	hdr = {'User-Agent': 'Mozilla/5.0'}
	request = requests.get(page, headers=hdr)
	soup = BeautifulSoup(request.content, "html.parser")
	box = soup.find('table', {'class': 'infobox vcard'})
	#print str(box)
	if re.search('NASDAQ', str(box)) != None:
		return 'NASDAQ'
	elif re.search('NYSE', str(box)) != None:
		return 'NYSE'
	else:
		return None

wikiurl = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
def scrape_list(url):
	hdr = {'User-Agent': 'Mozilla/5.0'}
	request = requests.get(url, headers=hdr)
	soup = BeautifulSoup(request.content, "html.parser")
	
	table = soup.find('table', {'class': 'wikitable sortable'})
	sector_tickers = dict()
	for row in table.findAll('tr'):
		col = row.findAll('td')
		if len(col) > 0:
			#print(col[1].get('title', 'No title attrbute'))
			ticker = col[0].string.strip().replace('.', '-')
			security = col[1].findAll('a')[0].get("title", "").replace("'","").replace("(page does not exist)", "").replace("(company)","").replace("(New)","").replace("brand","").replace("(IT services company)","").strip()
			sector = col[3].string
			industry = col[4].string
			stock_page = 'http://en.wikipedia.org'+col[1].findAll('a')[0].get("href","")
			exchange = getExchange(stock_page)
			
			if ticker!=None and security!=None and sector!=None and industry!=None and exchange!=None:
				db.query("""INSERT INTO stocks (symbol, security, exchange, sector, industry) VALUES ('%s','%s','%s','%s','%s')"""%(ticker, security, exchange, sector, industry))
				print "adding ", ticker, "|", security, "|", exchange, "|", sector, "|", industry
			
	return sector_tickers
			

scrape_list(wikiurl)
