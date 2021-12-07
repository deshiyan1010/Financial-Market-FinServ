from django.shortcuts import render
from pygooglenews import GoogleNews


def dash(request):

    gn = GoogleNews(lang = 'en')
    news = gn.search('crypto OR indian stock market OR BSE OR NSE OR NASDAQ OR stocks OR shares OR SEBI OR SEC',when='24h')['entries']
    
    sorted_news = [(x['title'],x['link']) for x in sorted(news,key = lambda i: i['published'],reverse=True)]
    





    return render(request, 'dashboard/dash.html',context=
                    {
                        'assetPerfom':[0, 48, 0, 19, 86, 27, 90],
                        'news':sorted_news,
                        }
                )