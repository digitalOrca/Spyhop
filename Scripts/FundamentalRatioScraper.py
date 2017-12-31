import requests
import urllib
import csv
import os.path
import re
from bs4 import BeautifulSoup
from pg import DB

#db = DB(dbname="interactive_brokers", host="localhost", port=5432, user="neurotrader", passwd="profit")

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

wikiurl = 'https://interactivebrokers.github.io/tws-api/fundamental_ratios_tags.html#gsc.tab=0'
def scrape_list(url):
	hdr = {'User-Agent': 'Mozilla/5.0'}
	request = requests.get(url, headers=hdr)
	soup = BeautifulSoup(request.content, "html.parser")
	
	table = soup.find('table', {'class': 'doxtable'})
	sector_tickers = dict()
	query = ''
	for row in table.findAll('tr'):
		cols = row.findAll('td')
		if len(cols) > 0:
			columns = cols[0].string + " REAL, "
			query += columns
	print query	

scrape_list(wikiurl)
