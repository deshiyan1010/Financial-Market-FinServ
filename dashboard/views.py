from django.shortcuts import render

def dash(request):
    return render(request, 'dashboard/dash.html',context={'name':'FinServ','datax':[0, 48, 0, 19, 86, 27, 90],'news':[('a','www.a.com'),('b','www.b.com')]})