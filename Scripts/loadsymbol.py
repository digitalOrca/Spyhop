import requests
import urllib
import csv
import os.path
import re
from bs4 import BeautifulSoup
from pg import DB

db = DB(dbname="interactive_brokers", host="localhost", port=5432, user="neurotrader", passwd="profit")

f = open('/home/meng/Projects/NeuroTrader/Misc/Stocks/NASDAQ_stocks.csv','r')
dual_listed = []
for i in f:
	item = i.split('\t')
	symbol = item[0]
	if symbol == 'Symbol':
		continue
	exchange = 'NASDAQ'
	name = item[1].replace("'", "")
	sector = item[5].replace("n/a", "NULL")
	if sector != "NULL":
		sector = "'"+sector+"'"
	industry = item[6].replace("n/a", "NULL")
	if industry != "NULL":
		industry = "'"+industry+"'"
	try:
		db.query("""INSERT INTO security (symbol, exchange, name, sector, industry) VALUES ('%s','%s','%s',%s,%s)"""%(symbol, exchange, name, sector, industry))
	except:
		dual_listed.append(symbol)
		
for item in dual_listed:
	db.query("DELETE FROM security WHERE symbol='%s'"%item)
	print "removing %s"%item


