from django.shortcuts import render
from django.utils import timezone
from portfolio import models as pModels
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required


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