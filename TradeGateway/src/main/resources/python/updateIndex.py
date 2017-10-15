#!/usr/bin/python

import sys
from datetime import date
import requests
from bs4 import BeautifulSoup
sys.path.append("/home/meng/Projects/NeuroTrader/Common/")
from DBUtils import DBConnect


snp500url = "https://finance.google.com/finance?q=INDEXSP:.INX"
hdr = {'User-Agent': 'Mozilla/5.0'}
request = requests.get(snp500url, headers=hdr)
soup = BeautifulSoup(request.content, "html.parser")
span = soup.find('span', {'id': 'ref_626307_l'})
benchmark = (float)(span.string.replace(",",""))

db = DBConnect()
date = date.today().isoformat()
query = "INSERT INTO benchmark (date, snp500) VALUES ('%s',%s)"%(date,benchmark)

try:
    db.update(query)
except:
    print "Update S&P500 benchmark failed"
