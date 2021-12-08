from pygooglenews import GoogleNews

import yfinance as yf

from portfolio import models as pModels

def getNews():
    gn = GoogleNews(lang = 'en')
    news = gn.search('crypto OR indian stock market OR BSE OR NSE OR NASDAQ OR stocks OR shares OR SEBI OR SEC',when='24h')['entries']
    
    sorted_news = [(x['title'],x['link'],x['published']) for x in sorted(news,key = lambda i: i['published'],reverse=True)]

    return sorted_news

def getTickerData():
    TOP_ASSETS = ['^NSEI','^BSESN','^GSPC','BTC-USD','ETH-USD','TSLA']

    topAssets = {}
    topDF = yf.download(" ".join(TOP_ASSETS),period='1d')['Adj Close']
    topAssets = topDF.to_dict()
    return topAssets

def getNetworthHist(userObj):
    assets_obj = pModels.Assets.objects.filter(port__user=userObj)
