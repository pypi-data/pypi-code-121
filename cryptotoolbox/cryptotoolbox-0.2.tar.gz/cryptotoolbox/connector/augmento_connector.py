#!/usr/bin/env python3
# coding: utf-8

import requests
import pandas as pd
import math
import datetime
from cryptotoolbox.connector import crypto_connector


def convert_string(s):
    from dateutil import parser
    dt_object = parser.parse(s)
    return dt_object.timestamp()

def convert_datetime(d):
    return str(d.date())+'T00:00:00Z'


def get_events_augmento(currency='bitcoin', startdate='2018-01-01T00:00:00Z', enddate='2019-10-01T00:00:00Z', source='twitter', precision='24H', local_root_directory=None):
    r = requests.request("GET", "http://api-dev.augmento.ai/v0.1/coins")
    # print('Coins available\n', r.content, '\n')
    r = requests.request("GET", "http://api-dev.augmento.ai/v0.1/sources")
    # print('Sources available\n', r.content, '\n')
    topics = requests.request("GET", "http://api-dev.augmento.ai/v0.1/topics").json()
    # print('Topics available\n', topics, '\n')
    topics = topics.values()

    startdate_unix, enddate_unix = startdate.timestamp(), enddate.timestamp()
    precision_dct = {'1H':3600, '24H':3600*24, 'hour': 3600, 'daily': 3600*24}
    runs, rest = divmod((enddate_unix-startdate_unix)/precision_dct[precision], 1000)
    rest = int(math.ceil(rest))
    url = "http://api-dev.augmento.ai/v0.1/events/aggregated"
    params = {
      "source" : source,
      "coin" : currency,
      "bin_size" : precision,
      "count_ptr" : 1000,
      "start_ptr" : 0,
      "start_datetime": convert_datetime(startdate),
      "end_datetime" : convert_datetime(enddate)} # "start_datetime" : "2019-05-01T00:00:00Z",
    output = pd.DataFrame()
    print(params)
    if runs != 0:
        for run in range(int(runs)):
            r = requests.request("GET", url, params=params)
            if r.status_code != 200:
                raise RuntimeError(r.json()['error']['message']) #resp.json()['error']['message']
            tmp = pd.DataFrame(r.json())
            tmp = pd.DataFrame(tmp['counts'].tolist(),index = tmp.datetime, columns = topics)
            output = pd.concat([output, tmp])
            params.update({'start_datetime': output.index.max()})
    #params['start_datetime'] = startdate
    params.update({'count_ptr': rest})
    print(params)
    r = requests.request("GET", url, params=params)
    if r.status_code != 200:
        raise RuntimeError(r.json()['error']['message'])
    elif len(r.json()) == 0:
        pass
    else:
        tmp = pd.DataFrame(r.json())
        tmp = pd.DataFrame(tmp['counts'].tolist(),index = tmp.datetime, columns = topics)
        output = pd.concat([output, tmp])
    output = output.drop_duplicates()
    return output


def get_daily_data_augmento(currency='BTC', startdate=None, enddate=None, local_root_directory=None, target_present=False):
    currency_dict = {'BTC': 'bitcoin', 'ETH': 'ethereum'}
    frequence = 'daily'

    twitter = get_events_augmento(currency=currency_dict[currency], startdate=startdate, enddate=enddate, source='twitter', precision='24H', local_root_directory=local_root_directory)
    reddit = get_events_augmento(currency=currency_dict[currency], startdate=startdate, enddate=enddate, source='reddit', precision='24H', local_root_directory=local_root_directory)
    bitcointalk = get_events_augmento(currency=currency_dict[currency], startdate=startdate, enddate=enddate, source='bitcointalk', precision='24H', local_root_directory=local_root_directory)

    twitter = twitter.reset_index()
    twitter['datetime'] = pd.to_datetime(twitter.datetime)
    twitter = twitter.set_index(twitter.datetime)
    twitter.index = twitter.index.tz_convert(None)
    twitter = twitter.drop(columns=['datetime'])
    twitter = twitter.add_prefix('twitter_')

    reddit = reddit.reset_index()
    reddit['datetime'] = pd.to_datetime(reddit.datetime)
    reddit = reddit.set_index(reddit.datetime)
    reddit.index = reddit.index.tz_convert(None)
    reddit = reddit.drop(columns=['datetime'])
    reddit = reddit.add_prefix('reddit_')

    bitcointalk = bitcointalk.reset_index()
    bitcointalk['datetime'] = pd.to_datetime(bitcointalk.datetime)
    bitcointalk = bitcointalk.set_index(bitcointalk.datetime)
    bitcointalk.index = bitcointalk.index.tz_convert(None)
    bitcointalk = bitcointalk.drop(columns=['datetime'])
    bitcointalk = bitcointalk.add_prefix('bitcointalk_')

    aggregated_df = twitter.copy()
    aggregated_df = aggregated_df.merge(reddit, left_index=True, right_index=True)
    aggregated_df = aggregated_df.merge(bitcointalk, left_index=True, right_index=True)

    # start_datetime = datetime.datetime.fromtimestamp(convert_string(startdate))
    # end_datetime = datetime.datetime.fromtimestamp(convert_string(enddate))

    if target_present:
        freqly_pkl_file_name_suffix = '_' + frequence + '_returns.pkl'
        refetch_all = True
        starting_date = startdate
        running_date = enddate
        underlying_df = napoleon_connector.fetch_crypto_daily_data(ssj=currency, local_root_directory=local_root_directory,
                                                               daily_return_pkl_filename_suffix=freqly_pkl_file_name_suffix,
                                                               refetch_all=refetch_all,
                                                               daily_crypto_starting_day=starting_date,
                                                               daily_crypto_ending_day=running_date)
        underlying_df = underlying_df.drop(columns=['volumeto'])
        underlying_df = underlying_df.rename(columns={'volumefrom': 'volume'})
        aggregated_df = aggregated_df.merge(underlying_df, left_index=True, right_index=True)

    dates_stub = startdate.strftime('%d_%b_%Y') + '_' + enddate.strftime('%d_%b_%Y')
    augmento_suffix = '_augmento.pkl'
    pickle_saving_path = local_root_directory + currency + '_' + frequence + '_' + dates_stub + augmento_suffix
    aggregated_df.to_pickle(pickle_saving_path)
    return aggregated_df


def get_hourly_data_augmento(currency='BTC', startdate=None, enddate=None, local_root_directory=None, target_present=False):
    currency_dict = {'BTC': 'bitcoin', 'ETH': 'ethereum'}
    frequence = 'hourly'

    twitter = get_events_augmento(currency=currency_dict[currency], startdate=startdate, enddate=enddate, source='twitter', precision='1H', local_root_directory=local_root_directory)
    reddit = get_events_augmento(currency=currency_dict[currency], startdate=startdate, enddate=enddate, source='reddit', precision='1H', local_root_directory=local_root_directory)
    bitcointalk = get_events_augmento(currency=currency_dict[currency], startdate=startdate, enddate=enddate, source='bitcointalk', precision='1H', local_root_directory=local_root_directory)

    twitter = twitter.reset_index()
    twitter['datetime'] = pd.to_datetime(twitter.datetime)
    twitter = twitter.set_index(twitter.datetime)
    twitter.index = twitter.index.tz_convert(None)
    twitter = twitter.drop(columns=['datetime'])
    twitter = twitter.add_prefix('twitter_')

    reddit = reddit.reset_index()
    reddit['datetime'] = pd.to_datetime(reddit.datetime)
    reddit = reddit.set_index(reddit.datetime)
    reddit.index = reddit.index.tz_convert(None)
    reddit = reddit.drop(columns=['datetime'])
    reddit = reddit.add_prefix('reddit_')

    bitcointalk = bitcointalk.reset_index()
    bitcointalk['datetime'] = pd.to_datetime(bitcointalk.datetime)
    bitcointalk = bitcointalk.set_index(bitcointalk.datetime)
    bitcointalk.index = bitcointalk.index.tz_convert(None)
    bitcointalk = bitcointalk.drop(columns=['datetime'])
    bitcointalk = bitcointalk.add_prefix('bitcointalk_')

    aggregated_df = twitter.copy()
    aggregated_df = aggregated_df.merge(reddit, left_index=True, right_index=True)
    aggregated_df = aggregated_df.merge(bitcointalk, left_index=True, right_index=True)

    # start_datetime = datetime.datetime.fromtimestamp(convert_string(startdate))
    # end_datetime = datetime.datetime.fromtimestamp(convert_string(enddate))

    if target_present:
        freqly_pkl_file_name_suffix = '_' + frequence + '_returns.pkl'
        refetch_all = True
        starting_date = startdate
        running_date = enddate
        underlying_df = napoleon_connector.fetch_crypto_hourly_data(ssj = currency, local_root_directory=local_root_directory, hourly_return_pkl_filename_suffix = freqly_pkl_file_name_suffix, refetch_all = refetch_all,daily_crypto_starting_day=starting_date,daily_crypto_ending_day= running_date)
        underlying_df = underlying_df.drop(columns=['volumeto'])
        underlying_df = underlying_df.rename(columns={'volumefrom': 'volume'})
        aggregated_df = aggregated_df.merge(underlying_df, left_index=True, right_index=True)

    dates_stub = startdate.strftime('%d_%b_%Y') + '_' + enddate.strftime('%d_%b_%Y')
    augmento_suffix = '_augmento.pkl'
    pickle_saving_path = local_root_directory + currency + '_' + frequence + '_' + dates_stub + augmento_suffix
    aggregated_df.to_pickle(pickle_saving_path)
    return aggregated_df