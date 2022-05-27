import pandas
import requests
import math
from googleapiclient.errors import HttpError
from datacorral import definitions
from datacorral import analytics_service_object

class Analytics:

    def __init__(self, token_file_name):
        self.ga_sites_dict = definitions.SITES
        self.token_file_name = token_file_name

        print('Initializing API helper')


    #This will be atomic data extract
    def api_call(self, site_id, start_date, end_date, metrics_string, dimensions_string, filters_string=None, sort_string=None, index=1, max_results=10000):
        '''DESCRIPTION
        '''

        # Try to make a request to the API or handle errors.
        try:
            service = analytics_service_object.initialize_service(self.token_file_name)
            response = service.data().ga().get(
                            ids=site_id
                            ,start_date=start_date
                            ,end_date=end_date
                            ,start_index=index
                            ,max_results=max_results
                            ,metrics=metrics_string
                            ,dimensions=dimensions_string
                            ,filters=filters_string
                            ,sort=sort_string
                            ,samplingLevel='HIGHER_PRECISION'
                        ).execute()
            return response

        except TypeError as error:
            print('   ERROR, in constructing your query : %s' % error)
            raise Exception
        except HttpError as error:
            print('   API ERROR: %s: %s' % (error.resp.status, error._get_reason()))
            raise Exception
        #except AccessTokenRefreshError:
        #    print('   ERROR, The credentials have been revoked or expired')
        #    raise Exception
        except Exception:
            print("   ERROR:", sys.exc_info()[0])
            raise Exception




    def get_data(self, site_list, start_date, end_date, metrics_string, dimensions_string, filters_string=None, sort_string=None, output_format='DataFrame', index=1, max_results=10000, allow_sampled_data = 0):
        '''DESCRIPTION
        '''

        #Initialize empty dataframe for api iteration call
        if output_format == 'DataFrame':
                data = pandas.DataFrame()

        for site in site_list:
            site_id = 'ga:' + str(self.ga_sites_dict[site])
            print('Site:', site)
            index = 1
            response = self.api_call(
                site_id = site_id
                , start_date = start_date
                , end_date = end_date
                , metrics_string = metrics_string
                , dimensions_string = dimensions_string
                , filters_string = filters_string
                , sort_string = sort_string
                , index = index
                , max_results = max_results
            )

            print('\tContains sampled data:', response['containsSampledData'])
            if response['containsSampledData']==True:
                if allow_sampled_data == 0:
                    print('\tExclude Sampled Data enabled. Skipping', site)
                    continue
                print('\tWARNING, contains sampled data')

            print('\tLink:', response['selfLink'])
            divisons = math.ceil(response['totalResults']/response['itemsPerPage'])
            print('\tTotal Results', response['totalResults'], '\n\tItems Per Page', response['itemsPerPage'],'\n\tNumber of divisions', divisons)
            headers = [ i['name'] for i in response['columnHeaders'] ]

            if response['totalResults'] > 0:
                data_contents = response['rows']
                index = index + max_results
                for i in range(divisons-1):
                    print('\tAppending next division', index)
                    r = self.api_call(
                        site_id = site_id
                        , start_date = start_date
                        , end_date = end_date
                        , metrics_string = metrics_string
                        , dimensions_string = dimensions_string
                        , filters_string = filters_string
                        , sort_string = sort_string
                        , index = index
                        , max_results = max_results
                    )
                    data_contents = data_contents + r['rows']
                    index = index + max_results

                #print('Completed Data Extract')
                print('\tCompleted Data Extract', len(data_contents), 'rows imported')

                #Consider appending site on json side rather than dataframe for improved efficiency
                if output_format == 'DataFrame':
                    df = pandas.DataFrame(data_contents, columns=headers)
                    df['Site'] = site
                    data = data.append(df)
            else:
                print('No Data')
                pass

        return(data)




    def transform_type(self, dataframe):
        df = dataframe.copy()
        for column in df.columns:
            if str.upper(column) == str.upper('ga:date'):
                df[column] = df[column].apply(lambda x: pandas.to_datetime(str(x), format='%Y-%m-%d'))
            if str.upper(column) == str.upper('Date'):
                df[column] = df[column].apply(lambda x: pandas.to_datetime(str(x), format='%Y-%m-%d'))
            if str.upper(column) == str.upper('DateLY'):
                df[column] = df[column].apply(lambda x: pandas.to_datetime(str(x), format='%Y-%m-%d'))


            if str.upper(column) == str.upper('ga:sessions'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:impressions'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:adCLicks'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:transactions'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:year'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:month'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:week'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:itemQuantity'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:uniquePurchases'):
                df[column] = df[column].astype(int)
            if str.upper(column) == str.upper('ga:users'):
                df[column] = df[column].astype(int)

            if str.upper(column) == str.upper('ga:transactionsPerSession'):
                df[column] = df[column].astype(float)
            if str.upper(column) == str.upper('ga:revenuePerTransaction'):
                df[column] = df[column].astype(float)
            if str.upper(column) == ('ga:revenuePerItem'):
                df[column] = df[column].astype(float)
            if str.upper(column) == str.upper('ga:adCost'):
                df[column] = df[column].astype(float)
            if str.upper(column) == str.upper('ga:CPC'):
                df[column] = df[column].astype(float)
            if str.upper(column) == str.upper('ga:ROAS'):
                df[column] = df[column].astype(float)
            if str.upper(column) == str.upper('ga:itemRevenue'):
                df[column] = df[column].astype(float)
            if str.upper(column) == str.upper('ga:transactionRevenue'):
                df[column] = df[column].astype(float)
            if str.upper(column) == str.upper('ga:adClicks'):
                df[column] = df[column].astype(float)

        return df
        #pandas.to_datetime(str(row['ga:date']), format='%Y%m%d')
