from django.db import models

from django.contrib.auth.models import User
from django.db.models.base import ModelState

from django.utils.timezone import now

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uPortName = models.CharField(max_length=64,primary_key=True)
    # uPortName2 = models.CharField(max_length=64)
    created_on = models.DateTimeField(auto_now_add=True)
    sold = models.BooleanField(default=False)
    def save(self):
        self.uPortName = self.user.username + self.uPortName
        super(Portfolio, self).save()

    def __str__(self):
        return self.user.username+"-"+self.uPortName


class Assets(models.Model):
    assetName = models.CharField(max_length=64,primary_key=True)
    assetTicker = models.CharField(max_length=8)

    def __str__(self):
        return self.assetName+"-"+self.assetTicker

class AssetPriceMovements(models.Model):
    ticker = models.ForeignKey(Assets,on_delete=models.CASCADE)
    adj_close = models.FloatField()
    date = models.DateTimeField()
    def __str__(self):
        return self.ticker.assetName+"  "+str(round(self.adj_close,3))+" "+self.date.strftime('%Y-%m-%d')

    class Meta:
        unique_together = ('ticker', 'date',)



class PortfolioAssets(models.Model):
    sold = models.BooleanField(default=False)
    port = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE)
    assetQuantity = models.FloatField()
    usdSpent = models.FloatField()
    bought_on = models.DateTimeField(auto_now_add=True)
    sold_on = models.DateTimeField(null=True)
    sold_for_usd = models.FloatField(null=True)

    def __str__(self):
        return self.port.user.username+"-"+self.port.uPortName+"-"+self.asset.assetName+" "+self.bought_on.strftime('%Y-%m-%d')

