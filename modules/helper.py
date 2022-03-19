from django.contrib.auth.decorators import user_passes_test
from pygooglenews import GoogleNews

import yfinance as yf

from portfolio import models as pModels

from datetime import datetime
from datetime import timedelta

from finserv.startup import ALL_ASSETS_REV

from pprint import pprint


def getNews():
    gn = GoogleNews(lang = 'en')
    news = gn.search('crypto OR indian stock market OR BSE OR NSE OR NASDAQ OR stocks OR shares OR SEBI OR SEC',when='24h')['entries']
    
    sorted_news = [(x['title'],x['link'],x['published']) for x in sorted(news,key = lambda i: i['published'],reverse=True)]

    return sorted_news

def getTickerData():
    TOP_ASSETS = ['^NSEI','^BSESN','^GSPC','BTC-USD','ETH-USD','TSLA']

    topAssets = {}
    topDF = yf.download(" ".join(TOP_ASSETS),period='3d').reset_index()[['Adj Close','Close']].fillna(method='ffill')['Close']
    
    perChg = (topDF.pct_change().iloc[-1]*100).to_dict()
    topAssets = topDF.iloc[-1].to_dict()

    fin_dict = {}

    for k1,v1 in topAssets.items():
        fin_dict[ALL_ASSETS_REV[k1]] = {'price':round(v1,2),'perchg':round(perChg[k1],2)}

    return fin_dict

def getNetWorthGainUnrealized(userObj):
    assets_obj = pModels.PortfolioAssets.objects.filter(port__user=userObj,sold=False)
    total_usd_spent = 0
    total_asset_dict = {}

    for assetO in assets_obj:
        total_usd_spent += assetO.usdSpent
        det = total_asset_dict.get(assetO,None)
        if det==None:
            total_asset_dict[assetO] = {'quantity_quote':0,
                                        'quantity_usd':0}
        
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

    return total_asset_dict,gains_dict,totalCurrProfit,totalCurrWorth


def gainChartRealized(userObj):
    assets_obj = pModels.PortfolioAssets.objects.filter(port__user=userObj,sold=True).order_by('sold_on')
    line_chart = []
    sold_dict = {}

    for assObj in assets_obj:
        sold_dict[assObj.sold_on] = sold_dict.get(assObj.sold_on,[]).append(assObj)

    sold_dict2 = {}
    for date,assObjList in sold_dict.items():
        usd_bought_at = 0
        sold_for = 0
        for asset in assObjList:
            usd_bought_at += asset.usdSpent
            sold_for += asset.sold_for_usd
        sold_dict2[date] = {
            'bought_at': usd_bought_at,
            'sold_for':sold_for,
        }
    return sold_dict2


def getLinePlot(assetName: str):
    assetDetailsObj = pModels.Assets.objects.get(assetName=assetName)
    assets_obj = pModels.AssetPriceMovements.objects.filter(ticker=assetDetailsObj).order_by('date')
    line_chart = []
    date = []
    for priceO in assets_obj:
        line_chart.append(priceO.adj_close)
        date.append(priceO.date)
    return line_chart,date


def calcPortfolioGain(portObj):
    assets_obj = pModels.PortfolioAssets.objects.filter(port=portObj)
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


        if portObj.sold==False:
            current_price = pModels.AssetPriceMovements.objects.filter(ticker=assetO.asset).latest('date').adj_close
        
        else:
            current_price = assetO.sold_for_usd/details['quantity_quote']


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

    return total_asset_dict,gains_dict,totalCurrProfit,totalCurrWorth

def getPortList(userObj):
    portList = pModels.Portfolio.objects.filter(user=userObj).order_by('created_on')

    portDetails = {}
    for port in portList:
        total_asset_dict,gains_dict,totalCurrProfit,totalCurrWorth = calcPortfolioGain(port)
        portDetails[port] = {
            'total_asset_dict':total_asset_dict,
            'gainDict':gains_dict,
            'totalCurrWorth':totalCurrWorth,
            'totalCurrProfit':totalCurrProfit
        }
    return portDetails





from django.contrib.auth.models import User
def gainChartUnrealizedProfitPortfolio(portObj):
    port_assets_list = pModels.PortfolioAssets.objects.filter(port=portObj)
    bought_on = portObj.created_on

    today = datetime.now() if portObj.sold==False else portObj.sold_on
    cday = bought_on

    cday = cday.replace(hour=0,minute=0,second=0)
    today = today.replace(hour=0,minute=0,second=0)

    line = []
    netAssetWorth = 0
    perchg = 0
    profit = 0

    datewise_dict = {}

    while cday<today-timedelta(days=1):
        pro_details = {}
        for asset in port_assets_list:
            try:
                assCurrPrice = pModels.AssetPriceMovements.objects.get(ticker=asset.asset,date__range=(cday,cday+timedelta(days=1))).adj_close
                perchg = (assCurrPrice/asset.usdSpent)*asset.assetQuantity
                netAssetWorth = perchg * asset.usdSpent
                profit = netAssetWorth - asset.usdSpent
            except Exception as e:
                try:
                    netAssetWorth = datewise_dict[cday][asset]['netWorth']
                    profit = datewise_dict[cday][asset]['profit']
                except:
                    # print("E2")
                    pass
                # print("E1")
                pass
            pro_details[asset] = {
                'netWorth':netAssetWorth,
                'profit':profit,
                # 'perchg':perchg
            }
        cday += timedelta(days=1)

        datewise_dict[cday] = pro_details
    
    return datewise_dict


def gainChartUnrealizedProfit(userObj):
    port_list = pModels.Portfolio.objects.filter(user=userObj,sold=False).order_by('created_on')
    
    days_stat_dict = {}

    for port in port_list:
        portGainsDict = gainChartUnrealizedProfitPortfolio(port)
        for date,assetsDict in portGainsDict.items():
            tempDict = days_stat_dict.get(date,None)
            if tempDict==None:
                days_stat_dict[date] = {
                    'profit':0,
                    'netWorth':0,
                }
            for _,val in assetsDict.items():
                for key2,val2 in val.items():
                    days_stat_dict[date][key2] += val2
    
    return days_stat_dict




def getIntoSameLine(line_dict):

    start_date = datetime.strptime('2100/12/31','%Y/%m/%d')
    ending_date = datetime.strptime('1999/01/01','%Y/%m/%d')

    for portName, line in line_dict.items():
        try:
            if start_date> datetime.strptime(line['date'][0],'%Y/%m/%d'):
                start_date = datetime.strptime(line['date'][0],'%Y/%m/%d')
            
            if ending_date<datetime.strptime(line['date'][-1],'%Y/%m/%d'):
                ending_date = datetime.strptime(line['date'][-1],'%Y/%m/%d')
        except:
            pass
    dateArr = []

    for i in range(0,(ending_date-start_date).days+1):
        dateArr.append(start_date+timedelta(days=i))
    
    
    for portName, line in line_dict.items():
        try:
            s = datetime.strptime(line['date'][0],'%Y/%m/%d')
            total_None_insertions = (s-start_date).days
            
            for i in range(total_None_insertions):
                line['netWorth'].insert(0,None)
                line['dayPnL'].insert(0,None)
        except:
            pass
        line['netWorth'] = [x if x>0 else None for x in line['netWorth'] ]
        # line['dayPnL'] = [x if x>0 else None for x in line['dayPnL'] ]
    dateArr = [d.strftime('%d/%m/%Y') for d in dateArr]
    return line_dict,dateArr


def getIndPortLineChart(userObj):
    port_list = pModels.Portfolio.objects.filter(user=userObj,sold=False).order_by('created_on')

    line_dict = {}

    for port in port_list:
        portGainsDict = gainChartUnrealizedProfitPortfolio(port)

        netWorth = []
        dayPnL = []

        for date,pAssetDict in portGainsDict.items():
            net = 0
            profit = 0
            for portAsset,details in pAssetDict.items():
                net += details['netWorth']
                profit += details['profit']

            netWorth.append(net)
            dayPnL.append(profit)
            
        line_dict[port.uPortName] = {
                'date': [d.strftime("%Y/%m/%d") for d in list(portGainsDict.keys())],
                'netWorth':netWorth,
                'dayPnL':dayPnL,
        }
    for port,lines in line_dict.items():
        for i in range(len(lines['dayPnL'])-1,0,-1):
            lines['dayPnL'][i] = lines['dayPnL'][i] - lines['dayPnL'][i-1]

    cleaned,datearr = getIntoSameLine(line_dict)
    return line_dict,cleaned,datearr




def getDateWiseLinePlot(portObj):

    portGainsDict = gainChartUnrealizedProfitPortfolio(portObj)

    netWorth = []
    dayPnL = []

    for date,pAssetDict in portGainsDict.items():
        net = 0
        profit = 0
        for portAsset,details in pAssetDict.items():
            net += details['netWorth']
            profit += details['profit']

        netWorth.append(net)
        dayPnL.append(profit)
    
    for i in range(len(dayPnL)-1,0,-1):
        dayPnL[i] = dayPnL[i] - dayPnL[i-1]
    
    date = [d.strftime("%Y/%m/%d") for d in list(portGainsDict.keys())]
    try:
        if netWorth[0]==0:
            netWorth[0] = netWorth[1]
        else:
            print("dcasDvcDS",netWorth[0])
    except Exception as e:
        print(e)
        pass

    line_dict = {
            'date': date,
            'netWorth':netWorth,
            'dayPnL':dayPnL,
    }
    return line_dict



def getCumPortLineChart(userObj):
    portwiseStats = gainChartUnrealizedProfit(userObj)

    netWorth = []
    dayPnL = []

    for date,details in portwiseStats.items():
        netWorth.append(details['netWorth'])
        dayPnL.append(details['profit'])

    for i in range(len(dayPnL)-1,0,-1):
        dayPnL[i] = dayPnL[i] - dayPnL[i-1]
    
    info_dict = {
        'date':[d.strftime("%Y/%m/%d") for d in list(portwiseStats.keys())],
        'netWorth':netWorth,
        'dayPnL':dayPnL
    }

    return info_dict




def overallStats(userObj):
    ports_dict = getPortList(userObj)
    netWorth = 0
    profit = 0

    for _,details in ports_dict.items():
        netWorth += details['totalCurrWorth']
        profit += details['totalCurrProfit']
    
    return {'netWorth':round(netWorth,2),'profit':round(profit,2)}


def getOverallPie(userObj):
    _,gain_dict,_,_ = getNetWorthGainUnrealized(userObj)

    weight_dict = {}
    currUSD = 0
    for asset,dictx in gain_dict.items():
        weight_dict[asset.asset.assetName] = dictx['currentAssetWorth']
        currUSD += dictx['currentAssetWorth']

    weight_dict = {x:y/currUSD*100 for x,y in weight_dict.items()}

    return weight_dict

def getPortPie(portObj):
    _,gain_dict,_,_ = calcPortfolioGain(portObj)

    weight_dict = {}
    currUSD = 0
    for asset,dictx in gain_dict.items():
        weight_dict[asset.asset.assetName] = dictx['currentAssetWorth']
        currUSD += dictx['currentAssetWorth']

    weight_dict = {x:y/currUSD*100 for x,y in weight_dict.items()}

    return weight_dict
