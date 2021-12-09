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

def getNetWorthGainUnrealized(userObj):
    assets_obj = pModels.Assets.objects.filter(port__user=userObj)
    total_usd_spent = 0
    total_asset_dict = {}

    for assetO in assets_obj:
        if assetO.sold!=None:
            total_usd_spent += assetO.usdSpent
            det = total_asset_dict.get(assetO,None)
            if det==None:
                total_asset_dict[assetO] = {'quantity_quote':0,
                                            'quantity_usd':0}
            
            total_asset_dict[assetO]['quantity_quote'] += assetO.assetQuantity
            total_asset_dict[assetO]['quantity_usd'] += assetO.usdSpent
    
    gains_dict = {}

    for assetO,details in total_asset_dict.items():
        avg_bought_price = details['quantity_quote']/details['quantity_usd']
        current_price = pModels.AssetPriceMovements.objects.filter(ticker=assetO.asset).latest('date').adj_close
        gains_dict[assetO] = (current_price/avg_bought_price)-1
    
    return total_asset_dict,gains_dict


def gainChartRealized(userObj):
    assets_obj = pModels.Assets.objects.filter(port__user=userObj,buy_sell_order=False).order_by('created_on')
    line_chart = []
    sold_dict = {}

    for assObj in assets_obj:
        if assObj.sold_on!=None:
            sold_dict[assObj.sold_on] = sold_dict.get(assObj.sold_on,[]).append(assObj)

    for date,assObjList in sold_dict.items():
        pass


def gainChartUnrealized(userObj):
    assets_obj = pModels.Assets.objects.filter(port__user=userObj).order_by('created_on')
    line_chart = []
    sold_dict = {}

    for assObj in assets_obj:
        if assObj.sold_on!=None:
            sold_dict[assObj.sold_on] = sold_dict.get(assObj.sold_on,[]).append(assObj)

        pass

def getLinePlot(assetName: str):
    assetDetailsObj = pModels.AssetsDetails.objects.get(assetName=assetName)
    assets_obj = pModels.AssetPriceMovements.objects.filter(ticker=assetDetailsObj).order_by('date')
    line_chart = []

    for priceO in assets_obj:
        line_chart.append(priceO.adj_close)
    
    return line_chart


def calcPortfolioGain(portObj):
    assets_obj = pModels.Assets.objects.filter(port=portObj)
    total_usd_spent = 0
    total_asset_dict = {}

    for assetO in assets_obj:
        if assetO.sold!=None:
            total_usd_spent += assetO.usdSpent
            det = total_asset_dict.get(assetO,None)
            if det==None:
                total_asset_dict[assetO] = {'quantity_quote':0,
                                            'quantity_usd':0,
                                            }
            
            total_asset_dict[assetO]['quantity_quote'] += assetO.assetQuantity
            total_asset_dict[assetO]['quantity_usd'] += assetO.usdSpent


    gains_dict = {}
    totalCurrWorth = 0
    totalCurrProfit = 0
    for assetO,details in total_asset_dict.items():
        avg_bought_price = details['quantity_usd']/details['quantity_quote']
        current_price = pModels.AssetPriceMovements.objects.filter(ticker=assetO.asset).latest('date').adj_close
        perGain = (current_price/avg_bought_price)-1
        
        profit = details['quantity_usd']*perGain
        currentAssetWorth = details['quantity_usd']+profit

        totalCurrWorth += currentAssetWorth
        totalCurrProfit += profit
        gains_dict[assetO] = {
            'perGain':perGain,
            'profit':profit,
            'currentAssetWorth':currentAssetWorth,
        }

    return gains_dict,totalCurrProfit,totalCurrWorth

def getPortList(userObj):
    portList = pModels.Portfolio.objects.get(user=userObj).order_by('created_on')

    portDetails = {}
    for port in portList:
        gains_dict,totalCurrProfit,totalCurrWorth = calcPortfolioGain(port)
        portDetails[port] = {
            'gainDict':gains_dict,
            'totalCurrWorth':totalCurrWorth,
            'totalCurrProfit':totalCurrProfit
        }
    return portDetails