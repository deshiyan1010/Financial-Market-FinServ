from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modules.helper import getNews,getTickerData,getPortList,getIndPortLineChart,overallStats,getOverallPie
    
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from pprint import pprint

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
    


    return render(request, 'dashboard/dashnewft.html',context=
                    {
                        'topAssets':topAssets,
                        'news':sorted_news,
                        'ports':ports,
                        'overall':overall,
                        'indPortLine':cleaned,
                        'dateArr':datearr,
                        'pie':pie_dict,
                        }
                )


