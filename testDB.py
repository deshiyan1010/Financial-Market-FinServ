# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE","finserv.settings")
# from django.utils.timezone import get_current_timezone
# from datetime import datetime

# import django 
# django.setup()

# import pandas as pd
# from portfolio.models import AssetPriceMovements,Assets
# from django.utils.dateparse import parse_datetime

# try:
#     tick_obj = Assets.objects.create(assetName='Microsoftx',assetTicker='MSSSS')
#     tick_obj.save()
# except:
#     tick_obj = Assets.objects.get(assetName='Microsoftx')

# tz = get_current_timezone()
# dt = tz.localize(datetime.strptime('2016-10-03', '%Y-%m-%d'))

# p = AssetPriceMovements.objects.create(ticker=tick_obj,adj_close=10,date=dt)
# p.save()
# dt = tz.localize(datetime.strptime('2017-10-03', '%Y-%m-%d'))
# p = AssetPriceMovements.objects.create(ticker=tick_obj,adj_close=10,date=dt)
# p.save()

# dt = tz.localize(datetime.strptime('2017-10-03', '%Y-%m-%d'))

# print(AssetPriceMovements.objects.latest('date').date.strftime())





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

import random

port = pModels.Assets.objects.get(assetName="Johnson and Johnson")
print(port.assetName)
# asset = pModels.Assets.objects.all()
# for i in range(5):
#     p = pModels.PortfolioAssets.objects.create(port=port,asset=asset[random.randint(0,31)],usdSpent=1000,assetQuantity=10)
#     p.save()

# for p in port:
#     if len(p.uPortName)==0:
#         p.delete()
# print(port.id)

# ALL_ASSETS = {
#     'Apple':'AAPL',
#     'Microsoft':'MSFT',
#     'Google':'GOOG',
#     'Amazon':'AMZN',
#     'Facebook':'FB',
#     'Nvidia':'NVDA',
#     'JP Morgan Chase':'JPM',
#     'Visa':'V',
#     'Johnson and Johnson':'JNJ',
#     'Analog Devices':'ADI',
#     'Bank Of America':'BAC',
#     'Walmart':'WMT',
#     'Procter & Gamble':'PG',
#     'Alibaba':'BABA',
#     'Mastercard':'MA',
#     'Adobe':'ADBE',
#     'Pfizer':'PFE',
#     'Netflix':'NFLX',
#     'Walt Disney Company':'DIS',
#     'Nike':'NKE',
#     'SalesForce':'CRM',
#     'Totota Motor':'TM',
#     'Oracle':'ORCL',
#     'Cisco':'CSCO',
#     "NSE":'^NSEI',
#     "BSE":'^BSESN',
#     "SnP500":'^GSPC',
#     "Bitcoin":'BTC-USD',
#     "Ethereum":'ETH-USD',
#     "Tesla":'TSLA',
# }

# ALL_ASSETS_REV = {y:x for x,y in ALL_ASSETS.items()}

# class Startup():
    
#     def __init__(self) -> None:
#         try:
#             self.lastUpdated = (pModels.AssetPriceMovements.objects.latest('date')).date.strftime('%Y-%m-%d')
#         except:
#             self.lastUpdated = '2021-12-01'

#         today = datetime.now().strftime("%Y-%m-%d")
#         if self.lastUpdated!=today:
#             self.syncData()

#     def syncData(self):


#         data = yf.download(" ".join(list(ALL_ASSETS.values())), start=self.lastUpdated)['Adj Close'].dropna().reset_index()
#         print(data)
#         for asset in data.columns[1:]:
#             tick_obj,created = pModels.Assets.objects.get_or_create(assetName=ALL_ASSETS_REV[asset],assetTicker=asset)
#             if created:
#                 tick_obj.save()

#             for i,row in data[['Date',asset]].iterrows():
#                 row = row.to_dict()
#                 date= datetime.strptime(str(row['Date'].date()), '%Y-%m-%d')
#                 p = pModels.AssetPriceMovements.objects.create(ticker=tick_obj,date=date,adj_close=row[asset])
#                 p.save()
# Startup()

# from django.contrib.auth.models import User
# def gainChartUnrealizedProfitPortfolio(portObj):
#     port_assets_list = pModels.PortfolioAssets.objects.filter(port=portObj,sold=False)
#     bought_on = portObj.created_on

#     today = datetime.now()
#     cday = bought_on

#     line = []
#     netAssetWorth = 0
#     perchg = 0
#     profit = 0

#     datewise_dict = {}
#     datewise_dict_cum = {}


#     cday = cday.replace(hour=0,minute=0,second=0)

#     cday = cday.replace(hour=0,minute=0,second=0)


#     while cday<today-timedelta(days=1):
#         pro_details = {}
#         for asset in port_assets_list:
#             try:
#                 assCurrPrice = pModels.AssetPriceMovements.objects.get(ticker=asset.asset,date__range=(cday,cday+timedelta(days=1))).adj_close
#                 perchg = (assCurrPrice/asset.usdSpent)*asset.assetQuantity
#                 netAssetWorth = perchg * asset.usdSpent
#                 profit = netAssetWorth - asset.usdSpent
#             except Exception as e:
#                 try:
#                     netAssetWorth = datewise_dict[cday][asset]['netWorth']
#                     profit = datewise_dict[cday][asset]['profit']
#                     # print("copied")
#                 except:
#                     # print("E2")
#                     pass
#                 # print("E1")
#                 pass
#             pro_details[asset] = {
#                 'netWorth':netAssetWorth,
#                 'profit':profit,
#                 # 'perchg':perchg
#             }
#         cday += timedelta(days=1)

#         datewise_dict[cday] = pro_details
    
#     for key,val in datewise_dict.items():
#         netAssetWorth = 0
#         profit = 0
#         for _,v2 in val.items():
#             netAssetWorth += v2['netWorth']
#             profit += v2['profit']
        
#         datewise_dict_cum[key] = {
#             'netWorth':netAssetWorth,
#             'profit':profit
#         }
    
    
#     return datewise_dict,datewise_dict_cum


# def gainChartUnrealizedProfit(userObj):
#     port_list = pModels.Portfolio.objects.filter(user=userObj,sold=False).order_by('created_on')
    
#     days_stat_dict = {}

#     for port in port_list:
#         portGainsDict,_ = gainChartUnrealizedProfitPortfolio(port)
#         for date,assetsDict in portGainsDict.items():
#             tempDict = days_stat_dict.get(date,None)
#             if tempDict==None:
#                 days_stat_dict[date] = {
#                     'profit':0,
#                     'netWorth':0,
#                 }
#             for _,val in assetsDict.items():
#                 for key2,val2 in val.items():
#                     days_stat_dict[date][key2] += val2
    
#     return days_stat_dict





#     # print((starting_date-today).days)

# from pprint import pprint

# uo = User.objects.all()[0]
# portObj = pModels.Portfolio.objects.get(user=uo)
# pprint(gainChartUnrealizedProfitPortfolio(portObj))
# pprint(gainChartUnrealizedProfit(uo))
