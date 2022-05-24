# requirements !pip install hubspot3 -q



import pytz
import pandas as pd

import requests
from hubspot3 import Hubspot3



"""

Description for get_deals_all_fiels function

MANDATORY INPUT: 

- API_KEY
- start_date as string "yyyy-mm-dd"
- end_date as string "yyyy-mm-dd"


"""




def get_hubspot_deals_all_fields(API_KEY, start_date, end_date):
    
    from datetime import date as dt, timedelta as td , datetime, timezone

    url = "https://api.hubapi.com/crm/v3/objects/deals"

    
    
    start_date = datetime.strptime(start_date,"%Y-%m-%d")
    
    end_date = datetime.strptime(end_date,"%Y-%m-%d")

    y = 0

    i = 20
    after = '1'
    deals_all_fields_record = []


    while i >0 :
        # miss_tariffa___motivo_ko
        # miss_tariffa___motivo_trash
        # google_ad_click_id
        # contattabile

        if y%500 == 0:
            print("Iteration num.", y)

        y += 1
        
        querystring = {"limit": "100", "paginateAssociations": "false" ,"properties":"tipo_di_ordine,miss_tariffa___motivo_ko,chiave_teamwork,miss_tariffa___motivo_trash,google_ad_click_id,amount_in_home_currency,days_to_close,hs_acv,hs_analytics_source,hs_analytics_source_data_1,hs_analytics_source_data_2,hs_arr,campaign_name,hs_closed_amount,hs_closed_amount_in_home_currency,hs_created_by_user_id,hs_deal_stage_probability,hs_forecast_amount,hs_forecast_probability,hs_is_closed,hs_is_closed_won,hs_lastmodifieddate,hs_likelihood_to_close,hs_line_item_global_term_hs_discount_percentage,hs_line_item_global_term_hs_discount_percentage_enabled,hs_line_item_global_term_hs_recurring_billing_period,hs_line_item_global_term_hs_recurring_billing_period_enabled,hs_line_item_global_term_hs_recurring_billing_start_date,hs_line_item_global_term_hs_recurring_billing_start_date_enabled,hs_line_item_global_term_recurringbillingfrequency,hs_line_item_global_term_recurringbillingfrequency_enabled,hs_manual_forecast_category,hs_merged_object_ids,hs_mrr,hs_next_step,hs_object_id,hs_predicted_amount,hs_predicted_amount_in_home_currency,hs_projected_amount,hs_projected_amount_in_home_currency,hs_tcv,hs_time_in_appointmentscheduled,hs_time_in_closedlost,hs_time_in_closedwon,hs_time_in_contractsent,hs_time_in_decisionmakerboughtin,hs_time_in_presentationscheduled,hs_time_in_qualifiedtobuy,hs_unique_creation_key,hs_updated_by_user_id,hs_user_ids_of_all_owners,hubspot_owner_assigneddate,application_uuid3,dealname,salesforcelastsynctime,amount,dealstage,onboardingfrontlink,pipeline,closedate,onboardingadminlink,createdate,engagements_last_meeting_booked,engagements_last_meeting_booked_campaign,engagements_last_meeting_booked_medium,engagements_last_meeting_booked_source,hs_latest_meeting_activity,hs_sales_email_last_replied,hubspot_owner_id,notes_last_contacted,notes_last_updated,notes_next_activity_date,num_contacted_notes,num_notes,hs_createdate,hubspot_team_id,dealtype,hs_all_owner_ids,description,hs_all_team_ids,hs_all_accessible_team_ids,num_associated_contacts,closed_lost_reason,closed_won_reason,application_uuid2","after":after,
                "archived": "false", "hapikey": API_KEY}

        headers = {'accept': 'application/json'}
        response = requests.request("GET", url, headers=headers, params=querystring)


        dati = response.json()
        try:
            after = dati['paging']['next']['after']
            i = len(dati['paging']['next']['after'])
        except:
            after = ''
            i = 0
        d1 = dati["results"]
        for dd in d1:
            try:
                id = dd['id']
            except :
                id = ''
            try:
                amount_in_home_currency = dd['properties']['amount_in_home_currency']
            except :
                amount_in_home_currency = ''
            try:
                days_to_close = dd['properties']['days_to_close']
            except :
                days_to_close = ''
            try:
                hs_acv = dd['properties']['hs_acv']
            except :
                hs_acv = ''

            try:
                hs_analytics_source = dd['properties']['hs_analytics_source']
            except :
                hs_analytics_source = ''

            try:
                tipo_di_ordine = dd['properties']['tipo_di_ordine']
            except :
                tipo_di_ordine = ''
            try:
                hs_analytics_source_data_1 = dd['properties']['hs_analytics_source_data_1']
            except :
                hs_analytics_source_data_1 = ''
            try:
                hs_analytics_source_data_2 = dd['properties']['hs_analytics_source_data_2']
            except :
                hs_analytics_source_data_2 = ''
            try:
                miss_tariffa___motivo_ko = dd['properties']['miss_tariffa___motivo_ko']
            except :
                miss_tariffa___motivo_ko = ''
            try:
                miss_tariffa___motivo_trash = dd['properties']['miss_tariffa___motivo_trash']
            except :
                miss_tariffa___motivo_trash = ''
            try:
                google_ad_click_id = dd['properties']['google_ad_click_id']
            except :
                google_ad_click_id = ''
            try:
                hs_arr = dd['properties']['hs_arr']
            except :
                hs_arr = ''
            try:
                hs_campaign = dd['properties']['campaign_name']
            except :
                hs_campaign = ''
            try:
                hs_closed_amount = dd['properties']['hs_closed_amount']
            except :
                hs_closed_amount = ''
            try:
                hs_closed_amount_in_home_currency = dd['properties']['hs_closed_amount_in_home_currency']
            except :
                hs_closed_amount_in_home_currency = ''
            try:
                hs_created_by_user_id = dd['properties']['hs_created_by_user_id']
            except :
                hs_created_by_user_id = ''
            try:
                hs_deal_stage_probability = dd['properties']['hs_deal_stage_probability']
            except :
                hs_deal_stage_probability = ''
            try:
                hs_forecast_amount = dd['properties']['hs_forecast_amount']
            except :
                hs_forecast_amount = ''
            try:
                hs_forecast_probability = dd['properties']['hs_forecast_probability']
            except :
                hs_forecast_probability = ''
            try:
                hs_is_closed = dd['properties']['hs_is_closed']
            except :
                hs_is_closed = ''
            try:
                hs_is_closed_won = dd['properties']['hs_is_closed_won']
            except :
                hs_is_closed_won = ''
            try:
                hs_lastmodifieddate = dd['properties']['hs_lastmodifieddate']
            except :
                hs_lastmodifieddate = ''
            try:
                hs_likelihood_to_close = dd['properties']['hs_likelihood_to_close']
            except :
                hs_likelihood_to_close = ''

            try:
                hs_manual_forecast_category = dd['properties']['hs_manual_forecast_category']
            except :
                hs_manual_forecast_category = ''
            try:
                hs_merged_object_ids = dd['properties']['hs_merged_object_ids']
            except :
                hs_merged_object_ids = ''
            try:
                hs_mrr = dd['properties']['hs_mrr']
            except :
                hs_mrr = ''
            try:
                hs_next_step = dd['properties']['hs_next_step']
            except :
                hs_next_step = ''
            try:
                hs_object_id = dd['properties']['hs_object_id']
            except :
                hs_object_id = ''
            try:
                hs_predicted_amount = dd['properties']['hs_predicted_amount']
            except :
                hs_predicted_amount = ''
            try:
                hs_predicted_amount_in_home_currency = dd['properties']['hs_predicted_amount_in_home_currency']
            except :
                hs_predicted_amount_in_home_currency = ''
            try:
                hs_projected_amount = dd['properties']['hs_projected_amount']
            except :
                hs_projected_amount = ''
            try:
                hs_projected_amount_in_home_currency = dd['properties']['hs_projected_amount_in_home_currency']
            except :
                hs_projected_amount_in_home_currency = ''
            try:
                hs_tcv = dd['properties']['hs_tcv']
            except :
                hs_tcv = ''
            try:
                hs_time_in_appointmentscheduled = dd['properties']['hs_time_in_appointmentscheduled']
            except :
                hs_time_in_appointmentscheduled = ''
            try:
                hs_time_in_closedlost = dd['properties']['hs_time_in_closedlost']
            except :
                hs_time_in_closedlost = ''
            try:
                hs_time_in_closedwon = dd['properties']['hs_time_in_closedwon']
            except :
                hs_time_in_closedwon = ''
            try:
                hs_time_in_contractsent = dd['properties']['hs_time_in_contractsent']
            except :
                hs_time_in_contractsent = ''
            try:
                hs_time_in_decisionmakerboughtin = dd['properties']['hs_time_in_decisionmakerboughtin']
            except :
                hs_time_in_decisionmakerboughtin = ''
            try:
                hs_time_in_presentationscheduled = dd['properties']['hs_time_in_presentationscheduled']
            except :
                hs_time_in_presentationscheduled = ''
            try:
                hs_time_in_qualifiedtobuy = dd['properties']['hs_time_in_qualifiedtobuy']
            except :
                hs_time_in_qualifiedtobuy = ''
            try:
                hs_unique_creation_key = dd['properties']['hs_unique_creation_key']
            except :
                hs_unique_creation_key = ''
            try:
                hs_updated_by_user_id = dd['properties']['hs_updated_by_user_id']
            except :
                hs_updated_by_user_id = ''
            try:
                hs_user_ids_of_all_owners = dd['properties']['hs_user_ids_of_all_owners']
            except :
                hs_user_ids_of_all_owners = ''
            try:
                hubspot_owner_assigneddate = dd['properties']['hubspot_owner_assigneddate']
            except :
                hubspot_owner_assigneddate = ''        
            try:
                application_uuid3 = dd['properties']['application_uuid3']
            except :
                application_uuid3 = ''
            try:
                dealname = dd['properties']['dealname']
            except :
                dealname = ''
            try:
                salesforcelastsynctime = dd['properties']['salesforcelastsynctime']
            except :
                salesforcelastsynctime = ''
            try:
                amount = dd['properties']['amount']
            except :
                amount = ''
            try:
                dealstage = dd['properties']['dealstage']
            except :
                dealstage = ''
            try:
                onboardingfrontlink = dd['properties']['onboardingfrontlink']
            except :
                onboardingfrontlink = ''
            try:
                pipeline = dd['properties']['pipeline']
            except :
                pipeline = ''
            try:
                closedate = dd['properties']['closedate']
            except :
                closedate = ''
            try:
                onboardingadminlink = dd['properties']['onboardingadminlink']
            except :
                onboardingadminlink = ''
            try:
                createdate = dd['properties']['createdate']
            except :
                createdate = ''     
            try:
                hs_latest_meeting_activity = dd['properties']['hs_latest_meeting_activity']
            except :
                hs_latest_meeting_activity = ''
            try:
                hs_sales_email_last_replied = dd['properties']['hs_sales_email_last_replied']
            except :
                hs_sales_email_last_replied = ''
            try:
                hubspot_owner_id = dd['properties']['hubspot_owner_id']
            except :
                hubspot_owner_id = ''
            try:
                notes_last_contacted = dd['properties']['notes_last_contacted']
            except :
                notes_last_contacted = ''
            try:
                notes_last_updated = dd['properties']['notes_last_updated']
            except :
                notes_last_updated = ''
            try:
                notes_next_activity_date = dd['properties']['notes_next_activity_date']
            except :
                notes_next_activity_date = ''
            try:
                num_contacted_notes = dd['properties']['num_contacted_notes']
            except :
                num_contacted_notes = ''
            try:
                num_notes = dd['properties']['num_notes']
            except :
                num_notes = ''
            try:
                hs_createdate = dd['properties']['hs_createdate']
            except :
                hs_createdate = ''
            try:
                hubspot_team_id = dd['properties']['hubspot_team_id']
            except :
                hubspot_team_id = ''
            try:
                dealtype = dd['properties']['dealtype']
            except :
                dealtype = ''
            try:
                hs_all_owner_ids = dd['properties']['hs_all_owner_ids']
            except :
                hs_all_owner_ids = ''
            try:
                description = dd['properties']['description']
                description = description.replace(';','',1000)
            except :
                description = ''
            try:
                hs_all_team_ids = dd['properties']['hs_all_team_ids'].replace(';','',1000)
            except :
                hs_all_team_ids = ''
            try:
                hs_all_accessible_team_ids = dd['properties']['hs_all_accessible_team_ids']
            except :
                hs_all_accessible_team_ids = ''
            try:
                num_associated_contacts = dd['properties']['num_associated_contacts']
            except :
                num_associated_contacts = ''
            try:
                closed_lost_reason = dd['properties']['closed_lost_reason']
            except :
                closed_lost_reason = ''
            try:
                closed_won_reason = dd['properties']['closed_won_reason']
            except :
                closed_won_reason = ''
            try:
                chiave_teamwork = dd['properties']['chiave_teamwork']
            except :
                chiave_teamwork = ''

            deals_all_fields_record.append({
                'id' : id ,
                'amount_in_home_currency' : amount_in_home_currency ,
                'days_to_close' : days_to_close ,
                'hs_acv' : hs_acv ,
                'hs_analytics_source' : hs_analytics_source ,
                'hs_analytics_source_data_1' : hs_analytics_source_data_1 ,
                'hs_analytics_source_data_2' : hs_analytics_source_data_2 ,
                'hs_arr' : hs_arr ,
                'hs_campaign' : hs_campaign ,
                'hs_closed_amount' : hs_closed_amount ,
                'hs_closed_amount_in_home_currency' : hs_closed_amount_in_home_currency ,
                'hs_created_by_user_id' : hs_created_by_user_id ,
                'hs_forecast_amount' : hs_forecast_amount ,
                'hs_forecast_probability' : hs_forecast_probability ,
                'hs_is_closed' : hs_is_closed ,
                'hs_is_closed_won' : hs_is_closed_won ,
                'hs_lastmodifieddate' : hs_lastmodifieddate[:10] ,
                'hs_likelihood_to_close' : hs_likelihood_to_close ,
                'hs_manual_forecast_category' : hs_manual_forecast_category ,
                'hs_merged_object_ids' : hs_merged_object_ids ,
                'hs_mrr' : hs_mrr ,
                'hs_next_step' : hs_next_step ,
                'hs_object_id' : hs_object_id ,
                'hs_predicted_amount' : hs_predicted_amount ,
                'hs_predicted_amount_in_home_currency' : hs_predicted_amount_in_home_currency ,
                'hs_projected_amount' : hs_projected_amount ,
                'hs_projected_amount_in_home_currency' : hs_projected_amount_in_home_currency ,
                'hs_tcv' : hs_tcv ,
                'hs_time_in_appointmentscheduled' : hs_time_in_appointmentscheduled ,
                'hs_time_in_closedlost' : hs_time_in_closedlost ,
                'hs_time_in_closedwon' : hs_time_in_closedwon ,
                'hs_time_in_contractsent' : hs_time_in_contractsent ,
                'hs_time_in_decisionmakerboughtin' : hs_time_in_decisionmakerboughtin ,
                'hs_time_in_presentationscheduled' : hs_time_in_presentationscheduled ,
                'hs_time_in_qualifiedtobuy' : hs_time_in_qualifiedtobuy ,
                'hs_unique_creation_key' : hs_unique_creation_key ,
                'hs_updated_by_user_id' : hs_updated_by_user_id ,
                'hs_user_ids_of_all_owners' : hs_user_ids_of_all_owners ,
                'hubspot_owner_assigneddate' : hubspot_owner_assigneddate ,
                'application_uuid3' : application_uuid3 ,
                'dealname' : dealname ,
                'salesforcelastsynctime' : salesforcelastsynctime ,
                'amount' : amount ,
                'dealstage' : dealstage ,
                'onboardingfrontlink' : onboardingfrontlink ,
                'pipeline' : pipeline ,
                'closedate' : closedate ,
                'onboardingadminlink' : onboardingadminlink ,
                'createdate' : createdate ,
                'hs_latest_meeting_activity' : hs_latest_meeting_activity ,
                'hs_sales_email_last_replied' : hs_sales_email_last_replied ,
                'hubspot_owner_id' : hubspot_owner_id ,
                'notes_last_contacted' : notes_last_contacted ,
                'notes_last_updated' : notes_last_updated ,
                'notes_next_activity_date' : notes_next_activity_date ,
                'num_contacted_notes' : num_contacted_notes ,
                'num_notes' : num_notes ,
                'hs_createdate' : hs_createdate ,
                'hubspot_team_id' : hubspot_team_id ,
                'dealtype' : dealtype ,
                'hs_all_owner_ids' : hs_all_owner_ids ,
                'description' : description ,
                'hs_all_team_ids' : hs_all_team_ids ,
                'hs_all_accessible_team_ids' : hs_all_accessible_team_ids ,
                'num_associated_contacts' : num_associated_contacts ,
                'closed_lost_reason' : closed_lost_reason ,
                'closed_won_reason' : closed_won_reason ,
                'miss_tariffa___motivo_ko' : miss_tariffa___motivo_ko ,
                'miss_tariffa___motivo_trash' : miss_tariffa___motivo_trash ,
                'google_ad_click_id' : google_ad_click_id ,
                'tipo_di_ordine' : tipo_di_ordine,
                'chiave_teamwork' : chiave_teamwork 
            })



    deals_all_fields = pd.DataFrame(deals_all_fields_record)


    deals_all_fields['hs_lastmodifieddate'] = pd.to_datetime(deals_all_fields['hs_lastmodifieddate'], format='%Y-%m-%d')

    deals_all_fields = deals_all_fields[(deals_all_fields['hs_lastmodifieddate'] >= start_date) & (deals_all_fields['hs_lastmodifieddate'] <= end_date)]   

    deals_all_fields = deals_all_fields.reset_index(drop = True)
    
    return deals_all_fields




"""

Description for get_hubspot_contact function

MANDATORY INPUT: 

- API_KEY
- start_date string as "yyyy-mm-dd"
- end_date string as "yyyy-mm-dd"



"""



def get_hubspot_contact(API_KEY, start_date, end_date):
    
    from datetime import datetime as dt, timedelta as td, date
    
    
    
    url = "https://api.hubapi.com/crm/v3/objects/contacts"


    utc=pytz.UTC


    i = 20
    after = '1'
    contact_record = []
    def qek(vl1,val2) :
        try :
            if vl1>val2 :
                True
            else :
                False
        except:
            False
    y = 1

    s = requests.Session()


    while i >0 :

        querystring = {"limit": "100", "paginateAssociations": "false" ,"associations":"deals","properties":"contattabile,campaign_content,campaign_medium,campaign_name,campaign_term,source,first_deal_created_date,hs_additional_emails,hs_all_assigned_business_unit_ids,hs_all_contact_vids,hs_analytics_first_touch_converting_campaign,hs_analytics_last_touch_converting_campaign,hs_calculated_form_submissions,hs_calculated_merged_vids,hs_calculated_mobile_number,hs_calculated_phone_number,hs_calculated_phone_number_area_code,hs_calculated_phone_number_country_code,hs_calculated_phone_number_region_code,hs_count_is_unworked,hs_count_is_worked,hs_created_by_conversations,hs_email_domain,hs_email_sends_since_last_engagement,hs_facebook_ad_clicked,hs_first_engagement_object_id,hs_google_click_id,hs_ip_timezone,hs_is_contact,hs_is_unworked,hs_last_sales_activity_date,hs_last_sales_activity_timestamp,hs_lead_status,hs_legal_basis,hs_object_id,hs_predictivescoringtier,hs_sa_first_engagement_date,hs_sa_first_engagement_descr,hs_sa_first_engagement_object_type,hs_sales_email_last_clicked,hs_sales_email_last_opened,hs_searchable_calculated_international_mobile_number,hs_searchable_calculated_international_phone_number,hs_searchable_calculated_mobile_number,hs_searchable_calculated_phone_number,hs_sequences_is_enrolled,hs_user_ids_of_all_owners,hubspot_owner_assigneddate,num_associated_deals,recent_deal_amount,recent_deal_close_date,total_revenue,company,first_conversion_event_name,hs_analytics_first_url,hs_email_delivered,hs_email_optout,currentlyinworkflow,hs_analytics_last_url,hs_email_open,num_conversion_events,website,first_conversion_date,firstname,hs_analytics_num_page_views,hs_analytics_num_visits,recent_conversion_event_name,hs_analytics_first_timestamp,hs_analytics_num_event_completions,hs_social_twitter_clicks,industry,lastname,mobilephone,recent_conversion_date,email,hs_analytics_last_timestamp,hs_email_last_email_name,hs_email_last_send_date,hs_social_facebook_clicks,num_unique_conversion_events,hs_analytics_first_visit_timestamp,hs_analytics_source,hs_email_last_open_date,hs_latest_meeting_activity,hs_sales_email_last_replied,hs_social_linkedin_clicks,hubspot_owner_id,hs_analytics_source_data_1,hs_social_google_plus_clicks,hubspot_team_id,ip_country,hs_all_owner_ids,hs_analytics_last_visit_timestamp,hs_analytics_source_data_2,hs_email_first_send_date,hs_social_num_broadcast_clicks,ip_state,hs_all_team_ids,hs_analytics_first_referrer,hs_email_first_open_date,ip_city,hs_all_accessible_team_ids,hs_analytics_last_referrer,phone,fax,address,hs_analytics_average_page_views,city,hs_analytics_revenue,state,hs_lifecyclestage_lead_date,hs_lifecyclestage_marketingqualifiedlead_date,hs_lifecyclestage_opportunity_date,zip,country,hs_lifecyclestage_salesqualifiedlead_date,jobtitle,hs_lifecyclestage_customer_date,hubspotscore,closedate,hs_lifecyclestage_subscriber_date,hs_lifecyclestage_other_date,lifecyclestage,createdate,lastmodifieddate,days_to_close,associatedcompanyid","after":after,
                    "archived": "false", "hapikey": API_KEY}

        headers = {'accept': 'application/json'}
        response = s.get(url, headers=headers, params=querystring)


        dati = response.json()
        try:
            after = dati['paging']['next']['after']
            i = len(dati['paging']['next']['after'])
        except:
            after = ''
            i = 0
        d1 = dati["results"]
        # campaign_content,campaign_medium,campaign_name,campaign_term
        for dd in d1:
            try:
                upd = dt.strptime(dd['properties']['createdate'][:-1], '%Y-%m-%dT%H:%M:%S.%f')
            except:
                upd = dt.strptime(dd['properties']['createdate'][:-1], '%Y-%m-%dT%H:%M:%S')
            
            begin_date = dt.strptime(start_date, "%Y-%m-%d").date()
            
            start = (date.today() - begin_date).days
            
            begin_date = (dt.today()-td(days=start)).isoformat()
            
            
            try:
                begin_date = dt.strptime(begin_date,'%Y-%m-%dT%H:%M:%S.%f')
            except:
                begin_date = dt.strptime(begin_date,'%Y-%m-%dT%H:%M:%S')
            upd = upd.replace(tzinfo=utc)
            begin_date = begin_date.replace(tzinfo=utc)
            
            
            final_date = dt.strptime(end_date, "%Y-%m-%d").date()

            end = (date.today() - final_date).days
            
            final_date = (dt.today()-td(days=end)).isoformat()
            
            
            try:
                final_date = dt.strptime(final_date,'%Y-%m-%dT%H:%M:%S.%f')
            except:
                final_date = dt.strptime(final_date,'%Y-%m-%dT%H:%M:%S')
            
            
            final_date = final_date.replace(tzinfo=utc)

            
            
            if  upd >= begin_date and upd <= final_date:
                if y%250 == 0:
                    print ("Iteration num.", y)
                y= y+ 1
                try:
                    id = dd['id']
                except :
                    id = ''
                try:
                    source = dd['properties']['source']
                except :
                    source = ''
                try:
                    contattabile = dd['properties']['contattabile']
                except :
                    contattabile = ''
                try:
                    campaign_content = dd['properties']['campaign_content']
                except :
                    campaign_content = ''
                try:
                    campaign_medium = dd['properties']['campaign_medium']
                except :
                    campaign_medium = ''
                try:
                    campaign_name = dd['properties']['campaign_name']
                except :
                    campaign_name = ''
                try:
                    campaign_term = dd['properties']['campaign_term']
                except :
                    campaign_term = ''
                try :
                    deal_id = dd['associations']['deals']['results'][0]['id']
                except :
                    deal_id = ''
                try:
                    first_deal_created_date = dd['properties']['first_deal_created_date']
                except:
                    first_deal_created_date = ''
                try:
                    hs_additional_emails = dd['properties']['hs_additional_emails']
                except:
                    hs_additional_emails = ''
                try:
                    hs_all_assigned_business_unit_ids = dd['properties']['hs_all_assigned_business_unit_ids']
                except:
                    hs_all_assigned_business_unit_ids = ''
                try:
                    hs_all_contact_vids = dd['properties']['hs_all_contact_vids']
                except:
                    hs_all_contact_vids = ''
                try:
                    hs_analytics_first_touch_converting_campaign = dd['properties']['hs_analytics_first_touch_converting_campaign']
                except:
                    hs_analytics_first_touch_converting_campaign = ''
                try:
                    hs_analytics_last_touch_converting_campaign = dd['properties']['hs_analytics_last_touch_converting_campaign']
                except:
                    hs_analytics_last_touch_converting_campaign = ''
                try:
                    hs_calculated_form_submissions = dd['properties']['hs_calculated_form_submissions']
                except:
                    hs_calculated_form_submissions = ''
                try:
                    hs_calculated_merged_vids = dd['properties']['hs_calculated_merged_vids']
                except:
                    hs_calculated_merged_vids = ''
                try:
                    hs_calculated_mobile_number = dd['properties']['hs_calculated_mobile_number']
                except:
                    hs_calculated_mobile_number = ''
                try:
                    hs_calculated_phone_number = dd['properties']['hs_calculated_phone_number']
                except:
                    hs_calculated_phone_number = ''
                try:
                    hs_calculated_phone_number_area_code = dd['properties']['hs_calculated_phone_number_area_code']
                except:
                    hs_calculated_phone_number_area_code = ''
                try:
                    hs_calculated_phone_number_country_code = dd['properties']['hs_calculated_phone_number_country_code']
                except:
                    hs_calculated_phone_number_country_code = ''
                try:
                    hs_calculated_phone_number_region_code = dd['properties']['hs_calculated_phone_number_region_code']
                except:
                    hs_calculated_phone_number_region_code = ''
                try:
                    hs_content_membership_registration_domain_sent_to = dd['properties']['hs_content_membership_registration_domain_sent_to']
                except:
                    hs_content_membership_registration_domain_sent_to = ''
                try:
                    hs_content_membership_registration_email_sent_at = dd['properties']['hs_content_membership_registration_email_sent_at']
                except:
                    hs_content_membership_registration_email_sent_at = ''
                try:
                    hs_count_is_unworked = dd['properties']['hs_count_is_unworked']
                except:
                    hs_count_is_unworked = ''
                try:
                    hs_count_is_worked = dd['properties']['hs_count_is_worked']
                except:
                    hs_count_is_worked = ''
                try:
                    hs_created_by_conversations = dd['properties']['hs_created_by_conversations']
                except:
                    hs_created_by_conversations = ''
                try:
                    hs_email_domain = dd['properties']['hs_email_domain']
                except:
                    hs_email_domain = ''
                try:
                    hs_email_sends_since_last_engagement = dd['properties']['hs_email_sends_since_last_engagement']
                except:
                    hs_email_sends_since_last_engagement = ''
                try:
                    hs_facebook_ad_clicked = dd['properties']['hs_facebook_ad_clicked']
                except:
                    hs_facebook_ad_clicked = ''
                try:
                    hs_first_engagement_object_id = dd['properties']['hs_first_engagement_object_id']
                except:
                    hs_first_engagement_object_id = ''
                try:
                    hs_google_click_id = dd['properties']['hs_google_click_id']
                except:
                    hs_google_click_id = ''
                try:
                    hs_ip_timezone = dd['properties']['hs_ip_timezone']
                except:
                    hs_ip_timezone = ''
                try:
                    hs_is_contact = dd['properties']['hs_is_contact']
                except:
                    hs_is_contact = ''
                try:
                    hs_is_unworked = dd['properties']['hs_is_unworked']
                except:
                    hs_is_unworked = ''
                try:
                    hs_last_sales_activity_date = dd['properties']['hs_last_sales_activity_date']
                except:
                    hs_last_sales_activity_date = ''
                try:
                    hs_last_sales_activity_timestamp = dd['properties']['hs_last_sales_activity_timestamp']
                except:
                    hs_last_sales_activity_timestamp = ''
                try:
                    hs_lead_status = dd['properties']['hs_lead_status']
                except:
                    hs_lead_status = ''
                try:
                    hs_legal_basis = dd['properties']['hs_legal_basis']
                except:
                    hs_legal_basis = ''
                try:
                    hs_object_id = dd['properties']['hs_object_id']
                except:
                    hs_object_id = ''
                try:
                    hs_predictivescoringtier = dd['properties']['hs_predictivescoringtier']
                except:
                    hs_predictivescoringtier = ''
                try:
                    hs_sa_first_engagement_date = dd['properties']['hs_sa_first_engagement_date']
                except:
                    hs_sa_first_engagement_date = ''
                try:
                    hs_sa_first_engagement_descr = dd['properties']['hs_sa_first_engagement_descr']
                except:
                    hs_sa_first_engagement_descr = ''
                try:
                    hs_sa_first_engagement_object_type = dd['properties']['hs_sa_first_engagement_object_type']
                except:
                    hs_sa_first_engagement_object_type = ''
                try:
                    hs_sales_email_last_clicked = dd['properties']['hs_sales_email_last_clicked']
                except:
                    hs_sales_email_last_clicked = ''
                try:
                    hs_sales_email_last_opened = dd['properties']['hs_sales_email_last_opened']
                except:
                    hs_sales_email_last_opened = ''
                try:
                    hs_searchable_calculated_international_mobile_number = dd['properties']['hs_searchable_calculated_international_mobile_number']
                except:
                    hs_searchable_calculated_international_mobile_number = ''
                try:
                    hs_searchable_calculated_international_phone_number = dd['properties']['hs_searchable_calculated_international_phone_number']
                except:
                    hs_searchable_calculated_international_phone_number = ''
                try:
                    hs_searchable_calculated_mobile_number = dd['properties']['hs_searchable_calculated_mobile_number']
                except:
                    hs_searchable_calculated_mobile_number = ''
                try:
                    hs_searchable_calculated_phone_number = dd['properties']['hs_searchable_calculated_phone_number']
                except:
                    hs_searchable_calculated_phone_number = ''
                try:
                    hs_sequences_is_enrolled = dd['properties']['hs_sequences_is_enrolled']
                except:
                    hs_sequences_is_enrolled = ''
                try:
                    hs_time_between_contact_creation_and_deal_close = dd['properties']['hs_time_between_contact_creation_and_deal_close']
                except:
                    hs_time_between_contact_creation_and_deal_close = ''
                try:
                    hs_time_between_contact_creation_and_deal_creation = dd['properties']['hs_time_between_contact_creation_and_deal_creation']
                except:
                    hs_time_between_contact_creation_and_deal_creation = ''
                try:
                    hs_time_to_first_engagement = dd['properties']['hs_time_to_first_engagement']
                except:
                    hs_time_to_first_engagement = ''
                try:
                    hs_time_to_move_from_lead_to_customer = dd['properties']['hs_time_to_move_from_lead_to_customer']
                except:
                    hs_time_to_move_from_lead_to_customer = ''
                try:
                    hs_time_to_move_from_marketingqualifiedlead_to_customer = dd['properties']['hs_time_to_move_from_marketingqualifiedlead_to_customer']
                except:
                    hs_time_to_move_from_marketingqualifiedlead_to_customer = ''
                try:
                    hs_time_to_move_from_opportunity_to_customer = dd['properties']['hs_time_to_move_from_opportunity_to_customer']
                except:
                    hs_time_to_move_from_opportunity_to_customer = ''
                try:
                    hs_time_to_move_from_salesqualifiedlead_to_customer = dd['properties']['hs_time_to_move_from_salesqualifiedlead_to_customer']
                except:
                    hs_time_to_move_from_salesqualifiedlead_to_customer = ''
                try:
                    hs_time_to_move_from_subscriber_to_customer = dd['properties']['hs_time_to_move_from_subscriber_to_customer']
                except:
                    hs_time_to_move_from_subscriber_to_customer = ''
                try:
                    hs_user_ids_of_all_owners = dd['properties']['hs_user_ids_of_all_owners']
                except:
                    hs_user_ids_of_all_owners = ''
                try:
                    hubspot_owner_assigneddate = dd['properties']['hubspot_owner_assigneddate']
                except:
                    hubspot_owner_assigneddate = ''
                try:
                    ip__ecomm_bridge__ecomm_synced = dd['properties']['ip__ecomm_bridge__ecomm_synced']
                except:
                    ip__ecomm_bridge__ecomm_synced = ''
                try:
                    ip__ecomm_bridge__source_app_id = dd['properties']['ip__ecomm_bridge__source_app_id']
                except:
                    ip__ecomm_bridge__source_app_id = ''
                try:
                    ip__ecomm_bridge__source_store_id = dd['properties']['ip__ecomm_bridge__source_store_id']
                except:
                    ip__ecomm_bridge__source_store_id = ''
                try:
                    ip__sync_extension__external_source_account_id = dd['properties']['ip__sync_extension__external_source_account_id']
                except:
                    ip__sync_extension__external_source_account_id = ''
                try:
                    ip__sync_extension__external_source_app_id = dd['properties']['ip__sync_extension__external_source_app_id']
                except:
                    ip__sync_extension__external_source_app_id = ''
                try:
                    ip_country_code = dd['properties']['ip_country_code']
                except:
                    ip_country_code = ''
                try:
                    ip_state_code = dd['properties']['ip_state_code']
                except:
                    ip_state_code = ''
                try:
                    ip_zipcode = dd['properties']['ip_zipcode']
                except:
                    ip_zipcode = ''
                try:
                    num_associated_deals = dd['properties']['num_associated_deals']
                except:
                    num_associated_deals = ''
                try:
                    recent_deal_amount = dd['properties']['recent_deal_amount']
                except:
                    recent_deal_amount = ''
                try:
                    recent_deal_close_date = dd['properties']['recent_deal_close_date']
                except:
                    recent_deal_close_date = ''
                try:
                    total_revenue = dd['properties']['total_revenue']
                except:
                    total_revenue = ''
                try:
                    blog_api_demonstration_blog_subscription = dd['properties']['blog_api_demonstration_blog_subscription']
                except:
                    blog_api_demonstration_blog_subscription = ''
                try:
                    blog_example_blog_10500366470_subscription = dd['properties']['blog_example_blog_10500366470_subscription']
                except:
                    blog_example_blog_10500366470_subscription = ''
                try:
                    company = dd['properties']['company']
                except:
                    company = ''
                try:
                    first_conversion_event_name = dd['properties']['first_conversion_event_name']
                except:
                    first_conversion_event_name = ''
                try:
                    hs_analytics_first_url = dd['properties']['hs_analytics_first_url']
                except:
                    hs_analytics_first_url = ''
                try:
                    hs_email_delivered = dd['properties']['hs_email_delivered']
                except:
                    hs_email_delivered = ''
                try:
                    hs_email_optout = dd['properties']['hs_email_optout']
                except:
                    hs_email_optout = ''
                try:
                    currentlyinworkflow = dd['properties']['currentlyinworkflow']
                except:
                    currentlyinworkflow = ''
                try:
                    hs_analytics_last_url = dd['properties']['hs_analytics_last_url']
                except:
                    hs_analytics_last_url = ''
                try:
                    hs_email_open = dd['properties']['hs_email_open']
                except:
                    hs_email_open = ''
                try:
                    num_conversion_events = dd['properties']['num_conversion_events']
                except:
                    num_conversion_events = ''
                try:
                    website = dd['properties']['website']
                except:
                    website = ''
                try:
                    first_conversion_date = dd['properties']['first_conversion_date']
                except:
                    first_conversion_date = ''
                try:
                    firstname = dd['properties']['firstname']
                except:
                    firstname = ''
                try:
                    hs_analytics_num_page_views = dd['properties']['hs_analytics_num_page_views']
                except:
                    hs_analytics_num_page_views = ''
                try:
                    hs_analytics_num_visits = dd['properties']['hs_analytics_num_visits']
                except:
                    hs_analytics_num_visits = ''
                try:
                    recent_conversion_event_name = dd['properties']['recent_conversion_event_name']
                except:
                    recent_conversion_event_name = ''
                try:
                    hs_analytics_first_timestamp = dd['properties']['hs_analytics_first_timestamp']
                except:
                    hs_analytics_first_timestamp = ''
                try:
                    hs_analytics_num_event_completions = dd['properties']['hs_analytics_num_event_completions']
                except:
                    hs_analytics_num_event_completions = ''
                try:
                    hs_social_twitter_clicks = dd['properties']['hs_social_twitter_clicks']
                except:
                    hs_social_twitter_clicks = ''
                try:
                    industry = dd['properties']['industry']
                except:
                    industry = ''
                try:
                    lastname = dd['properties']['lastname']
                except:
                    lastname = ''
                try:
                    mobilephone = dd['properties']['mobilephone']
                except:
                    mobilephone = ''
                try:
                    recent_conversion_date = dd['properties']['recent_conversion_date']
                except:
                    recent_conversion_date = ''
                try:
                    email = dd['properties']['email']
                except:
                    email = ''
                try:
                    hs_analytics_last_timestamp = dd['properties']['hs_analytics_last_timestamp']
                except:
                    hs_analytics_last_timestamp = ''
                try:
                    hs_email_last_email_name = dd['properties']['hs_email_last_email_name']
                except:
                    hs_email_last_email_name = ''
                try:
                    hs_email_last_send_date = dd['properties']['hs_email_last_send_date']
                except:
                    hs_email_last_send_date = ''
                try:
                    hs_social_facebook_clicks = dd['properties']['hs_social_facebook_clicks']
                except:
                    hs_social_facebook_clicks = ''
                try:
                    num_unique_conversion_events = dd['properties']['num_unique_conversion_events']
                except:
                    num_unique_conversion_events = ''
                try:
                    engagements_last_meeting_booked = dd['properties']['engagements_last_meeting_booked']
                except:
                    engagements_last_meeting_booked = ''
                try:
                    engagements_last_meeting_booked_campaign = dd['properties']['engagements_last_meeting_booked_campaign']
                except:
                    engagements_last_meeting_booked_campaign = ''
                try:
                    engagements_last_meeting_booked_medium = dd['properties']['engagements_last_meeting_booked_medium']
                except:
                    engagements_last_meeting_booked_medium = ''
                try:
                    engagements_last_meeting_booked_source = dd['properties']['engagements_last_meeting_booked_source']
                except:
                    engagements_last_meeting_booked_source = ''
                try:
                    hs_analytics_first_visit_timestamp = dd['properties']['hs_analytics_first_visit_timestamp']
                except:
                    hs_analytics_first_visit_timestamp = ''
                try:
                    hs_analytics_source = dd['properties']['hs_analytics_source']
                except:
                    hs_analytics_source = ''
                try:
                    hs_email_last_open_date = dd['properties']['hs_email_last_open_date']
                except:
                    hs_email_last_open_date = ''
                try:
                    hs_latest_meeting_activity = dd['properties']['hs_latest_meeting_activity']
                except:
                    hs_latest_meeting_activity = ''
                try:
                    hs_sales_email_last_replied = dd['properties']['hs_sales_email_last_replied']
                except:
                    hs_sales_email_last_replied = ''
                try:
                    hs_social_linkedin_clicks = dd['properties']['hs_social_linkedin_clicks']
                except:
                    hs_social_linkedin_clicks = ''
                try:
                    hubspot_owner_id = dd['properties']['hubspot_owner_id']
                except:
                    hubspot_owner_id = ''
                try:
                    notes_last_contacted = dd['properties']['notes_last_contacted']
                except:
                    notes_last_contacted = ''
                try:
                    notes_last_updated = dd['properties']['notes_last_updated']
                except:
                    notes_last_updated = ''
                try:
                    notes_next_activity_date = dd['properties']['notes_next_activity_date']
                except:
                    notes_next_activity_date = ''
                try:
                    num_contacted_notes = dd['properties']['num_contacted_notes']
                except:
                    num_contacted_notes = ''
                try:
                    num_notes = dd['properties']['num_notes']
                except:
                    num_notes = ''
                try:
                    hs_analytics_source_data_1 = dd['properties']['hs_analytics_source_data_1']
                except:
                    hs_analytics_source_data_1 = ''
                try:
                    hs_social_google_plus_clicks = dd['properties']['hs_social_google_plus_clicks']
                except:
                    hs_social_google_plus_clicks = ''
                try:
                    hubspot_team_id = dd['properties']['hubspot_team_id']
                except:
                    hubspot_team_id = ''
                try:
                    ip_country = dd['properties']['ip_country']
                except:
                    ip_country = ''
                try:
                    hs_all_owner_ids = dd['properties']['hs_all_owner_ids']
                except:
                    hs_all_owner_ids = ''
                try:
                    hs_analytics_last_visit_timestamp = dd['properties']['hs_analytics_last_visit_timestamp']
                except:
                    hs_analytics_last_visit_timestamp = ''
                try:
                    hs_analytics_source_data_2 = dd['properties']['hs_analytics_source_data_2']
                except:
                    hs_analytics_source_data_2 = ''
                try:
                    hs_email_first_send_date = dd['properties']['hs_email_first_send_date']
                except:
                    hs_email_first_send_date = ''
                try:
                    hs_social_num_broadcast_clicks = dd['properties']['hs_social_num_broadcast_clicks']
                except:
                    hs_social_num_broadcast_clicks = ''
                try:
                    ip_state = dd['properties']['ip_state']
                except:
                    ip_state = ''
                try:
                    hs_all_team_ids = dd['properties']['hs_all_team_ids']
                except:
                    hs_all_team_ids = ''
                try:
                    hs_analytics_first_referrer = dd['properties']['hs_analytics_first_referrer']
                except:
                    hs_analytics_first_referrer = ''
                try:
                    hs_email_first_open_date = dd['properties']['hs_email_first_open_date']
                except:
                    hs_email_first_open_date = ''
                try:
                    ip_city = dd['properties']['ip_city']
                except:
                    ip_city = ''
                try:
                    hs_all_accessible_team_ids = dd['properties']['hs_all_accessible_team_ids']
                except:
                    hs_all_accessible_team_ids = ''
                try:
                    hs_analytics_last_referrer = dd['properties']['hs_analytics_last_referrer']
                except:
                    hs_analytics_last_referrer = ''
                try:
                    phone = dd['properties']['phone']
                except:
                    phone = ''
                try:
                    fax = dd['properties']['fax']
                except:
                    fax = ''
                try:
                    address = dd['properties']['address']
                except:
                    address = ''
                try:
                    hs_analytics_average_page_views = dd['properties']['hs_analytics_average_page_views']
                except:
                    hs_analytics_average_page_views = ''
                try:
                    city = dd['properties']['city']
                except:
                    city = ''
                try:
                    hs_analytics_revenue = dd['properties']['hs_analytics_revenue']
                except:
                    hs_analytics_revenue = ''
                try:
                    state = dd['properties']['state']
                except:
                    state = ''
                try:
                    hs_lifecyclestage_lead_date = dd['properties']['hs_lifecyclestage_lead_date']
                except:
                    hs_lifecyclestage_lead_date = ''
                try:
                    hs_lifecyclestage_marketingqualifiedlead_date = dd['properties']['hs_lifecyclestage_marketingqualifiedlead_date']
                except:
                    hs_lifecyclestage_marketingqualifiedlead_date = ''
                try:
                    hs_lifecyclestage_opportunity_date = dd['properties']['hs_lifecyclestage_opportunity_date']
                except:
                    hs_lifecyclestage_opportunity_date = ''
                try:
                    zip = dd['properties']['zip']
                except:
                    zip = ''
                try:
                    country = dd['properties']['country']
                except:
                    country = ''
                try:
                    hs_lifecyclestage_salesqualifiedlead_date = dd['properties']['hs_lifecyclestage_salesqualifiedlead_date']
                except:
                    hs_lifecyclestage_salesqualifiedlead_date = ''
                try:
                    jobtitle = dd['properties']['jobtitle']
                except:
                    jobtitle = ''
                try:
                    hs_lifecyclestage_customer_date = dd['properties']['hs_lifecyclestage_customer_date']
                except:
                    hs_lifecyclestage_customer_date = ''
                try:
                    hubspotscore = dd['properties']['hubspotscore']
                except:
                    hubspotscore = ''
                try:
                    closedate = dd['properties']['closedate']
                except:
                    closedate = ''
                try:
                    hs_lifecyclestage_subscriber_date = dd['properties']['hs_lifecyclestage_subscriber_date']
                except:
                    hs_lifecyclestage_subscriber_date = ''
                try:
                    hs_lifecyclestage_other_date = dd['properties']['hs_lifecyclestage_other_date']
                except:
                    hs_lifecyclestage_other_date = ''
                try:
                    lifecyclestage = dd['properties']['lifecyclestage']
                except:
                    lifecyclestage = ''
                try:
                    createdate = dd['properties']['createdate']
                except:
                    createdate = ''
                try:
                    lastmodifieddate = dd['properties']['lastmodifieddate']
                except:
                    lastmodifieddate = ''
                try:
                    associatedcompanyid = dd['properties']['associatedcompanyid']
                except:
                    associatedcompanyid = ''
                try:
                    days_to_close = dd['properties']['days_to_close']
                except:
                    days_to_close = ''
                contact_record.append({
                'id' : id ,

                'first_deal_created_date' : first_deal_created_date,
                'hs_additional_emails' : hs_additional_emails,
                'hs_all_assigned_business_unit_ids' : hs_all_assigned_business_unit_ids,
                'hs_all_contact_vids' : hs_all_contact_vids,
                'irst_touch_converting_campaign' : hs_analytics_first_touch_converting_campaign,
                'last_touch_converting_campaign' : hs_analytics_last_touch_converting_campaign,
                'hs_form_submissions' : hs_calculated_form_submissions,
                'hs_merged_vids' : hs_calculated_merged_vids,
                'hs_mobile_number' : hs_calculated_mobile_number,
                'hs_phone_number' : hs_calculated_phone_number,
                'hs_phone_number_area_code' : hs_calculated_phone_number_area_code,
                'hs_phone_number_country_code' : hs_calculated_phone_number_country_code,
                'hs_phone_number_region_code' : hs_calculated_phone_number_region_code,
                'hs_content_domain_sent_to' : hs_content_membership_registration_domain_sent_to,
                'hs_content_email_sent_at' : hs_content_membership_registration_email_sent_at,
                'hs_count_is_unworked' : hs_count_is_unworked,
                'hs_count_is_worked' : hs_count_is_worked,
                'hs_created_by_conversations' : hs_created_by_conversations,
                'hs_email_domain' : hs_email_domain,
                'hs_email_sends_since_last_engagement' : hs_email_sends_since_last_engagement,
                'hs_facebook_ad_clicked' : hs_facebook_ad_clicked,
                'hs_first_engagement_object_id' : hs_first_engagement_object_id,
                'hs_google_click_id' : hs_google_click_id,
                'hs_ip_timezone' : hs_ip_timezone,
                'hs_is_contact' : hs_is_contact,
                'hs_is_unworked' : hs_is_unworked,
                'hs_last_sales_activity_date' : hs_last_sales_activity_date,
                'hs_last_sales_activity_timestamp' : hs_last_sales_activity_timestamp,
                'hs_lead_status' : hs_lead_status,
                'hs_legal_basis' : hs_legal_basis,
                'hs_object_id' : hs_object_id,
                'hs_predictivescoringtier' : hs_predictivescoringtier,
                'hs_sa_first_engagement_date' : hs_sa_first_engagement_date,
                'hs_sa_first_engagement_descr' : hs_sa_first_engagement_descr,
                'hs_sa_first_engagement_object_type' : hs_sa_first_engagement_object_type,
                'hs_sales_email_last_clicked' : hs_sales_email_last_clicked,
                'hs_sales_email_last_opened' : hs_sales_email_last_opened,
                'hs_searchable_calculated_mobile_number' : hs_searchable_calculated_mobile_number,
                'hs_searchable_calculated_phone_number' : hs_searchable_calculated_phone_number,
                'hs_sequences_is_enrolled' : hs_sequences_is_enrolled,
                'hs_time_deal_creation' : hs_time_between_contact_creation_and_deal_creation,
                'hs_time_to_first_engagement' : hs_time_to_first_engagement,
                'hs_time_lead_to_customer' : hs_time_to_move_from_lead_to_customer,
                'hs_time_to_customer' : hs_time_to_move_from_marketingqualifiedlead_to_customer,
                'hs_user_ids_of_all_owners' : hs_user_ids_of_all_owners,
                'hubspot_owner_assigneddate' : hubspot_owner_assigneddate,
                'num_associated_deals' : num_associated_deals,
                'recent_deal_amount' : recent_deal_amount,
                'recent_deal_close_date' : recent_deal_close_date,
                'total_revenue' : total_revenue,
                'blog_api' : blog_api_demonstration_blog_subscription,
                'blog_example_' : blog_example_blog_10500366470_subscription,
                'company' : company,
                'first_conversion_event_name' : first_conversion_event_name,
                'hs_analytics_first_url' : hs_analytics_first_url,
                'hs_email_delivered' : hs_email_delivered,
                'hs_email_optout' : hs_email_optout,
                'currentlyinworkflow' : currentlyinworkflow,
                'hs_analytics_last_url' : hs_analytics_last_url,
                'hs_email_open' : hs_email_open,
                'num_conversion_events' : num_conversion_events,
                'website' : website,
                'first_conversion_date' : first_conversion_date,
                'firstname' : firstname,
                'hs_analytics_num_page_views' : hs_analytics_num_page_views,
                'hs_analytics_num_visits' : hs_analytics_num_visits,
                'recent_conversion_event_name' : recent_conversion_event_name,
                'hs_analytics_first_timestamp' : hs_analytics_first_timestamp,
                'hs_analytics_num_event_completions' : hs_analytics_num_event_completions,
                'hs_social_twitter_clicks' : hs_social_twitter_clicks,
                'industry' : industry,
                'lastname' : lastname,
                'mobilephone' : mobilephone,
                'recent_conversion_date' : recent_conversion_date,
                'email' : email,
                'hs_analytics_last_timestamp' : hs_analytics_last_timestamp,
                'hs_email_last_email_name' : hs_email_last_email_name,
                'hs_email_last_send_date' : hs_email_last_send_date,
                'hs_social_facebook_clicks' : hs_social_facebook_clicks,
                'num_unique_conversion_events' : num_unique_conversion_events,
                'hs_analytics_source' : hs_analytics_source,
                'hs_email_last_open_date' : hs_email_last_open_date,
                'hs_latest_meeting_activity' : hs_latest_meeting_activity,
                'hs_sales_email_last_replied' : hs_sales_email_last_replied,
                'hs_social_linkedin_clicks' : hs_social_linkedin_clicks,
                'hubspot_owner_id' : hubspot_owner_id,
                'notes_last_contacted' : notes_last_contacted,
                'notes_last_updated' : notes_last_updated,
                'notes_next_activity_date' : notes_next_activity_date,
                'num_contacted_notes' : num_contacted_notes,
                'num_notes' : num_notes,
                'hs_analytics_source_data_1' : hs_analytics_source_data_1,
                'hs_social_google_plus_clicks' : hs_social_google_plus_clicks,
                'hubspot_team_id' : hubspot_team_id,
                'ip_country' : ip_country,
                'hs_all_owner_ids' : hs_all_owner_ids,
                'hs_analytics_last_visit_timestamp' : hs_analytics_last_visit_timestamp,
                'hs_analytics_source_data_2' : hs_analytics_source_data_2,
                'hs_email_first_send_date' : hs_email_first_send_date,
                'hs_social_num_broadcast_clicks' : hs_social_num_broadcast_clicks,
                'ip_state' : ip_state,
                'hs_all_team_ids' : hs_all_team_ids,
                'hs_analytics_first_referrer' : hs_analytics_first_referrer,
                'hs_email_first_open_date' : hs_email_first_open_date,
                'ip_city' : ip_city,
                'hs_all_accessible_team_ids' : hs_all_accessible_team_ids,
                'hs_analytics_last_referrer' : hs_analytics_last_referrer,
                'phone' : phone,
                'fax' : fax,
                'address' : address,
                'hs_analytics_average_page_views' : hs_analytics_average_page_views,
                'city' : city,
                'hs_analytics_revenue' : hs_analytics_revenue,
                'state' : state,
                'hs_lifecyclestage_lead_date' : hs_lifecyclestage_lead_date,
                'hs_lifecyclestage_marketingqualifiedlead_date' : hs_lifecyclestage_marketingqualifiedlead_date,
                'hs_lifecyclestage_opportunity_date' : hs_lifecyclestage_opportunity_date,
                'zip' : zip,
                'country' : country,
                'hs_lifecyclestage_salesqualifiedlead_date' : hs_lifecyclestage_salesqualifiedlead_date,
                'jobtitle' : jobtitle,
                'hs_lifecyclestage_customer_date' : hs_lifecyclestage_customer_date,
                'hubspotscore' : hubspotscore,
                'closedate' : closedate,
                'hs_lifecyclestage_subscriber_date' : hs_lifecyclestage_subscriber_date,
                'hs_lifecyclestage_other_date' : hs_lifecyclestage_other_date,
                'lifecyclestage' : lifecyclestage,
                'createdate' : createdate,
                'lastmodifieddate' : lastmodifieddate,
                'associatedcompanyid' : associatedcompanyid,
                'days_to_close' : days_to_close,
                'deal_id' : deal_id,
                'source'  : source,
                'campaign_content' : campaign_content,
                'campaign_medium' : campaign_medium,
                'campaign_name' : campaign_name,
                'campaign_term' : campaign_term,
                'contattabile' : contattabile

                })


    contact = pd.DataFrame(contact_record)
    

    return contact








"""

Description for get_hubspot_pipeline function

MANDATORY INPUT: API_KEY



"""

def get_hubspot_pipelines(API_KEY):                    
    
    from datetime import date as dt, timedelta as td , datetime, timezone


    client = Hubspot3(api_key=API_KEY)

    pipelines_client = client.crm_pipelines.get_all()

    pipeline_dati = []

    for d in pipelines_client:
        for s in d['stages']:
            pipeline_dati.append({
                "label" : d['label'],
                "active" : d['active'],
                "object_type" : d['objectType'],
                "pipeline_id" : d['pipelineId'],
                "created_at" : d['createdAt'],
                "updatet_at" : d['updatedAt'],
                "stage_name" : s['label'],
                "stage_id" : s['stageId'],
                "is_close" : s['metadata']['isClosed']

            })


    pipelines = pd.DataFrame(pipeline_dati)

    pipelines["created_at"] = pd.to_datetime(pipelines["created_at"], unit='ms')

    pipelines["updatet_at"] = pd.to_datetime(pipelines["updatet_at"], unit='ms')

    return pipelines
        



"""

Description for get_hubspot_users function

MANDATORY INPUT: API_KEY


"""

def get_hubspot_users(API_KEY):

    from datetime import date as dt, timedelta as td , datetime, timezone


    url = f"https://api.hubapi.com/owners/v2/owners?hapikey={API_KEY}"

    r= requests.get(url = url)
    dati = r.json()
    users_records = []
    for d in list(dati):
        try:
            users_records.append({
                "portalid" : d["portalId"],
                "ownerid" : d["ownerId"],
                "type" : d["type"],
                "firstname" : d["firstName"],
                "lastname" : d["lastName"],
                "email" : d["email"],
                "is_active" : d["isActive"]
            })

        except:
            pass

    users = pd.DataFrame(users_records)

    return users