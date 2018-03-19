#!/usr/bin/python3

import requests
import urllib
import csv
import os.path
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2 as pg

connection = pg.connect("""dbname='interactive_brokers'
                           host='/run/postgresql/'
                           user='neurotrader'
                           password='profit'""")
connection.autocommit = True
cursor = connection.cursor()

data = pd.read_csv('/home/meng/Downloads/SP500.csv')

prev_close = "NULL"

for d in data.iterrows():
    date = d[1].loc["Date"]
    open_price = d[1].loc["Open"]
    
    query = """INSERT INTO benchmarks (date, snp500_prev_close, snp500_open) VALUES ('%s',%s,%s)"""%(date, prev_close, open_price)
    print(query)
    if prev_close != "NULL":    
        try:
            cursor.execute(query)
        except:
            print("failed:", date)
    
    prev_close = d[1].loc["Close"]

    
    
    #try:
    #    db.query("""INSERT INTO benchmarks (date, snp500_prev_close, snp500_open) VALUES ('%s',%s,%s)"""%(date, prev_close, o))
    #except:
    #   print("failed:", t)
       
    #prev_close = c
		
#for item in dual_listed:
#	db.query("DELETE FROM security WHERE symbol='%s'"%item)
#	print "removing %s"%item
