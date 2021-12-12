from django.urls import path
from . import views
from finserv import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "portfolio"

urlpatterns = [
                path('addport/',views.addport,name='addport'),
            ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()