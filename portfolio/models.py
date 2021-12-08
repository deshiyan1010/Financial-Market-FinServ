from django.db import models

from django.contrib.auth.models import User
from django.db.models.base import ModelState

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uPortName = models.CharField(max_length=64,primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self):
        self.uPortName = self.user.username + self.uPortName
        super(Portfolio, self).save()

    def __str__(self):
        return self.user.username+"-"+self.uPortName


class AssetsDetails(models.Model):
    assetName = models.CharField(max_length=64,primary_key=True)
    assetTicker = models.CharField(max_length=8)

    def __str__(self):
        return self.assetName+"-"+self.assetTicker

class AssetPriceMovements(models.Model):
    ticker = models.ForeignKey(AssetsDetails,on_delete=models.CASCADE)
    adj_close = models.FloatField()
    date = models.DateTimeField()
    def __str__(self):
        return self.ticker.assetName+"  "+self.date.strftime('%Y-%m-%d')

    class Meta:
        unique_together = ('ticker', 'date',)


class Assets(models.Model):
    port = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    assetName = models.ForeignKey(AssetsDetails, on_delete=models.CASCADE)
    assetQuantity = models.FloatField()
    usdSpent = models.FloatField()

    def __str__(self):
        return self.port.user.username+"-"+self.port.uPortName+"-"+self.assetName