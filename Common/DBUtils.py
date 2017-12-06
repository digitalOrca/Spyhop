#!/usr/bin/python3

"""DBUtils.py
Description:
    database function wrapper utility
"""

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
import traceback

class DBConnect:
	
    """Constructor
    """
    def __init__(self):
        self.connection = pg.connect("""dbname='interactive_brokers'
                                        host='/run/postgresql/'
                                        user='neurotrader'
                                        password='profit'""")
        self.connection.autocommit = True
    
    """query
	Description:
	    issue query to the database and returning result
	Input:
	    query: query string
	    index: index of the returned dataframe
    """
    def query(self, query, index='symbol'):
        dataframe = None
        try:
            dataframe = psql.read_sql(query, self.connection)
            if index is not None:
                dataframe.set_index(index, inplace=True)
        except:
            traceback.print_exc()
        return dataframe
    
    """update
    Description:
        update the database
    Input:
        query: query string
    """
    def update(self, query):
        try:
            cur = self.connection.cursor()
            cur.execute(query)
        except:
            print("Database update operation failed on query:"%query)
            #TODO: USE LOG CAPTURING LATER
