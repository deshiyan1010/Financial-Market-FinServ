from django.shortcuts import render
from django.utils import timezone
from django.views.decorators import csrf
from yfinance import ticker
from portfolio import models as pModels
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from finserv.startup import ALL_ASSETS,ALL_ASSETS_REV

from modules import portfolio_opt

@login_required
def sellPortfolio(request,port_id):

    assetObjectist = pModels.PortfolioAssets.objects.filter(port_id=port_id,sold=False)

    for asset in assetObjectist:
        asset.sold = True
        asset.sold_on = timezone.now()
        asset.sold_for_usd = pModels.AssetPriceMovements.objects.filter(ticker=asset.asset).latest('date')
        asset.save()


    return HttpResponseRedirect(reverse('dashboard:dash'))


    #<a class='col-lg-2 col-md-2 btn btn-success' href="{% url 'portfolio:sellPortfolio' port.id %}">Sell</a>


def addAssetToPort(portObj,assetName,USD):
    assetObj = pModels.Assets.objects.get(assetName=assetName)
    cPrice = pModels.AssetPriceMovements.objects.filter(ticker=assetObj).latest('date').adj_close
    amtAssetOwned = USD/cPrice
    portAsset = pModels.PortfolioAssets.objects.create(port=portObj,asset=assetObj,assetQuantity=amtAssetOwned,usdSpent=USD)
    portAsset.save()

@csrf_exempt
def addport(request):

    if request.user.is_authenticated==False:
        return HttpResponseRedirect(reverse('reg_sign_in_out:user_login'))  

    if request.method == "POST":

        opt = True if 'opt' in request.POST else False
        letOptPick = True if 'ap' in request.POST else False
        print(letOptPick,opt)

        portName = request.POST.get('portName')
        print(portName)
        create_port = pModels.Portfolio.objects.create(user=request.user,uPortName=portName)
        create_port.save()

        


        grandAmount = float(request.POST.get('amount'))


        
        if opt==False:
            assets = {}
            for i in range(100):
                assetName = request.POST.get('assetName'+str(i))
                amount = request.POST.get('assetAmount'+str(i))
                if assetName!=None:
                    assets[assetName] = float(amount)

            for asset, amount in assets.items():
                addAssetToPort(create_port,asset,amount)



        elif opt==True and letOptPick==False:
            assets = []
            for i in range(100):
                assetName = request.POST.get('assetName'+str(i))
                if assetName!=None:
                    assets.append(ALL_ASSETS[assetName])

            po = portfolio_opt.PortfolioOptmizer(tickList=assets)
            po.getWeights()
            weights = po.wCleaned

            for asset,weight in weights.items():
                print(asset,weight)
                addAssetToPort(create_port,ALL_ASSETS_REV[asset],weight*grandAmount)

        else:
            
            assets = list(ALL_ASSETS.values())
            po = portfolio_opt.PortfolioOptmizer(tickList=assets)
            po.getWeights()
            weights = po.wCleaned

            for asset,weight in weights.items():
                print(asset,weight)
                addAssetToPort(create_port,ALL_ASSETS_REV[asset],weight*grandAmount)


        return HttpResponseRedirect(reverse('dashboard:dash'))

    return render(request, 'portfolio/addport.html',context={'assetList':ALL_ASSETS_REV.values()})



def portDetails():
    pass