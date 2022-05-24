import os
import pandas as pd
import numpy as np
import sys
from datetime import date as dt
from datetime import timedelta as td 
import time
from time import sleep
import datetime
from dateutil import parser
import pytz
import requests
import math



"""

MANDATORY INPUT: token, api_key

OPTIONAL INPUT:

- start: n days ago for starting the date range.
        Default start = 7 days ago.
        
- end: n days ago for ending the date range.
        Default end = 0 days ago.


"""




def get_aircall_calls(token, api_key, #mandatory
                      
                      start = 7, end = 0 #optional
                     ):

    
    
    start_date = (dt.today()-td(days = start)).isoformat()
    # converted to UNIX timefromat 
    start_date = math.trunc(time.mktime(datetime.datetime.strptime(start_date, "%Y-%m-%d").timetuple()))

    end_date = (dt.today()-td(days = end)).isoformat()
    # converted to UNIX timefromat 
    end_date = math.trunc(time.mktime(datetime.datetime.strptime(end_date, "%Y-%m-%d").timetuple()))
    
    link = f'https://{token}:{api_key}@api.aircall.io/v1/calls?from={start_date}&to={end_date}&page=1&per_page=50'

    headers = {'accept': 'application/json'}

    response = requests.request("GET", link, headers=headers)

    dati = response.json()

    total_items = dati["meta"]["total"]
    
    
    records = []

    if total_items >= 10000:

        print("Range interval reduce as:")


        day_intervals = []

        while True:

            left = start

            right = max(end, start - 11)

            day_intervals.append((left, right))

            start = right + 1

            if right == end:

                break




        for start, end in day_intervals:

            print("start {}, end {}".format(start, end))

            start_date = (dt.today()-td(days = start)).isoformat()
                # converted to UNIX timefromat 
            start_date =math.trunc(time.mktime(datetime.datetime.strptime(start_date, "%Y-%m-%d").timetuple()))

            end_date = (dt.today()-td(days = end)).isoformat()
            # converted to UNIX timefromat 
            end_date = math.trunc(time.mktime(datetime.datetime.strptime(end_date, "%Y-%m-%d").timetuple()))
            
            new_link = f'https://{token}:{api_key}@api.aircall.io/v1/calls?from={start_date}&to={end_date}&page=1&per_page=50'
    
            new_headers = {'accept': 'application/json'}

            new_response = requests.request("GET", new_link, headers=new_headers)

            new_dati = new_response.json()

            new_total_items = new_dati["meta"]["total"]
            
            if new_total_items >= 10000:
                
                print("Second range interval reduced as:")
                
             

                for new_left in range(start, end, -1):
                    
                    print("start {}, end {}".format(new_left, new_left - 1))

                    new_start_date = (dt.today() - td(days = new_left)).isoformat()
                    
                    # converted to UNIX timefromat
                    
                    new_start_date = math.trunc(time.mktime(datetime.datetime.strptime(new_start_date, "%Y-%m-%d").timetuple()))
                    
                    new_end_date = (dt.today() - td(days = new_left - 1)).isoformat()
                    
                    new_end_date = math.trunc(time.mktime(datetime.datetime.strptime(new_end_date, "%Y-%m-%d").timetuple()))
                    
                    records += run_all_requests(new_start_date, new_end_date, token, api_key)
             
           
            
            else:


                records += run_all_requests(start_date, end_date, token, api_key)

    else:

        records += run_all_requests(start_date, end_date, token, api_key)
    
    aircall_calls = pd.DataFrame(records)


    unix_to_readable = ["answered_at", "ended_at", "started_at"]

    for unix_col in unix_to_readable:

        #aircall_calls[unix_col] = pd.to_datetime(aircall_calls[unix_col], unit='s')
        
        #convert to italian timezone
        aircall_calls[unix_col] = pd.to_datetime(aircall_calls[unix_col], unit='s', utc=True, ).dt.tz_convert('Europe/Rome').dt.tz_localize(None)

    
    return aircall_calls




def run_all_requests(start_date, end_date, token, api_key):
    
    
    
    records = []
    
    page = 1
    
    run = True
    
    while run:

        sleep(1)

        


        link = f'https://{token}:{api_key}@api.aircall.io/v1/calls?from={start_date}&to={end_date}&page={page}&per_page=50'

        headers = {'accept': 'application/json'}

        response = requests.request("GET", link, headers=headers)

        
        try:
            dati = response.json()
            
        except:
            print(response)
            print('page', page)
            print(start_date, end_date)

        total_pages = math.ceil(dati["meta"]["total"]/50)

        if page == 1:
            total_items = dati["meta"]["total"]



            print("Total number of pages", total_pages)

            print("Total number of items", total_items)

        '''

        if page%30 == 0: 
            
            print("---------")
            print("Page N.", page)

            print(dati["meta"])

        '''
        
        
        if dati["meta"]["count"] == 0:
            run = False


        else:
            page += 1

            for d in dati['calls']:

                try:
                    id = d['id']
                except:
                    id  = ''
                try:
                    cost_cent = d['cost']
                except:
                    cost_cent  = ''                
                try:
                    direction = d['direction']
                except:
                    direction  = ''
                try:
                    status = d['status']
                except:
                    status  = ''
                try:
                    started_at = d['started_at']
                except:
                    started_at  = ''
                try:
                    answered_at = d['answered_at']
                except:
                    answered_at  = ''
                try:
                    ended_at = d['ended_at']
                except:
                    ended_at  = ''
                try:
                    duration = d['duration']
                except:
                    duration  = ''
                try:
                    raw_digits = d['raw_digits']
                except:
                    raw_digits  = ''
                try:
                    user_id = d['user'][0]['id']
                except:
                    try:
                        user_id  = d['user']['id']
                    except:

                        user_id = ''
                try:
                    user_name = d['user'][0]['name']
                except:
                    try:
                        user_name  = d['user']['name']
                    except:
                        user_name = ''
                try:
                    contact_id = d['contact']['id']
                except:
                    contact_id  = ''
                try:
                    contact_name = d['contact']['first_name']
                except:
                    contact_name  = ''
                try:
                    contact_last_name = d['contact']['last_name']
                except:
                    contact_last_name  = ''
                try:
                    cnt_company_name = d['contact']['company_name']
                except:
                    cnt_company_name  = ''

                records.append({
                    'id' : id,
                    'direction' : direction,
                    'status' : status,
                    'started_at' : started_at, #
                    'answered_at' : answered_at, #
                    'ended_at' : ended_at,
                    'duration' : duration, #
                    'raw_digits' : raw_digits, #deal_id
                    'user_id' : user_id,
                    'user_name' : user_name,
                    'contact_id' : contact_id,
                    'contact_name' : contact_name,
                    'contact_last_name' : contact_last_name,
                    'cnt_company_name' : cnt_company_name,
                    'cost_cent' : cost_cent
                })
    
    return records
