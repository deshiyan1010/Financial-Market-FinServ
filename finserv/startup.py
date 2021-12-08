
import os

from multitasking import createPool
os.environ.setdefault("DJANGO_SETTINGS_MODULE","finserv.settings")

from datetime import datetime
from datetime import timedelta

import django 
django.setup()

import pandas as pd
from portfolio import models as pModels
from django.utils.dateparse import parse_datetime

import yfinance as yf

ALL_ASSETS = {
    'Apple':'AAPL',
    'Microsoft':'MSFT',
    'Google':'GOOG',
    'Amazon':'AMZN',
    'Facebook':'FB',
    'Nvidia':'NVDA',
    'JP Morgan Chase':'JPM',
    'Visa':'V',
    'Johnson and Johnson':'JNJ',
    'Analog Devices':'ADI',
    'Bank Of America':'BAC',
    'Walmart':'WMT',
    'Procter & Gamble':'PG',
    'Alibaba':'BABA',
    'Mastercard':'MA',
    'Adobe':'ADBE',
    'Pfizer':'PFE',
    'Netflix':'NFLX',
    'Walt Disney Company':'DIS',
    'Nike':'NKE',
    'SalesForce':'CRM',
    'Totota Motor':'TM',
    'Oracle':'ORCL',
    'Cisco':'CSCO',
    "NSE":'^NSEI',
    "BSE":'^BSESN',
    "SnP500":'^GSPC',
    "Bitcoin":'BTC-USD',
    "Ethereum":'ETH-USD',
    "Tesla":'TSLA',
}

ALL_ASSETS_REV = {y:x for x,y in ALL_ASSETS.items()}

class Startup():
    
    def __init__(self) -> None:
        try:
            self.lastUpdated = (pModels.AssetPriceMovements.objects.latest('date')).date.strftime('%Y-%m-%d')
        except:
            self.lastUpdated = '2021-12-01'

        today = datetime.now().strftime("%Y-%m-%d")
        print(self.lastUpdated)
        if self.lastUpdated!=today:
            self.syncData()

    def syncData(self):

        try:
            data = yf.download(" ".join(list(ALL_ASSETS.values())), start=self.lastUpdated)['Adj Close'].dropna().reset_index()
            for asset in data.columns[1:]:
                tick_obj,created = pModels.AssetsDetails.objects.get_or_create(assetName=ALL_ASSETS_REV[asset],assetTicker=asset)
                if created:
                    tick_obj.save()

                for i,row in data[['Date',asset]].iterrows():
                    row = row.to_dict()
                    date= datetime.strptime(str(row['Date'].date()), '%Y-%m-%d')
                    p = pModels.AssetPriceMovements.objects.create(ticker=tick_obj,date=date,adj_close=row[asset])
                    p.save()

        except:
            pass