#!/usr/bin/python3

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
import traceback

class DBConnect:
	
    def __init__(self):
        self.connection = pg.connect("""dbname='interactive_brokers'
                                        user='neurotrader'
                                        password='profit'""")
        self.connection.autocommit = True
    
	
    def query(self, query, index='symbol'):
        dataframe = None
        try:
            dataframe = psql.read_sql(query, self.connection)
            if index is not None:
                dataframe.set_index(index, inplace=True)
        except:
            traceback.print_exc()
        return dataframe
    
    
    def update(self, query):
        try:
            cur = self.connection.cursor()
            cur.execute(query)
        except:
            print("Database update operation failed on query:"%query)
            #TODO: USE LOG CAPTURING LATER
