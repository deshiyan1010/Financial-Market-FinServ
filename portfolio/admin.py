from django.contrib import admin

from django.contrib import admin
from portfolio.models import *

admin.site.register(Portfolio)
admin.site.register(PortfolioAssets)
admin.site.register(Assets)
admin.site.register(AssetPriceMovements)