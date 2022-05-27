import requests
import pandas as pd
from pandas.io.json import json_normalize


class VoSpiegel(object):
    """
    This is python wrapper for the VO Spiegel API. Documentation about the API could be found at https://vospiegel.nl/api
    """
    def __init__(self):
        self.url = 'https://vospiegel.nl/api/'

    def api_key(self, user, password):
        """
        Returns the API key of an user which can be used to call all the other endpoints
        :param user: the username, email is ok
        :param password: passowrd in plain text
        :return: the API key
        """
        response = requests.post(url=f'{self.url}key', data={'user': user, 'password': password})
        if response.status_code > 201:
            raise Exception('No valid username or Password')
        api_key = response.json()['data']['key']
        return api_key

    def inquiries(self, api_key):
        """
        Get all the inquiries bound to a user based on his API Key
        :param api_key: The API key which can be retrieved calling the api_key function
        :return: a pandas dataframe with all the inqueries
        """
        header = {'x-api-key': api_key}
        df = pd.DataFrame()
        skip = 0
        total = 1000
        while skip < total:
            response = requests.get(f'{self.url}inquiry', headers=header, params={'skip': skip}).json()
            total = response['paginator']['itemsTotal']
            skip += response['paginator']['itemsPerPage']
            df_temp = pd.DataFrame(data=response['data'])
            df = pd.concat([df, df_temp])
        return df

    def questions(self, api_key, inquiries: list):
        """
        Get all the questions (without answers) from a list of inquiires
        :param api_key: The API key which can be retrieved calling the api_key function
        :param inquiries: A list with inquiry ID's. Even if you want 1 inquiry, give this ID in a list
        :return: a pandas dataframe with the questions and their information
        """
        header = {'x-api-key': api_key}
        df = pd.DataFrame()
        for i in inquiries:
            response = requests.get(url=f'{self.url}inquiry/questions', headers=header, params={'inquiry': i}).json()
            df_questions = pd.DataFrame()
            # First extract the nested questions from the json. Normally should this work with json-normalize but for unknown reasons will this not work without this loop
            for j in response['data']:
                # Replace carriage returns in the data. They're screwing the final csv file
                if j['info'] is not None:
                    j['info'] = j['info'].replace('\r\n', ' ')
                if j['question']['text'] is not None:
                    j['question']['text'] = j['question']['text'].replace('\r\n', ' ')
                df_questions_temp = json_normalize(data=j['question'])
                # Check now if there are answer_options
                if len(j['question']['options']) > 0:
                    df_options = pd.DataFrame(data=j['question']['options'])
                    df_options['id'] = int(j['question']['id'])
                    df_options.rename(columns={'index': 'option_id', 'text': 'option_text'}, inplace=True)
                    df_options = df_options[['id', 'option_id', 'option_text']]
                    df_questions_temp = pd.merge(df_questions_temp, df_options, how='left', on='id')

                # Add all the questions together to one dataframe
                df_questions_temp.rename(columns={'id': 'reference'}, inplace=True)
                df_questions_temp['reference'] = df_questions_temp['reference'].astype(int)
                del df_questions_temp['options']
                df_questions = pd.concat([df_questions, df_questions_temp])

            # Now get the metadata of the question and join with the question itself
            df_temp = pd.DataFrame(response['data'])
            del df_temp['question']
            df_temp['reference'] = df_temp['reference'].astype(int)
            df_temp = pd.merge(df_temp, df_questions, how='left', on='reference')

            # Concat with previous dataframes and return
            df = pd.concat([df, df_temp])
        df['option_id'] = df['option_id'].astype(pd.Int64Dtype())
        df['scaleId'] = df['scaleId'].astype(pd.Int64Dtype())
        return df

    def results(self, api_key, inquiries: list):
        """
        Get all the results per question and inquiry
        :param api_key: The API key which can be retrieved calling the api_key function
        :param inquiries: A list with inquiry ID's. Even if you want 1 inquiry, give this ID in a list
        :return: a pandas dataframe with the results
        """
        header = {'x-api-key': api_key}
        df = pd.DataFrame()
        for i in inquiries:
            response = requests.get(url=f'{self.url}inquiry/result', headers=header, params={'inquiry': i}).json()
            if len(response['data']) > 0:
                # Loop through all the questions
                for key_1, value_1 in response['data'].items():
                    # Loop through the answers per question and transform all kind of answers (which are all stored in different formats) to one format
                    template = []
                    for key_2, value_2 in value_1.items():
                        if key_2 == 'average':
                            # if an average is given, also the standard deviation is given
                            template.append({'question_id': key_1,
                                             'count': value_1['count'],
                                             'average': value_1['average'],
                                             'stdev': value_1['stdev']})
                        elif key_2 == 'answers':
                            # An anwser is een open text value
                            for answer in value_2:
                                template.append({'question_id': key_1,
                                                 'count': value_1['count-answers'],
                                                 'answer': answer.replace('\r\n', '. '),
                                                 'option_count': 1})
                        elif key_2 == 'choices':
                            # A choice could be a yes or no choice or a choice_id
                            for key_choice, value_choice in value_2.items():
                                if key_choice == 'yes' or key_choice == 'no':
                                    template.append({'question_id': key_1,
                                                     'count': value_1['count'],
                                                     'option_id': key_choice,
                                                     'option_count': value_choice})
                                else:
                                    template.append({'question_id': key_1,
                                                     'count': value_1['count'],
                                                     'option_id': key_choice,
                                                     'option_count': value_choice['count']})
                        elif key_2 == 'ranges':
                            for j in value_2:
                                template.append({'question_id': key_1,
                                                 'count': value_1['count'],
                                                 'option_id': j['title'],
                                                 'option_count': j['count']})
                        elif key_2 in ['inquiry-question', 'values', 'scores', 'count', 'count-answers', 'stdev']:
                            # The kind of answers in the list above, are already processed before or have never a value
                            pass
                        else:
                            # If there is a answer type which is not processed in all the option above. Give an error
                            raise Exception(f'inquiry: {i} with question {key_1} have a non processed answer type {key_2}')

                    df_temp = pd.DataFrame(template)
                    df_temp['inquiry_id'] = i
                    df = pd.concat([df, df_temp])
        df = df[['inquiry_id', 'question_id', 'count', 'average', 'stdev', 'option_id', 'option_count', 'answer']]
        df['option_count'] = df['option_count'].astype(pd.Int64Dtype())
        return df

    def group_response(self, api_key, inquiries: list):
        """
        Get the metadata of a group_response for a list of inquiries
        :param api_key: The API key which can be retrieved calling the api_key function
        :param inquiries: A list with inquiry ID's. Even if you want 1 inquiry, give this ID in a list
        :return: a pandas dataframe with the group response metadata
        """
        header = {'x-api-key': api_key}
        df = pd.DataFrame()
        for i in inquiries:
            response = requests.get(url=f'{self.url}inquiry/group-response', headers=header, params={'inquiry': i}).json()
            df_temp = pd.DataFrame(data=response['data'])
            df = pd.concat([df, df_temp])
        return df

    def labels(self, api_key, inquiries: list):
        """
        get the labels of a list of inquiries
        :param api_key: The API key which can be retrieved calling the api_key function
        :param inquiries: A list with inquiry ID's. Even if you want 1 inquiry, give this ID in a list
        :return: a pandas dataframe with the labels of inquiries
        """
        header = {'x-api-key': api_key}
        df = pd.DataFrame()
        for i in inquiries:
            response = requests.get(url=f'{self.url}inquiry/label', headers=header, params={'inquiry': i}).json()
            df_temp = pd.DataFrame(data=response['data'])
            df = pd.concat([df, df_temp])
        return df

    def groups(self, api_key, inquiries: list):
        """
        get the groups of a list of inquiries
        :param api_key: The API key which can be retrieved calling the api_key function
        :param inquiries: A list with inquiry ID's. Even if you want 1 inquiry, give this ID in a list
        :return: a pandas dataframe with the groups of inquiries
        """
        header = {'x-api-key': api_key}
        df = pd.DataFrame()
        for i in inquiries:
            response = requests.get(url=f'{self.url}group', headers=header, params={'inquiry': i}).json()
            df_temp = pd.DataFrame(data=response['data'])
            df = pd.concat([df, df_temp])
        return df

    def scales(self, api_key):
        """
        get all the available scales in a customer environment
        :param api_key: The API key which can be retrieved calling the api_key function
        :return: a pandas dataframe with the scales in a enironment
        """
        header = {'x-api-key': api_key}
        df = pd.DataFrame()
        skip = 0
        total = 1000
        while skip < total:
            response = requests.get(f'{self.url}scale', headers=header, params={'skip': skip}).json()
            total = response['paginator']['itemsTotal']
            skip += response['paginator']['itemsPerPage']
            df_temp = pd.DataFrame(data=response['data'])
            df = pd.concat([df, df_temp])
        return df