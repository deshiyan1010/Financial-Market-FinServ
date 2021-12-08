from django.shortcuts import render
from pygooglenews import GoogleNews
import yfinance as yf
from django.contrib.auth.decorators import login_required



TOP_ASSETS = ['^NSEI','^BSESN','^GSPC','BTC-USD','ETH-USD','TSLA']

@login_required
def dash(request):

    gn = GoogleNews(lang = 'en')
    news = gn.search('crypto OR indian stock market OR BSE OR NSE OR NASDAQ OR stocks OR shares OR SEBI OR SEC',when='24h')['entries']
    
    sorted_news = [(x['title'],x['link'],x['published']) for x in sorted(news,key = lambda i: i['published'],reverse=True)]
    

    topAssets = {}
    topDF = yf.download(" ".join(TOP_ASSETS),period='1d')['Adj Close']
    topAssets = topDF.to_dict()

    return render(request, 'dashboard/dash.html',context=
                    {
                        'topAssets':topAssets,
                        'assetPerfom':[0, 48, 0, 19, 86, 27, 90],
                        'news':sorted_news,
                        }
                )