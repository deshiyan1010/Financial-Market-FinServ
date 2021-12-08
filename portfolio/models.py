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


class Assets(models.Model):
    user = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    assetName = models.CharField(max_length=64)
    assetQuantity = models.FloatField()
    usdSpent = models.FloatField()


class AssetsDetails(models.Model):
    assetName = models.CharField(max_length=64,primary_key=True)
    assetTicker = models.CharField(max_length=8)

class AssetPriceMovements(models.Model):
    ticker = models.ForeignKey(AssetsDetails,on_delete=models.CASCADE)
    adj_close = models.FloatField()
    date = models.DateTimeField()


