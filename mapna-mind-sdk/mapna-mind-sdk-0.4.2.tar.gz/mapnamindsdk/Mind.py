import json
import datetime
import cherrypy
import pandas as pd
from threading import Thread
from mapnamindsdk import WS as WS
from mapnamindsdk.Rest import Rest as Rest
import mapnamindsdk.Constants as Constants
from mapnamindsdk.Mapper import Mapper as mapper


class Mind(object):

    @staticmethod
    def removeSignal(signalName, userId):

        try:
            body = {"signalName": signalName,
                    "userId": userId
                    }

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/remove', params=body)
            jsonResult = post_req.post()

            if jsonResult.get('messageCode') == '0000':
                return True
            else:
                return False

            return jsonResult

        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None

    @staticmethod
    def createSignal(signalName, signalDescription, unitMeasurment, dataType, parameterSource, userId):

        try:
            body = {"signalName": signalName,
                    "description": signalDescription,
                    "unitMeasurment": unitMeasurment,
                    "dataType": dataType,
                    "ParameterSource": parameterSource,
                    "userId": userId
                    }

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/create', params=body)
            jsonResult = post_req.post();

            if jsonResult['messageCode'] == '0000':
                return True
            else:
                return False

        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None

        # TODO Check Signal duplication with performance signals

    @staticmethod
    def setValue(signalName, value, dateAndTime, userId):

        if dateAndTime.lower() != 'now'.lower():
            Mind._validate(dateAndTime)

        # f = mapper.Mapper.getInstance()

        # signalId = f.SignalMapper[signalName]
        # Request Body
        body = {"signalName": signalName,
                "dateAndTime": dateAndTime,
                "value": value,
                "userId": userId
                }

        # post_req = Rest(f'http://{Constants.SDK_SERVER_IP}:{Constants.SDK_PORT}',
        #                 path='sdk-remote/offline/set', params=body)
        post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                        path='/offline/set', params=body)
        jsonResult = post_req.post()

        if jsonResult['messageCode'] == '0000':
            return True
        else:
            return False

        return jsonResult

    # @staticmethod
    # def getValue(signalNames):
    #     '''
    #     Get value from ONLINE table
    #     :return:
    #     '''
    #     try:
    #
    #         f = mapper.Mapper.getInstance()
    #
    #         # Get signalId for given signalName from the Mapper
    #         signalID = int(f.SignalMapper[signalNames])
    #
    #         # Request Body
    #         body = {'ids': [signalID], 'type': "TIMESERIES"}
    #
    #         post_req = Rest(f'http://{Constants.DATASERVICE_SERVER_IP}:{Constants.DATASERVICE_PORT}',
    #                         path='/online/get', params=body)
    #         listResult = post_req.post()
    #
    #
    #         # Convert Json to List/Dict composition
    #         dictResult = json.loads(jsonResult)[0]
    #
    #         return dictResult
    #     except KeyError as err:
    #         print("ERROR: Signal Name {} not found!\n".format(err))
    #     return None

    @staticmethod
    def _mapHistorian2DataFrame(x, signalNames):
        '''
        Map function for converting each row of the given list (x) to dictionary
        :param x: A single row of list
        :param signalNames: list of signal_names for columns title
        :return: Input list rows in dict format
        '''

        try:
            # Create an empty row
            dictCurrentRow = {}

            # add first column of DataFrame table and its value
            dictCurrentRow.update({'time': x['time']})

            # Create rest of columns using list of signal_names and their values
            valueColumns = {signalNames[i]: x['values'][i] if x['values'][i] != 9876.54321 else None for i in
                            range(0, len(signalNames))}
            # valueColumns = {signalNames[i]: x['values'][i].replace(9876.54321, None) for i in
            #                 range(0, len(signalNames))}

            # Add rest of the columns and values to the current row
            dictCurrentRow.update(valueColumns)

            # Return the row
            return dictCurrentRow

        except:
            print("ERROR MAP:\n")

        return None

    @staticmethod
    def getSignalTags(userId):

        try:
            # body = {"signalName": signalName,
            #         "userId": userId
            #         }

            payload = {'userId': userId}

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/get-tag', params=payload)
            jsonResult = post_req.get();

            if len(jsonResult) == 1:
                if jsonResult[0].get('messageCode') == '0045':
                    return jsonResult.get('message')

            return jsonResult


        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None

    @staticmethod
    def getAlarmTags(userId):

        try:
            # body = {"signalName": signalName,
            #         "userId": userId
            #         }

            payload = {'userId': userId}

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/alarm/get-tag-alarm', params=payload)
            jsonResult = post_req.get();

            if len(jsonResult) == 1 and jsonResult[0].__contains__('messageCode'):
                if jsonResult[0].get('messageCode') == '0045':
                    return jsonResult['message']

            return jsonResult


        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None

    @staticmethod
    def getProfile(user_id):
        jsonResult = {}
        try:
            body = {
                "userId": user_id,
            }
            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}'
                            , path=f'/user/getProfile', params=body,
                            header={'Content-Type': 'application/json; charset=utf-8'})

            jsonResult = post_req.post()
            # print(jsonResult)
            # if len(jsonResult) == 1 and jsonResult.__contains__('status'):
            #     if jsonResult[0].get('messageCode') == '500':
            #         return "user Id is not correct"

        except:
            print("ERROR getProfile")

        return jsonResult

    @staticmethod
    def getPlants(user_id):
        jsonResult = {}
        try:
            body = {
                "userId": user_id,
            }
            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}'
                            , path=f'/user/getPlants', params=body,
                            header={'Content-Type': 'application/json; charset=utf-8'})

            jsonResult = post_req.post()
            # print(jsonResult)

            # if len(jsonResult) == 1 and jsonResult.__contains__('status'):
            #     if jsonResult.get('status') == '500':
            #         return "user Id is not correct"

        except:
            print("ERROR getPlants")
        return jsonResult

    @staticmethod
    def get_kks():
        try:
            post_req = Rest(f'http://{Constants.VIB_SERVICE_IP}:{Constants.VIB_SERVICE_PORT}',
                            path='/getKKS')
            json_result = post_req.get()

            return json_result
        except:
            print("ERROR get_kks")
        return json_result

    @staticmethod
    def _convertJsonToDataFrame(jsonResponse, signalNames):
        """
        Converts given json_response to pandas DataFrame
        :param jsonResponse: Query result in json_response format
        :param signal_names: List of signal names in query to set as columns name of DataFrame
        :return: DataFrame object of json_response
        """
        try:
            # Convert JSON to LIST
            #     listResult = json.loads(jsonResponse)
            #     print(listResult)

            # list_result->dictionary->DataFram

            mylist = map(lambda x: Mind._mapHistorian2DataFrame(x, signalNames), jsonResponse)
            list_1 = list(mylist)
            dataframe = pd.DataFrame(list_1)
            return dataframe

        except:
            print("ERROR convert:\n")
        return None

    @staticmethod
    def _convertJsonToListOfDict(listResult, signalNames, signalIds):
        ii = 0
        totaldict = {}
        for i in listResult:
            dict = i
            mediumlist = dict.get(str(signalIds[ii]))
            listofvaluetimetotal = []
            for l in mediumlist:
                time = l.get('TIME')
                value = l.get('VALUE')
                listofvaluetime = [time, value]
                listofvaluetimetotal.append(listofvaluetime)
            totaldict[signalNames[ii]] = listofvaluetimetotal
            ii = ii + 1

        print(totaldict)
        return totaldict

    @staticmethod
    def _plant_validate(plantName):
        plant_list = {"fars", "paresar", "genaveh"}
        # if plantName is None or not plantName:
        #     raise Exception("INPUT ERROR: plant names can not be null! And  It just can be one of (Fars or Paresar or "
        #                     "Genaveh)")

        if plantName not in plant_list and not (isinstance(plantName, str)):
            raise Exception("INPUT ERROR: plant names is not correct! And  It just can be one of (fars or paresar or "
                            "genaveh)")

    @staticmethod
    def _validate_signalName(signalNames):

        if not (isinstance(signalNames, list) and len(signalNames) < 50):
            raise Exception("Input signalName must be list and its length should be less than 50 signals")
        # try:
        #     # plant = switch_plant(plantName)
        #     # f = mapper.getInstance(plant)
        #     #
        #     # # Get signalId for given signalName from the Mapper
        #     # signalIDs = list(map(lambda x: int(f.SignalMapper[x]), signalNames))
        #     # Get signalId for given signalName from the Mapper
        # except KeyError as err:
        #     print("ERROR: Signal Name {} not found!\n".format(err))

    @staticmethod
    def _validate(start_date, end_text, myinterval):
        try:
            interval = {"SECOND": 7, 'MINUTE': 90, 'DAY': 366}
            start_date = datetime.datetime.strptime(start_date, '%Y/%m/%d-%H:%M:%S')
            end_text = datetime.datetime.strptime(end_text, '%Y/%m/%d-%H:%M:%S')
            delta = end_text - start_date
            if int(delta.days) > interval[myinterval]:
                raise Exception("Your timespan is out of range. In the minute interval that is 90 days and "
                                 "In the second interval that is 7 days")
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY/MM/DD-HH:mm:SS")

    @staticmethod
    def _sec_validate(date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY/MM/DD-HH:mm:SS")

    @staticmethod
    def createAlarm(alarmName, alarmDescription, userId):

        try:
            body = {"alarmName": alarmName,
                    "description": alarmDescription,
                    "userId": userId
                    }

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/alarm/create-alarm', params=body)
            jsonResult = post_req.post()

            if jsonResult.get('messageCode') == '0000':
                return True
            else:
                return False

        # except urllib.error.HTTPError as err:
        #     print("{}\nError Code:{}, URL:{}".format(err, err.code, err.filename))

        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None

    @staticmethod
    def removeAlarm(alarmName, userId):

        try:
            body = {"alarmName": alarmName,
                    "userId": userId
                    }

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/alarm/remove-alarm', params=body)

            jsonResult = post_req.post();

            if jsonResult['messageCode'] == '0000':
                return True
            else:
                return False

            return jsonResult

        except KeyError as err:
            print("ERROR: Signal Name {} not found!\n".format(err))
        return None

    @staticmethod
    def setAlarm(alarm_name, alarm_comment, active_status, user_id):

        if isinstance(alarm_comment, str) and isinstance(active_status, bool) \
                and isinstance(user_id, str) and isinstance(alarm_name, str):
            print("this is ok")
            body = {"alarmName": alarm_name,
                    "alarmComment": alarm_comment,
                    "activeStatus": active_status,
                    "userId": user_id
                    }

            post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                            path='/alarm/set-alarm', params=body)
            json_result = post_req.post()
            return json_result
        else:

            return 'Input Type Is Not Correct. It Must Be (str,str,bool,str)'

    @staticmethod
    def getLastAlarm():

        post_req = Rest(f'http://{Constants.SDK_SERVICE_IP}:{Constants.SDK_SERVICE_PORT}',
                        path='/alarm/get-last-alarm')
        json_result = post_req.get()

        return json_result

    @staticmethod
    def _date_validate(date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y/%m/%d %H:%M:%S')
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY/MM/DD H:M:S")

    @staticmethod
    def _signal_type_validate(input_signal_type):
        signal_type = {'fft', 'ps', 'timebase', 'orbit', 'raw'}
        if (input_signal_type not in signal_type):
            raise Exception('Input signal type is not valid. The signal type was: {}'.format(input_signal_type))

    @staticmethod
    def _signal_name_validate(signalName):
        if isinstance(signalName, str):
            return
        else:
            raise Exception('Input signalName type is not str.')

    @staticmethod
    def _find_signal_input_table(signalName):
        try:
            signal_type_table = {'FFT': 'fft', 'PSM': 'ps', 'PMS': 'ps', 'TIB': 'timebase', 'ORB': 'orbit',
                                 'RAW': 'raw'}
            mylist = []
            mylist = signalName.split("_")
            key = mylist[2]
            return signal_type_table[key]
        except:
            print("ERROR signalName  is not valid:\n")

        return None

    @staticmethod
    def fft_column(x):
        try:
            # date = datetime.datetime.strptime(x['date'], '%M/%D/%Y').strftime('%Y/%M/%D')
            # print(date)
            return {'date': x['date'], 'time': x['time'], 'kks': x['kks'], 'values': x['values'],
                    'unit': x['unit'], 'f_0': x['f_0'], 'df': x['df']}
        except:
            print("ERROR3:\n")

        return None

    @staticmethod
    def raw_column(x):
        try:
            return {'date': x['date'], 'time': x['time'], 'kks': x['kks'], 'data': x['data'],
                    'unit': x['unit'], 'duration': x['duration'], 'dt': x['dt']}
        except:
            print("ERROR3:\n")

        return None

    @staticmethod
    def timebase_column(x):

        try:
            # valueColumn = {'orders': x['orders'], 'xUnfiltered': x['xUnfiltered'], 'yUnfiltered': x['yUnfiltered'],
            #                'xFiltered1': x['xFiltered']['xFiltered1'], 'yFiltered1': x['yFiltered']['yFiltered1'],
            #                'xFiltered2': x['xFiltered']['xFiltered2'], 'yFiltered2': x['yFiltered']['yFiltered2'],
            #                'xFiltered3': x['xFiltered']['xFiltered3'], 'yFiltered3': x['yFiltered']['yFiltered3']}
            valueColumn = {'date': x['date'], 'time': x['time'], 'kks': x['kks'],
                           'unit': x['unit'], 'orders': x['orders'], 'xUnfiltered': x['xunfiltered'],
                           'yUnfiltered': x['yunfiltered'],
                           # 'signalName': x['signalName'],
                           'xFiltered1': [], 'xFiltered2': [], 'xFiltered3': [],
                           'yFiltered1': [], 'yFiltered2': [], 'yFiltered3': []
                           }
            for i in x['orders']:
                i = str(int(i))
                valueColumn['xFiltered' + i] = x['xfiltered']['xFiltered' + i]
                valueColumn['yFiltered' + i] = x['yfiltered']['yFiltered' + i]

            return valueColumn
        except:
            print("ERROR4:\n")

        return None

    @staticmethod
    def orbit_column(x):

        try:
            valueColumn = {'date': x['date'], 'time': x['time'], 'kks': x['kks'],
                           'unit': x['unit'], 'orders': x['orders'], 'unfiltered': x['unfiltered'],
                           'filtered1': [], 'filtered2': [], 'filtered3': []}
            for i in x['orders']:
                i = str(int(i))
                valueColumn['filtered' + i] = x['filtered']['filtered' + i]
            # if (x['unfiltered']):
            #     valueColumn['unfiltered'] = x['unfiltered']
            return valueColumn
        except:
            print("ERROR5:\n")
        return None

    @staticmethod
    def _mapVibHistorian2DataFrame(x, signalType):
        '''
        Map function for converting each row of the given list (x) to dictionary
        :param x: A single row of list
        :param signalType: It can be one of the fft, ps, timebase or orbit
        :return: Input list rows in dict format
        '''

        try:
            dict = {'fft': Mind.fft_column, 'ps': Mind.fft_column, 'raw': Mind.raw_column,
                    'timebase': Mind.timebase_column, 'orbit': Mind.orbit_column}
            # Create an empty row
            dictCurrentRow = {}
            valueColumn = {}
            # add first column of DataFrame table and its value
            # dictCurrentRow.update({'signalName': x['signalName']})
            # dictCurrentRow.update({'time': x['time']})

            valueColumn = dict[signalType](x)
            # valueColumn = x

            # Add rest of the columns and values to the current row
            dictCurrentRow.update(valueColumn)

            # Return the row
            # print(dictCurrentRow)
            return dictCurrentRow

        except:
            print("ERROR2:\n")

        return None

    @staticmethod
    def _convertJsonVibToDataFrame(jsonResponse, signal_type):
        """
        Converts given json_response to pandas DataFrame
        :param jsonResponse: Query result in json_response format
        :return: DataFrame object of json_response
        """
        try:
            mylist = []
            # for item in jsonResponse:
            #     print(item)
            #     mylist.append(Mind.mapVibHistorian2DataFrame(item, signalName))
            #     print(mylist)
            mylist = map(lambda x: Mind._mapVibHistorian2DataFrame(x, signal_type), jsonResponse)
            # mylist = jsonResponse['values']

            list_1 = list(mylist)
            dataframe = pd.DataFrame(list_1)
            return dataframe

        except:
            print("ERROR1:\n")
        return None
