#!/usr/bin/python

from pg import DB

db = DB(dbname="interactive_brokers", host="localhost", port=5432, user="neurotrader", passwd="profit")
tables = ("benchmark", "fundamental_ratios", "histogram", "tick", "tick_history")
for table in tables:
	deletequery = "DELETE FROM %s"%table
	resetquery = "ALTER SEQUENCE %s_index_seq RESTART WITH 1"%table
	db.query(deletequery)
	try:
		db.query(resetquery)
	except:
		continue
