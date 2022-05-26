#required !pip install googleads -q


import pandas as pd
import numpy as np

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf.json_format import MessageToDict



import _locale


"""
MANDATORY INPUT:

start_date, end_date as string "yyyy-mm-dd"

OPTIONAL INPUTS: 



- yaml_file_path: the path of 'googleads.yaml'. 
                Optional, but mandatory to have it in same folder script if used the default parameter.

"""

def get_google_ads(start_date, end_date, admin_account,
                   
                   
                   ## optional
                   
                   yaml_file_path = 'googleads.yaml'
                  ):

    _locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])
    
    googleads_client = GoogleAdsClient.load_from_storage('googleads.yaml')
    
    ga_service = googleads_client.get_service("GoogleAdsService")
    
    query = f"""
            SELECT 
            campaign_budget.amount_micros,
            campaign.id, 
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            metrics.cost_micros, 
            segments.month, 
            segments.date, 
            campaign.name, 
            metrics.impressions, 
            metrics.clicks, 
            metrics.ctr, 
            metrics.average_cpc, 
            metrics.conversions, 
            metrics.view_through_conversions, 
            metrics.cost_per_conversion, 
            campaign.status, 
            metrics.all_conversions_from_interactions_rate, 
            metrics.average_cpm 
            FROM campaign 
            WHERE 
            segments.date BETWEEN '{start_date}' AND '{end_date}' """
    
    search_request = googleads_client.get_type("SearchGoogleAdsStreamRequest")
        
    
    google_ads = pd.DataFrame(columns = ['Customer ID','Brand','Currency','Campaign state','Campaign','Campaign ID','Clicks','View-through conv.','Conversions','Cost','Cost / conv.','CTR','Conv. rate','Avg. CPC','Avg. CPM','Impressions','Budget','Day','Month'])
        
    df = pd.DataFrame(columns = ['Customer ID','Brand','Currency','Campaign state','Campaign','Campaign ID','Clicks','View-through conv.','Conversions','Cost','Cost / conv.','CTR','Conv. rate','Avg. CPC','Avg. CPM','Impressions','Budget','Day','Month'])
        
    for key, acc_id in admin_account.items():

        
        
        stream = ga_service.search(customer_id = acc_id, query=query)
        
        
        
        st = next(stream.pages)
        dictobj = MessageToDict(st)
        
        #print(dictobj)
        
        if 'results' in dictobj:
            
            df = pd.json_normalize(dictobj,record_path=['results'])


            df = df.drop(columns = ['customer.resourceName', 'campaign.resourceName', 'campaignBudget.resourceName'])


            df = df.rename(columns =  {'customer.id':'Customer ID',
                                     'customer.descriptiveName':'Brand',
                                     'customer.currencyCode':'Currency',
                                     'campaign.status':'Campaign state',
                                     'campaign.name':'Campaign',
                                     'campaign.id':'Campaign ID',
                                     'metrics.clicks':'Clicks',
                                     'metrics.viewThroughConversions':'View-through conv.',
                                     'metrics.conversions':'Conversions',
                                     'metrics.costMicros':'Cost',
                                     'metrics.costPerConversion':'Cost / conv.',
                                     'metrics.ctr':'CTR',
                                     'metrics.allConversionsFromInteractionsRate':'Conv. rate',
                                     'metrics.averageCpc':'Avg. CPC',
                                     'metrics.averageCpm':'Avg. CPM',
                                     'metrics.impressions':'Impressions',
                                     'campaignBudget.amountMicros':'Budget',
                                     'segments.date':'Day',
                                     'segments.month':'Month'} )

            

            #print(df.head())
            print(f'Extracted data for {key}')

        else:
            print(f'No data for {key}')

        google_ads = pd.concat([google_ads, df])
    
        
    google_ads = google_ads[['Month', 'Day', 'Campaign ID', 'Customer ID', 'Campaign',
           'Campaign state', 'Budget', 'Currency', 'Clicks', 'Impressions', 'CTR',
           'Avg. CPC', 'Cost', 'Conversions', 'View-through conv.', 'Cost / conv.',
           'Conv. rate', 'Avg. CPM', 'Brand']].reset_index(drop = True)
    
    to_float = ['Clicks', 'Impressions', 'Cost', 'CTR', 'View-through conv.', 'Conversions', 'Cost / conv.', 'Conv. rate', 'Avg. CPC', 'Avg. CPM']

    google_ads['Campaign ID'] = google_ads['Campaign ID'].astype(int)

    for c in to_float:

        google_ads[c] = google_ads[c].astype(float)

    # micro amount 1000000
    google_ads['Cost'] = google_ads['Cost']/1000000
    
    google_ads['CTR'] = round(google_ads['CTR']*100, 2).astype(str) + '%'
    
    google_ads['Conv. rate'] = round(google_ads['Conv. rate']*100, 2).astype(str) + '%'
    
    google_ads['Campaign state'] = google_ads['Campaign state'].str.lower()
    
    
    google_ads['Avg. CPC'] = round(google_ads['Avg. CPC'], 1)
    google_ads['Avg. CPM'] = round(google_ads['Avg. CPM'], 1)
    google_ads['Cost / conv.'] = round(google_ads['Cost / conv.'], 1)
        
    return google_ads