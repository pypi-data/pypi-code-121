#required imports
import json
import requests
import pandas as pd
from datetime import datetime
import holidays

#other module imports
from .constants import parameter_to_return_value
from .functions_aux import __build_dictionary,__fill_dataframe_gaps
from .functions_time import from_local_time_to_utc, split_dates

def get_sensor_tree(user, pwd, add_sensor_names=False):
    '''
    :param user: metrikus api username
    :param pwd: metrikus api password
    :param add_sensor_names: if True -> it will look for the names of the sensors in various fields like "name", "description", and "area ID"
    :return: dataframe with all sensors for all buildings found within a project
    '''
    # Get portolios associated to key
    parent_href = 'https://app.metrikus.io/cat'
    category_name = 'Portfolio name: '
    portfolios = __build_dictionary(parent_href, category_name, user, pwd, separator="'")

    df_rows = []
    # get buildings
    for portfolio in portfolios:
        parent_href = portfolios[portfolio][0]
        category_name = 'Project name: '
        buildings = __build_dictionary(parent_href, category_name, user, pwd, separator="'")

        # get floors ("asset groups")
        for building in buildings:
            parent_href = buildings[building][0]
            category_name = 'Asset group '
            groups = __build_dictionary(parent_href, category_name, user, pwd, separator="'")

            # Get sensor types (type + status)
            for group in groups:
                parent_href = groups[group][0]
                category_name = 'Asset type: '
                sensor_types = __build_dictionary(parent_href, category_name, user, pwd, separator="'")

                for sensor_type in sensor_types:
                    sensor_hrefs = sensor_types[sensor_type]
                    num_unknown = 0
                    for sensor_href in sensor_hrefs:
                        name_available = True
                        # get sensor name
                        if add_sensor_names:
                            features = __build_dictionary(sensor_href, "", user, pwd, separator="")
                            # print("****",features,"****")
                            print(sensor_href.split("/")[-1])
                            if 'Name' in features:
                                parent_href = features['Name'][0] + "/c"
                            elif 'Description' in features:
                                parent_href = features['Description'][0] + "/c"
                            elif 'Area ID' in features:
                                parent_href = features['Area ID'][0] + "/c"
                            else:
                                name_available = False
                            if name_available:
                                response = requests.get(parent_href, auth=(user, pwd))
                                r = response.json()
                                sensor_name = r['value']
                            else:
                                num_unknown += 1
                                sensor_name = "Unknown"
                            print(sensor_name)
                            df_row = [portfolio, building, group, sensor_type.split('~')[0], sensor_type.split('~')[1],
                                      sensor_name, sensor_href, sensor_href.split("/")[-1]]
                            columns = ["project", "building", "group", "sensor_type", "sensor_status", "sensor_name",
                                       "sensor_href", "asset_id"]
                        else:
                            df_row = [portfolio, building, group, sensor_type.split('~')[0], sensor_type.split('~')[1],
                                      sensor_href, sensor_href.split("/")[-1]]
                            columns = ["project", "building", "group", "sensor_type", "sensor_status", "sensor_href",
                                       "asset_id"]
                        df_rows.append(df_row)

    sensor_tree = pd.DataFrame(data=df_rows, columns=columns)
    return sensor_tree




def retrieve_multiple_telemetries(user,
                                  pwd,
                                  id_list,
                                  id_to_name_dictionary=None,
                                  telemetry_list=["TEMPERATURE"],
                                  interval_minutes=5,
                                  from_local_time='2021-12-14T00:00:00',
                                  to_local_time='2021-12-20T23:19:00',
                                  max_days_per_call = 31,
                                  tz_code='Europe/Madrid',
                                  office_hours_only=False,
                                  office_hours_local_begin='08:00',
                                  office_hours_local_end='18:00',
                                  exclude_holidays_country_region=['Country','Region'],
                                  operation='mean',
                                  group_by='asset',
                                  add_day_hour_minute=False):
    '''
    :param user: Metrikus api user
    :param pwd: Metrikus api password
    :param id_list: list of Metrikus unique sensor IDs (at present, a 6-digit integer)
    :param id_to_name_dictionary:if available, dictionary mapping each Metrikus unique id to its friendly name, otherwise use None
    :param telemetry_list: llist of telemetries to be downloaded (key items in the parameter_to_return_value dictionary)
    :param interval_minutes: integer data frequency (in number of minutes)
    :param from_local_time: local time in ISO string in the format '2021-12-14T00:00:00'
    :param to_local_time: local time in ISO string in the format '2021-12-14T00:00:00'
    :param max_days_per_call: maximum number of dates that Metrikus API will return in a single call
    :param tz_code: one of the codes shown in https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    :param office_hours_only: True or False
    :param office_hours_local_begin: ISO string in the format '18:00'
    :param office_hours_local_end: ISO string in the format '18:00'
    :param exclude_holidays_country_region: list of country and (if available) regional holidays to exclude. See list at https://pypi.org/project/holidays/. If left as an empty list,it will NOT exclude holidays.
    :param operation: 'mean','max' or 'min'
    :param group_by: needs to always be 'asset'
    :param add_day_hour_minute: True if we want to append separate columns with this data
    :return: three dataframes: allSensors (all data downloaded), sensors_metrics_list (list of all sensors and metrics retrieved) , sensor_list (list of all sensors for which information was found)
    '''


    from_to_list = split_dates(from_local_time=from_local_time,to_local_time=to_local_time,max_days=max_days_per_call)
    partial_df_list = []
    block_number = 1
    for (start_local_time,end_local_time) in from_to_list:
        #MAIN LOOP
        # transform from local to UTC time
        from_UTC_time = from_local_time_to_utc(datetime.fromisoformat(start_local_time).replace(microsecond=0).isoformat(),
                                               tz_code)
        to_UTC_time = from_local_time_to_utc(datetime.fromisoformat(end_local_time).replace(microsecond=0).isoformat(),
                                             tz_code)

        params = (
            ('asset_source', id_list),
            ('telemetry', telemetry_list),
            ('start', from_UTC_time),
            ('end', to_UTC_time),
            ('interval', str(interval_minutes)),
            ('op', operation),
            ('group_by', group_by),
        )

        response = requests.get('https://app.metrikus.io/api/v1/analytics', auth=(user, pwd), params=params)
        print(f'block {block_number} of {len(from_to_list)}')
        print(response)
        r = json.loads(response.text)['data']

        # text_file = open("response.txt", "w")  # for debugging
        # n = text_file.write(str(r))
        # text_file.close()

        dfList = []
        sensor_list = [id_to_name_dictionary[assetID] if isinstance(id_to_name_dictionary, dict) else str(assetID) for
                       assetID in id_list]
        for telemetry in telemetry_list:
            print(telemetry)
            for asset in r['assets']:
                assetID = asset['asset_id']
                for reading in asset['readings']:
                    measure = reading['telemetry']
                    if parameter_to_return_value[telemetry] == measure:
                        data = reading[operation]
                        df = pd.DataFrame(data=data)
                        df.index = pd.to_datetime(df['from'])
                        df = df[['value']]
                        if isinstance(id_to_name_dictionary, dict):
                            valueColumn = id_to_name_dictionary[str(assetID)] + "_" + measure
                        else:
                            valueColumn = str(assetID) + "_" + measure
                        df.rename(columns={'value': valueColumn}, inplace=True)
                        dfList.append(df)

        if len(dfList) > 0:
            allSensors = pd.concat(dfList, axis=1)
        else:
            allSensors = pd.DataFrame()
        #----------------------------------
        partial_df_list.append(allSensors)
        block_number+=1
    allSensors = pd.concat(partial_df_list,axis=0)


    # cleanup gaps
    allSensors = __fill_dataframe_gaps(allSensors, from_time=from_UTC_time, to_time=to_UTC_time,
                                       interval=str(interval_minutes) + "min")

    # return to local time
    # allSensors.index = allSensors.index.shift(UTC_to_local_offset_minutes,"min")
    allSensors.index = allSensors.index.tz_localize('utc')
    allSensors.index = allSensors.index.tz_convert(tz_code)
    sensors_metrics_list = allSensors.columns

    # add hour minute and weekday
    allSensors['hour'] = allSensors.index.hour
    allSensors['minutes'] = allSensors.index.minute
    allSensors['hour_minutes'] = allSensors['hour'].apply(lambda x: '{0:0>2}'.format(x)) + ":" + allSensors[
        'minutes'].apply(lambda x: '{0:0>2}'.format(x))
    allSensors['weekday'] = allSensors.index.weekday + 1

    # filter by office hours and weekdays
    if office_hours_only:
        allSensors = allSensors[allSensors['weekday'] <= 5].between_time(start_time=office_hours_local_begin,
                                                                         end_time=office_hours_local_end)

    #filter by bank holidays
    if (exclude_holidays_country_region==['Country','Region']) or (exclude_holidays_country_region==[]):
        pass
    else:
        country,region = exclude_holidays_country_region
        hols = holidays.country_holidays(country, subdiv=region)
        allSensors["date"] = allSensors.index.date
        allSensors["holiday"] = allSensors["date"].apply(lambda x: x in hols)
        excluded_holidays = pd.DataFrame(allSensors[allSensors["holiday"]==True]["date"].unique(),columns=['date'])
        excluded_holidays['event']=excluded_holidays['date'].apply(lambda x: hols.get(x))
        print("******************")
        print("Holidays excluded:")
        print(excluded_holidays)
        print("******************")
        allSensors = allSensors[allSensors['holiday']==False]
        allSensors.drop(columns = ["date","holiday"])

    if add_day_hour_minute==False:
        allSensors= allSensors.drop(columns=["weekday","hour","minutes","hour_minutes"])

    return allSensors, sensors_metrics_list, sensor_list
