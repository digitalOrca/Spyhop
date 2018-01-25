#!/usr/bin/python2.7

import requests
import urllib
import csv
import os.path
import re
from bs4 import BeautifulSoup
from pg import DB

db = DB(dbname="interactive_brokers", host="localhost", port=5432, user="neurotrader", passwd="profit")

f = open('/home/meng/Downloads/benchmark.csv','r')

prev_close = "NULL"

for line in f:
    t = line.strip().split(",")
    date = t[0]
    if date == "Date":
        continue
    o = t[1]
    c = t[4]
    
    try:
        db.query("""INSERT INTO benchmarks (date, snp500_prev_close, snp500_open) VALUES ('%s',%s,%s)"""%(date, prev_close, o))
    except:
       print("failed:", t)
       
    prev_close = c
		
f.close()
#for item in dual_listed:
#	db.query("DELETE FROM security WHERE symbol='%s'"%item)
#	print "removing %s"%item
