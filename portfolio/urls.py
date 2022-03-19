from django.urls import path
from . import views
from finserv import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "portfolio"

urlpatterns = [
                path('addport/',views.addport,name='addport'),
                path('portDetails/<str:portName>/',views.portdetails,name='portdetails'),
                path('sellPortfolio/<str:portName>/',views.sellPortfolio,name='sellPortfolio'),
                path('rebalance/<str:portName>/',views.rebalance,name='rebalance'),
                path('sellAsset/<str:portName>+<str:assetName>/',views.sellAsset,name='sellAsset'),
            ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()