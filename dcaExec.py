import pause
from datetime import datetime,timedelta
import time
import os

from multitasking import createPool
os.environ.setdefault("DJANGO_SETTINGS_MODULE","finserv.settings")

from datetime import datetime
from datetime import timedelta

import django 
django.setup()

import pandas as pd
from portfolio import models as pModels

from pymongo import MongoClient

time_in_min = 1

def getNextRun(dcaCollLatest):
    oldest_date = datetime.now()
    oldest_rec = None
    for rec in dcaCollLatest.find({}):
        if oldest_date>rec['exec_on']:
            oldest_date = rec['exec_on']
            oldest_rec = rec
    return oldest_date +timedelta(minutes=time_in_min),oldest_rec


def buy(rec,dcaCollLatest,dcaColl):
    nrec = {
        'portName':rec['portName'],
        'exec_on':datetime.now(),
        'amount':rec['amount']
    }

    dcaCollLatest.delete_many({'portName':rec['portName']})
    dcaColl.insert_one(rec)
    dcaCollLatest.insert_one(nrec)




if __name__=="__main__":
    client = MongoClient('localhost', 27017)

    dcaDatabase = client['dca']
    dcaColl = dcaDatabase['dca_report']
    dcaCollLatest = dcaDatabase['dca_report_latest']

    # inserting the data in the database
    rec = {
        'portName':'',
        'exec_on':'',
        'amount':''
    }

    # for i in dcaColl.find({}):
    #     print(i)
    

    for portRec in pModels.Portfolio.objects.all():
        if dcaColl.find_one({'portName': portRec.uPortName})==None:
            rec_copy = {}
            rec_copy['portName'] = portRec.uPortName
            rec_copy['exec_on'] = datetime.now()
            rec_copy['amount'] = 1000
            rec = dcaCollLatest.insert_one(rec_copy)

    # for i in dcaCollLatest.find({}):
    #     print(i)
    # print("***8")

    while 1:
        next_run,recovered_rec = getNextRun(dcaCollLatest)
        print("NextRun")
        pause.until(next_run)
        buy(recovered_rec,dcaCollLatest,dcaColl)
        print("Bought:\n\tPortfolio Name: {}\n\tLast Executed: {}".format(recovered_rec['portName'],recovered_rec['exec_on']))