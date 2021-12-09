from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modules.helper import getNews,getTickerData,getNetWorthGainUnrealized,getPortList



@login_required
def dash(request):

    
    sorted_news = getNews()
    topAssets = getTickerData()
    total_asset_dict,gains_dict = getNetWorthGainUnrealized(request.user)
    print(
        {x.asset.assetName:y for x,y in total_asset_dict.items()},
        {x.asset.assetName:y for x,y in gains_dict.items()}
        )

    ports = getPortList(request.user)

    return render(request, 'dashboard/dash.html',context=
                    {
                        'topAssets':topAssets,
                        'assetPerfom':[0, 48, 0, 19, 86, 27, 90],
                        'news':sorted_news,
                        'ports':ports
                        }
                )