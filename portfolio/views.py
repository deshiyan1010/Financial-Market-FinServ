from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators import csrf
from riskfolio.Portfolio import Portfolio
from scipy import cluster
from scipy.cluster.hierarchy import dendrogram
from portfolio import models as pModels
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from finserv.startup import ALL_ASSETS,ALL_ASSETS_REV, VALUE

from modules.helper import getLinePlot,calcPortfolioGain,gainChartUnrealizedProfitPortfolio,getPortPie,getDateWiseLinePlot
from modules import portfolio_opt

from pprint import pprint



def sellPortfolio(request,portName):

    assetObjectist = pModels.PortfolioAssets.objects.filter(port_id=portName,sold=False)
    
    portObj = pModels.Portfolio.objects.get(uPortName=portName)
    portObj.sold = True
    portObj.sold_on = timezone.now()
    realized_profit = 0

    for asset in assetObjectist:
        if asset.sold==False:
            asset.sold = True
            asset.sold_on = timezone.now()
            asset.sold_for_usd = pModels.AssetPriceMovements.objects.filter(ticker=asset.asset).latest('date').adj_close * asset.assetQuantity
            asset.save()
            realized_profit += asset.sold_for_usd - asset.usdSpent


    portObj.realized_profit += realized_profit
    portObj.save()

    return HttpResponseRedirect(reverse('dashboard:dash'))


    #<a class='col-lg-2 col-md-2 btn btn-success' href="{% url 'portfolio:sellPortfolio' port.id %}">Sell</a>

def sellAsset(request,portName,assetName):

    _sellAsset(portName,assetName,True)

    return HttpResponseRedirect(reverse('portfolio:portdetails',args=[portName]))  

def _sellAsset(portName,assetName,realized):

    asset = pModels.PortfolioAssets.objects.get(port__uPortName=portName,asset__assetName=assetName,sold=False)
    asset.sold = True
    asset.sold_on = datetime.now()
    asset.sold_for_usd = pModels.AssetPriceMovements.objects.filter(ticker__assetName=assetName).latest('date').adj_close * asset.assetQuantity
    asset.save()

    portObj = pModels.Portfolio.objects.get(uPortName=portName)
    portObj.realized_profit += asset.sold_for_usd - asset.usdSpent
    portObj.save()


def addAssetToPort(portObj,assetName,USD):
    print("Adding",assetName)
    assetObj = pModels.Assets.objects.get(assetName=assetName)
    cPrice = pModels.AssetPriceMovements.objects.filter(ticker=assetObj).latest('date').adj_close
    amtAssetOwned = USD/cPrice
    portAsset = pModels.PortfolioAssets.objects.create(port=portObj,asset=assetObj,assetQuantity=amtAssetOwned,usdSpent=USD,bought_on=datetime.now())
    portAsset.save()

@csrf_exempt
def addport(request):

    if request.user.is_authenticated==False:
        return HttpResponseRedirect(reverse('reg_sign_in_out:user_login'))  

    if request.method == "POST":

        opt = True if 'opt' in request.POST else False
        letOptPick = True if 'ap' in request.POST else False

        portName = request.POST.get('portName')
        create_port = pModels.Portfolio.objects.create(user=request.user,uPortName=portName,created_on=datetime.now())
        create_port.save()

        grandAmount = float(request.POST.get('amount'))
        
        if opt==False:
            assets = {}
            for i in range(100):
                assetName = request.POST.get('assetName'+str(i))
                
                amount = request.POST.get('assetAmount'+str(i))
                if assetName!=None:
                    assetName = " ".join(assetName.split("_"))
                    assets[assetName] = assets.get(assetName,0)+float(amount)
            for asset, amount in assets.items():
                addAssetToPort(create_port,asset,amount)


        elif opt==True and letOptPick==False:
            assets = []
            for i in range(100):
                assetName = request.POST.get('assetName'+str(i))
                
                if assetName!=None:
                    assetName = " ".join(assetName.split("_"))
                    assets.append(ALL_ASSETS[assetName])

            assets = list(set(assets))
            
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
                addAssetToPort(create_port,ALL_ASSETS_REV[asset],weight*grandAmount)


        return HttpResponseRedirect(reverse('dashboard:dash'))

    return render(request, 'portfolio/addport.html',context={'assetList':VALUE})










def rebalance(request,portName):

    assetObjectist = pModels.PortfolioAssets.objects.filter(port__uPortName=portName,sold=False)
    totalAmount = 0
    netWorth = 0
    assetList = []

    for asset in assetObjectist:
        if asset.sold==False:
            totalAmount += asset.usdSpent
            netWorth += pModels.AssetPriceMovements.objects.filter(ticker=asset.asset).latest('date').adj_close * asset.assetQuantity
            assetList.append(asset.asset.assetTicker)
            _sellAsset(portName,asset.asset.assetName,False)
    print("LIst",assetList)

    po = portfolio_opt.PortfolioOptmizer(tickList=assetList)
    po.getWeights()
    weights = po.wCleaned
    print(weights)
    portObj = pModels.Portfolio.objects.get(uPortName=portName)

    for asset,weight in weights.items():
        addAssetToPort(portObj,ALL_ASSETS_REV[asset],weight*netWorth)



    return HttpResponseRedirect(reverse('portfolio:portdetails',args=[portName]))  


@csrf_exempt
def portdetails(request,portName):
    
    portObj = pModels.Portfolio.objects.get(uPortName=portName)

    if request.user.is_authenticated==False:
        return HttpResponseRedirect(reverse('reg_sign_in_out:user_login'))  

    if request.method == "POST":
        assetName = " ".join(request.POST.get('assetName').split("_"))
        print(assetName)
        amount = float(request.POST.get('amount'))
        addAssetToPort(portObj,assetName,amount)
        return HttpResponseRedirect(reverse('portfolio:portdetails',args=[portName]))  

    
    assetList = pModels.PortfolioAssets.objects.filter(port=portObj)
    indLinePlot = {}

    for pAsset in assetList:
        line,dateArr = getLinePlot(pAsset.asset.assetName)
        indLinePlot[pAsset.asset.assetName] = line
    
    
    dateArr = [cdate.strftime("%d/%m/%Y") for cdate in dateArr]

    total_asset_dict,gains_dict,totalCurrProfit,totalCurrWorth = calcPortfolioGain(portObj)

    portPie = getPortPie(portObj)

    cum_line_dict = getDateWiseLinePlot(portObj)


    port_opt_obj = portfolio_opt.PortfolioOptmizer(tickList=[ALL_ASSETS[ass] for ass in indLinePlot.keys()])

    assetListabc = []
    weightabc = []
    for asset,weight in portPie.items():
        assetListabc.append(ALL_ASSETS[asset])
        weightabc.append(weight/100)


    port_opt_obj.setWeigth(assetListabc,weightabc)

    frontier = port_opt_obj.frontierPlotPlotly()
    frontierArea = port_opt_obj.frontierAreaPlot()
    # cluster = port_opt_obj.clusterPlot()
    # dendrogram = port_opt_obj.dendrogramPlot()
    

    return render(request, 'portfolio/portdetails.html',context={
        'cum_line':cum_line_dict,
        'portPie':portPie,
        'curProfit':totalCurrProfit,
        'curWorth':totalCurrWorth,
        'gainDict':gains_dict,
        'allAssets': total_asset_dict,
        'portName':portObj.uPortName,
        'dateArr':dateArr,
        'indLine':indLinePlot,
        'frontier':frontier,
        'frontierArea':frontierArea,
        'portObj':portObj,
        'assetList':VALUE,
    })