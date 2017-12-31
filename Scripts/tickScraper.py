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

wikiurl = 'https://interactivebrokers.github.io/tws-api/tick_types.html#gsc.tab=0'
def scrape_list(url):
	hdr = {'User-Agent': 'Mozilla/5.0'}
	request = requests.get(url, headers=hdr)
	soup = BeautifulSoup(request.content, "html.parser")
	
	table = soup.find('table', {'class': 'doxtable'})
	sector_tickers = dict()
	for row in table.findAll('tr'):
		col = row.findAll('td')
		if len(col) > 0:
			#print(col[1].get('title', 'No title attrbute'))
			name = col[0].string.strip().lower().replace(' ', '_')
			tickid = int(col[1].string)
			#if col[4].string == '-':
			#	generic = None
			#else:
			try:
				generic = int(col[4].string.split('or')[0])
			except:
				generic = None
				
			if name!=None and tickid!=None:
				if generic != None:
					db.query("""INSERT INTO tick_type (id, name, generic) VALUES (%d,'%s', %d)"""%(tickid, name, generic))
				else:
					db.query("""INSERT INTO tick_type (id, name, generic) VALUES (%d,'%s', NULL)"""%(tickid, name))
				print "adding ", tickid, "|", name, "|", generic
						

scrape_list(wikiurl)
