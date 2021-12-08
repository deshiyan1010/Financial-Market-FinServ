from django.shortcuts import render
from reg_sign_in_out.models import *
from . import forms 
import requests
import urllib.parse
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
import json
import os
from finserv.settings import STATIC_DIR
import re


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))  

@csrf_protect
def registration(request):

    registered = False

    if request.method == "POST":
        form = forms.UserForm(request.POST)
        profileform = forms.RegistrationForm(request.POST)

        if form.is_valid() and profileform.is_valid():


            user = form.save()
            user.set_password(user.password)
            user.save()

            profile = profileform.save(commit=False)
            profile.user = user

            profile.save()

            registered = True
            return HttpResponseRedirect(reverse('reg_sign_in_out:user_login'))
        
        else:

            print(form.errors,profileform.errors)
            
            return render(request,"reg_sign_in_out/registration.html",{"tried":"True",
                                                    "registered":registered,
                                                   "profile_form":profileform,
                                                   "user_form":form,
                                                   "errorone":form.errors,
                                                   "errortow":profileform.errors,
                                                   })
            

    else:
        user = forms.UserForm()
        profileform = forms.RegistrationForm()

    return render(request,"reg_sign_in_out/registration.html",{"registered":registered,
                                                   "profile_form":profileform,
                                                   "user_form":user,
                                                   })


@csrf_protect
def user_login(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('dashboard:dash'))

        else:

            return render(request,"reg_sign_in_out/login.html",{'tried':'True'})

    else:
        return render(request,"reg_sign_in_out/login.html")

