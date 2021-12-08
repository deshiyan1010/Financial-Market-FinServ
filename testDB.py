import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","finserv.settings")

import django 
django.setup()

import pandas as pd
from portfolio.models import AssetPriceMovements,AssetsDetails


tick_obj = AssetsDetails.objects.create(assetName='Microsoftx',assetTicker='MSSSS')
tick_obj.save()

p = AssetPriceMovements.objects.create(ticker=tick_obj,adj_close=10)
p.save()

p = AssetPriceMovements.objects.create(ticker=tick_obj,adj_close=10)
p.save()