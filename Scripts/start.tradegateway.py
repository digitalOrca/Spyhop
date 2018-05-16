#!/usr/bin/python

import sys
import pandas as pd
import datetime

today = datetime.datetime.now()
holidays = pd.read_csv("/home/meng/Projects/NeuroTrader/Models/Config/TradingHoliday.csv").Date.apply(lambda x: str(x).strip()).tolist()

if len(sys.argv) < 2:
    print("Too few argument!")

if today.weekday() <= 4 and today.strftime("%Y-%m-%d") not in holidays:
    /home/meng/Projects/NeuroTrader/Scripts/start.tradegateway.sh sys.argv[1]
else:
    print("Today is not a trading day!!!")
