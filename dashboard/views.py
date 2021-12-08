from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modules.helper import getNews,getTickerData



@login_required
def dash(request):

    
    sorted_news = getNews()
    topAssets = getTickerData()
    # networth = getNetworthHist(request.user)
    

    return render(request, 'dashboard/dash.html',context=
                    {
                        'topAssets':topAssets,
                        'assetPerfom':[0, 48, 0, 19, 86, 27, 90],
                        'news':sorted_news,
                        }
                )