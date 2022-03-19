from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modules.helper import getNews,getTickerData,getPortList,getIndPortLineChart,overallStats,getOverallPie
    
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import finnhub
from pprint import pprint

from finserv.startup import ALL_ASSETS

def dash(request):

    if request.user.is_authenticated==False:
        return HttpResponseRedirect(reverse('reg_sign_in_out:user_login'))  


    #List of news [(title,link,published)]
    sorted_news = getNews()[:15]

    #{asset:price}
    topAssets = getTickerData()

    #{port:{asset:{'quantity_quote':x,'quantity_usd':x}}}
    #{port:{asset:{'perGain':x,'profit':x,'currentAssetWorth':x}}
    #totalprofit
    #portWorth

    ports = getPortList(request.user)



    indPortLine,cleaned,datearr = getIndPortLineChart(request.user)

    pie_dict = getOverallPie(request.user)
    
    overall = overallStats(request.user)
    
    finnhub_client = finnhub.Client(api_key="c8qa5e2ad3ienapjhe80")

    score = []

    for asset,sym in list(ALL_ASSETS.items())[:2]:
        try:
            scoreval = int(finnhub_client.stock_social_sentiment(sym)['twitter'][0]['score']*100)/100
            score.append([scoreval,asset])
        except Exception as e:
            print(e)
            pass

    score = sorted(score,key=lambda x:x[0],reverse=True)[:10]
    score = {y:x for x,y in score}
    return render(request, 'dashboard/dashnewft.html',context=
                    {
                        'topAssets':topAssets,
                        'news':sorted_news,
                        'ports':ports,
                        'overall':overall,
                        'indPortLine':cleaned,
                        'dateArr':datearr,
                        'pie':pie_dict,
                        'pred':score
                        }
                )


