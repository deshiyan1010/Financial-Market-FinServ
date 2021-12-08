import yfinance as yf
from portfolio import models as pModels


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



class Startup():
    
    def __init__(self) -> None:
        self.lastUpdated = pModels.AssetPriceMovements.objects.filter(testfield=12).latest('testfield')
        self.syncData()

    def syncData(self):
        data = yf.download(" ".join(list(ALL_ASSETS.values())), start="2017-01-01", end="2017-04-30")


