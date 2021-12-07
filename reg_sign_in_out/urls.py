from django.urls import path
from . import views

app_name = "reg_sign_in_out"

urlpatterns = [
    path('user_login/',views.user_login,name='user_login'),
    path('registration/',views.registration,name="registration"),

]
